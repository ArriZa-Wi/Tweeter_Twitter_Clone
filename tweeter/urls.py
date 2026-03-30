
from django.urls import path
from .views import HomePageView, TwitListView, TwitDetailView, TwitCreateView, TwitUpdateView, TwitDeleteView, TwitLikeView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("twits/", TwitListView.as_view(), name="twit_list"),
    path("twits/<int:pk>/", TwitDetailView.as_view(), name="twit_detail"),
    path("twits/new/", TwitCreateView.as_view(), name="twit_create"),
    path("twits/<int:pk>/edit/", TwitUpdateView.as_view(), name="twit_update"),
    path("twits/<int:pk>/delete/", TwitDeleteView.as_view(), name="twit_delete"),
    path("twits/<int:pk>/like/", TwitLikeView.as_view(), name="twit_like"),
]