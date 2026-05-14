
import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Twit
from .forms import CommentForm


def _htmx_trigger(response, events):
    """Attach an HX-Trigger header to a response. `events` is a dict."""
    response["HX-Trigger"] = json.dumps(events)
    return response


class HomePageView(LoginRequiredMixin, TemplateView):
    """Home page view"""
    template_name = "home.html"


class TwitListView(LoginRequiredMixin, ListView):
    """Twit List View"""
    model = Twit
    template_name = "twit_list.html"
    ordering = ["-created"]


class TwitDetailView(LoginRequiredMixin, View):
    """Twit Detail View — dispatches to GET/POST sub-views."""

    def get(self, request, *args, **kwargs):
        view = CommentGetView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPostView.as_view()
        return view(request, *args, **kwargs)


class CommentGetView(LoginRequiredMixin, DetailView):
    """Twit Detail View"""

    model = Twit
    template_name = "twit_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.all()
        return context


class CommentPostView(SingleObjectMixin, FormView):
    """Comment Post View"""
    model = Twit
    form_class = CommentForm
    template_name = "twit_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.twit = self.object
        comment.author = self.request.user
        comment.save()

        if getattr(self.request, "htmx", False):
            html = render_to_string(
                "partials/_comment.html",
                {"comment": comment, "user": self.request.user},
                request=self.request,
            )
            response = HttpResponse(html)
            return _htmx_trigger(response, {"comment:created": {"twit_id": self.object.id}})

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("twit_detail", kwargs={"pk": self.object.pk})


class TwitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Twit Update View"""
    model = Twit
    template_name = "twit_update.html"
    fields = ("body", "image_url")

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def form_valid(self, form):
        self.object = form.save()
        if getattr(self.request, "htmx", False):
            html = render_to_string(
                "partials/_twit_card.html",
                {"twit": self.object, "user": self.request.user},
                request=self.request,
            )
            response = HttpResponse(html)
            return _htmx_trigger(response, {"twit:updated": {"twit_id": self.object.id}})
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("twit_list")


class TwitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Twit Delete View"""
    model = Twit
    template_name = "twit_delete.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def form_valid(self, form):
        twit_id = self.object.id
        self.object.delete()
        if getattr(self.request, "htmx", False):
            response = HttpResponse("")
            return _htmx_trigger(response, {"twit:deleted": {"twit_id": twit_id}})
        return super().form_valid(form)

    # htmx sends HTTP DELETE; route it through the same form_valid path as POST.
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.form_valid(self.get_form())

    def get_success_url(self):
        return reverse_lazy("twit_list")


class TwitCreateView(LoginRequiredMixin, CreateView):
    """Twit Create View"""
    model = Twit
    template_name = "twit_create.html"
    fields = ("body", "image_url")

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()

        if getattr(self.request, "htmx", False):
            html = render_to_string(
                "partials/_twit_card.html",
                {"twit": self.object, "user": self.request.user},
                request=self.request,
            )
            response = HttpResponse(html)
            return _htmx_trigger(response, {"twit:created": {"twit_id": self.object.id}})

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("twit_list")


class TwitLikeView(LoginRequiredMixin, View):
    """Like/unlike a twit. Returns an HX-Trigger with the new state."""

    def get(self, request, *args, **kwargs):
        twit_id = kwargs.get("pk") or request.GET.get("twit_id")
        twit_action = request.GET.get("twit_action", "like")

        twit = Twit.objects.get(id=twit_id)

        if twit_action == "like":
            twit.likes.add(request.user)
            liked = True
        else:
            twit.likes.remove(request.user)
            liked = False

        response = HttpResponse("")
        return _htmx_trigger(response, {
            "twit:liked": {
                "twit_id": twit.id,
                "liked": liked,
                "count": twit.likes.count(),
            }
        })
