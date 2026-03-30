
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "date_of_birth", "email", "password1", "password2")

class CustomUserChangeForm(UserChangeForm):
    """Custom user change form"""
    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "date_of_birth", "email",)
