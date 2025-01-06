from .serializers import GetChatsSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from .serializers import ChatSerializer
from rest_framework.exceptions import NotFound
from accounts.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, Role
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
class CreateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        chat_type = data.get('chat_type')  # نوع چت (direct, group, channel)
        user1 = request.user  # کاربر اول از توکن احراز هویت گرفته می‌شود
        user2_username = data.get('user2')  # یوزرنیم کاربر دوم (برای چت direct)

        # بررسی وجود کاربر دوم
        try:
            user2 = User.objects.get(username=user2_username)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # بررسی وجود تصویر گروه
        group_image = None
        if chat_type == 'group' or chat_type == 'channel':
            group_image = request.FILES.get('group_image')  # دریافت تصویر گروه از درخواست

            if not group_image and chat_type in ['group', 'channel']:
                return Response({"error": "Group image is required."}, status=status.HTTP_400_BAD_REQUEST)

        # ساخت چت
        if chat_type == 'direct':
            # ایجاد چت برای دو نفر
            chat = Chat.objects.create(chat_type='direct')
            chat.participants.add(user1, user2)  # اضافه کردن دو کاربر به چت
            chat.group_admin.set([user1])  # کاربر اول به عنوان ادمین
            chat.save()

            # نقش‌ها را برای هر دو نفر تعیین می‌کنیم
            Role.objects.create(user=user1, chat=chat, role='admin')
            Role.objects.create(user=user2, chat=chat, role='admin')

        elif chat_type == 'group':
            # ایجاد چت گروهی
            group_name = data.get('group_name')
            max_participants = data.get('max_participants', 50)  # حداکثر تعداد اعضا

            if not group_name:
                return Response({"error": "Group name is required."}, status=status.HTTP_400_BAD_REQUEST)

            chat = Chat.objects.create(chat_type='group', group_name=group_name, max_participants=max_participants)
            chat.participants.add(user1, user2)  # اضافه کردن دو کاربر به چت
            chat.group_admin.set([user1])  # کاربر اول به عنوان ادمین

            # ذخیره تصویر گروه
            if group_image:
                chat.group_image = group_image  # ذخیره تصویر گروه

            chat.save()

            # نقش‌ها را برای اعضای گروه تنظیم می‌کنیم
            Role.objects.create(user=user1, chat=chat, role='admin')
            Role.objects.create(user=user2, chat=chat, role='member')

        elif chat_type == 'channel':
            # ایجاد چت کانال
            group_name = data.get('group_name')

            if not group_name:
                return Response({"error": "Channel name is required."}, status=status.HTTP_400_BAD_REQUEST)

            chat = Chat.objects.create(chat_type='channel', group_name=group_name)
            chat.participants.add(user1, user2)  # اضافه کردن دو کاربر به چت
            chat.group_admin.set([user1])  # کاربر اول به عنوان ادمین

            # ذخیره تصویر گروه (برای کانال نیز)
            if group_image:
                chat.group_image = group_image  # ذخیره تصویر گروه

            chat.save()

            # نقش‌ها را برای کانال تنظیم می‌کنیم
            Role.objects.create(user=user1, chat=chat, role='admin')
            Role.objects.create(user=user2, chat=chat, role='viewer')

        else:
            return Response({"error": "Invalid chat type."}, status=status.HTTP_400_BAD_REQUEST)

        # بازگرداندن اطلاعات چت جدید به همراه جزئیات آن
        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class UpdateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, chat_id):
        """
        این ویو برای تغییر نام کانال یا گروه و یا عکس کانال استفاده می‌شود.
        """
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه آیا کاربر ادمین این چت است
        if request.user not in chat.group_admin.all():
            return Response({"error": "You are not the admin of this chat."}, status=status.HTTP_403_FORBIDDEN)

        # تغییرات مجاز
        group_name = request.data.get('group_name')
        group_image = request.data.get('group_image')  # فرض می‌کنیم که عکس کانال به صورت فایل ارسال می‌شود

        if group_name:
            chat.group_name = group_name

        if 'group_image' in request.FILES:
            chat.group_image = request.FILES['group_image']  # دریافت و ذخیره عکس گروه

        chat.save()

        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_200_OK)



class DeleteChatView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, chat_id):
        """
        این ویو برای حذف کانال یا گروه استفاده می‌شود.
        """
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه آیا کاربر ادمین این چت است
        if request.user not in chat.group_admin.all():
            return Response({"error": "You are not the admin of this chat."}, status=status.HTTP_403_FORBIDDEN)

        # حذف چت
        chat.delete()

        return Response({"message": "Chat deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class AddUserToChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        """
        این ویو برای اضافه کردن چندین کاربر به گروه یا کانال استفاده می‌شود.
        """
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه آیا کاربر ادمین این چت است
        if request.user not in chat.group_admin.all():
            return Response({"error": "You are not the admin of this chat."}, status=status.HTTP_403_FORBIDDEN)

        # دریافت یوزرنیم‌های کاربران که می‌خواهیم به چت اضافه کنیم
        usernames = request.data.get('usernames')
        if not usernames or not isinstance(usernames, list):
            return Response({"error": "Usernames must be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)

        # اضافه کردن کاربران به چت
        new_users = []
        already_in_chat = []

        for username in usernames:
            try:
                new_user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": f"User {username} not found."}, status=status.HTTP_400_BAD_REQUEST)

            # بررسی اینکه آیا کاربر قبلاً عضو چت است یا نه
            if new_user in chat.participants.all():
                already_in_chat.append(username)
                continue  # کاربر از قبل عضو است

            chat.participants.add(new_user)
            new_users.append(new_user)

        chat.save()

        # پیام نهایی
        message = f"Users {', '.join([user.username for user in new_users])} added successfully."
        if already_in_chat:
            message += f" Users {', '.join(already_in_chat)} were already in the chat."

        return Response({"message": message}, status=status.HTTP_200_OK)



class RemoveUserFromChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        """
        این ویو برای اخراج چندین کاربر از گروه یا کانال استفاده می‌شود.
        """
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه آیا کاربر ادمین این چت است
        if request.user not in chat.group_admin.all():
            return Response({"error": "You are not the admin of this chat."}, status=status.HTTP_403_FORBIDDEN)

        # دریافت یوزرنیم‌های کاربران که می‌خواهیم از چت اخراج کنیم
        usernames = request.data.get('usernames')
        if not usernames or not isinstance(usernames, list):
            return Response({"error": "Usernames must be provided as a list."}, status=status.HTTP_400_BAD_REQUEST)

        removed_users = []
        not_found_users = []
        not_in_chat_users = []

        for username in usernames:
            try:
                remove_user = User.objects.get(username=username)
            except User.DoesNotExist:
                not_found_users.append(username)
                continue

            # بررسی اینکه آیا کاربر عضو چت است
            if remove_user not in chat.participants.all():
                not_in_chat_users.append(username)
                continue

            chat.participants.remove(remove_user)
            removed_users.append(remove_user)

        chat.save()

        # بررسی پیام‌های خطا
        error_messages = []
        if not_found_users:
            error_messages.append(f"User(s) {', '.join(not_found_users)} not found.")
        if not_in_chat_users:
            error_messages.append(f"User(s) {', '.join(not_in_chat_users)} are not in the chat.")

        if error_messages:
            return Response({"error": " | ".join(error_messages)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": f"User(s) {', '.join([user.username for user in removed_users])} removed successfully."},
            status=status.HTTP_200_OK
        )

class LeaveChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        """
        این ویو برای خروج کاربر از گروه یا کانال استفاده می‌شود.
        """
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی اینکه آیا کاربر عضو چت است
        if request.user not in chat.participants.all():
            return Response({"error": "You are not a participant in this chat."}, status=status.HTTP_403_FORBIDDEN)

        # حذف کاربر از چت
        chat.participants.remove(request.user)
        chat.save()

        return Response({"message": "You have successfully left the chat."}, status=status.HTTP_200_OK)




class GetUserChatsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  # اضافه کردن احراز هویت JWT

    def get(self, request, *args, **kwargs):
        user = request.user  # کاربر احراز هویت شده از طریق توکن JWT
        chats = Chat.objects.filter(participants=user)

        # استفاده از سریالایزر برای چت‌ها
        serializer = GetChatsSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchChatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('search', '')  # جستجو بر اساس نام چت
        chats = Chat.objects.filter(group_name__icontains=query, participants=request.user)

        serializer = GetChatsSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_chat_participants(request, chat_id):
    # ابتدا بررسی می‌کنیم که آیا کاربر درخواست را فرستاده در چت حضور دارد یا نه
    user = request.user
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        raise NotFound('Chat not found')

    # بررسی اینکه آیا کاربر در لیست شرکت‌کنندگان چت وجود دارد
    if user not in chat.participants.all():
        raise PermissionDenied('You are not authorized to view this chat')

    # مقداردهی سریالایزر با ارسال context برای دسترسی به request
    serializer = ChatSerializer(chat, context={'request': request})
    return Response(serializer.data)
