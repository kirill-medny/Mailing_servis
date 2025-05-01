from django.urls import path
from mailing.views import (
    home,
    MessageListView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
)

app_name = 'mailing'

urlpatterns = [
    path('', home, name='home'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
]