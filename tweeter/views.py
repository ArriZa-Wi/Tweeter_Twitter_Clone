
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse

from .models import Twit
from .forms import CommentForm

class HomePageView(LoginRequiredMixin, TemplateView):
    """Home page view"""
    template_name = "home.html"

class TwitListView(LoginRequiredMixin, ListView):
    """Twit List View"""
    model = Twit
    template_name = "twit_list.html"

class TwitDetailView(LoginRequiredMixin, View):
    """Twit Detail View New"""

    def get(self, request, *args, **kwargs):
        """Handles GET requests"""
        view = CommentGetView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handles POST requests"""
        view = CommentPostView.as_view()
        return view(request, *args, **kwargs)
 
class CommentGetView(LoginRequiredMixin, DetailView):
    """Twit Detail View"""

    model = Twit
    template_name = "twit_detail.html"

    def get_context_data(self, **kwargs):
        """Get the context data for the template"""
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.all()
        return context
    
class CommentPostView(SingleObjectMixin, FormView):
    """Commwent Post View"""
    model = Twit
    form_class = CommentForm
    template_name = "twit_detail.html"

    def post(self, request, *args, **kwargs):
        # Get the twit object that is currently associated with the pk in the URL
        self.object = self.get_object()
        # Do work that the parent would have already
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Create new comment when form is valid. self refers to current pk and form is CommentForm"""    
        # Get the comment instance by saving the form, but set commit to False
        # as we don't want the form to actually fully save the model to the db yet
        comment = form.save(commit=False)
        # Attach the twit to the new comment.
        comment.twit = self.object
        # Attach the author to the new comment.
        comment.author = self.request.user
        # Save the comment to the db
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Get the success url"""
        twit = self.get_object()
        return reverse("twit_detail", kwargs={"pk": twit.pk})

class TwitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Twit Update View"""
    model = Twit
    template_name = "twit_update.html"
    fields = (
        "body",  # The text content of the twit
        "image_url",  # Optional image URL for the twit
    )

    def test_func(self):
        """Check if the user is the author of the twit"""
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self):
        # Redirect to the list of twits after successful update
        return reverse_lazy('twit_list')
    
class TwitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Twit Delete View"""
    model = Twit
    template_name = "twit_delete.html"

    def test_func(self):
        """Check if the user is the author of the twit"""
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self):
        # Redirect to the list of twits after successful deletion
        return reverse_lazy('twit_list')

class TwitCreateView(LoginRequiredMixin, CreateView):
    """Twit Create View"""
    model = Twit
    template_name = "twit_create.html"
    fields = (
        "body",  # The text content of the twit
        "image_url",  # Optional image URL for the twit
    )

    def form_valid(self, form):
        # Set the author of the twit to the current logged-in user
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the list of twits after successful creation
        return reverse_lazy('twit_list')
    
class TwitLikeView(LoginRequiredMixin, View):
    """Twit Like View"""

    def get(self, request, *args, **kwargs):
        """GET Request"""
        # Get data from the GET request sent via AJAX
        twit_id = request.GET.get("twit_id", None)
        twit_action = request.GET.get("twit_action", None)

        print(twit_id)
        print(twit_action)

        # Fetch the twit from the database
        twit = Twit.objects.get(id=twit_id)

        if twit_action == "like":
            # Add the user to the likes
            twit.likes.add(request.user)
        else:
            # Remove the user from the likes
            twit.likes.remove(request.user)

        # Return a JSON response indicating success
        return JsonResponse({
            "success": True,
        })
