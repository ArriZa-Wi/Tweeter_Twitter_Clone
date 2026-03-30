
from django.conf import settings
from django.db import models
from django.urls import reverse

class Twit(models.Model):
    """Model for twit posts"""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='twits')
    body = models.TextField()
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_twits",
        blank=True,
    )

    def __str__(self):
        """String representation of the twit"""
        return f"Twit by {self.author.username}"
    
    def get_absolute_url(self):
        """Get the URL for the twit detail page"""
        return reverse("twit_detail", kwargs={"pk": self.pk})
    
    def get_like_url(self):
        """Get the URL for liking a twit based on the twit's pk"""
        return reverse("twit_like", kwargs={"pk": self.pk})
    
class Comment(models.Model):
    """Model for comment posts"""
    twit = models.ForeignKey(Twit, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.CharField(max_length=140)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of the comment"""
        return f"Comment by {self.author.username} on Twit {self.twit.id}"

    def get_absolute_url(self):
        """Get the URL for the twit list page"""
        return reverse("twit_list")