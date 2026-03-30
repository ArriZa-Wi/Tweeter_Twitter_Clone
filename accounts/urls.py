
from django.urls import path
from .views import SignUpView, ProfileDetailView, ProfileUpdateView, PublicProfileView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path('profile/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('public_profile/<int:pk>/', PublicProfileView.as_view(), name='public_profile'),
]