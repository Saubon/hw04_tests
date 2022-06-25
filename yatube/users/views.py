from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserCreationForm


class SignUp(CreateView):
    form_class = UserCreationForm
    template_name = 'auth/signup.html'
    success_url = reverse_lazy('posts:index')
    success_message = "Вы успешно зарегистрированы!"
