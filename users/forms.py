from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from users.models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class UserProfileEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "avatar",
            "phone_number",
            "country",
        )

        # Исключите поле для ввода пароля
        exclude = ("password",)
