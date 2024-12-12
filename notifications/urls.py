from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/mark-as-read/', views.NotificationMarkAsReadView.as_view(), name='notification-mark-as-read'),
    path('<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification-delete'),
    path('settings/', views.NotificationSettingsView.as_view(), name='notification-settings'),
]