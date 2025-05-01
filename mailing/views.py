from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from mailing.models import Message, Client, Mailing
from django.contrib import messages


@login_required
def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status='running').count()
    unique_clients = Client.objects.values('email').distinct().count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
    }
    return render(request, 'mailing/home.html', context)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body']
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка создания сообщения. Проверьте введенные данные.')
        return super().form_invalid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body']
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно обновлено.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка обновления сообщения. Проверьте введенные данные.')
        return super().form_invalid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Сообщение успешно удалено.')
        return super().delete(request, *args, **kwargs)