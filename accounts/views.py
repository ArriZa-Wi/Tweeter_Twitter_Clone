
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from .models import CustomUser
from .forms import CustomUserChangeForm

from .forms import CustomUserCreationForm

class SignUpView(CreateView):
    """Sign Up View"""

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

class PublicProfileView(DetailView):
    """Public Profile View"""
    model = CustomUser
    template_name = 'public_profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        """Get the context data for the template"""
        context = super().get_context_data(**kwargs)
        context['twits'] = self.object.twits.all().order_by('-created')
        return context

class ProfileDetailView(LoginRequiredMixin, DetailView):
    """Profile Detail View"""
    model = CustomUser
    template_name = 'profile_detail.html'

    def get_object(self):
        """Get the current user object"""
        return self.request.user

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Profile Update View"""
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile_update.html'
    success_url = reverse_lazy('profile_detail')

    def get_object(self):
        """Get the current user object"""
        return self.request.user