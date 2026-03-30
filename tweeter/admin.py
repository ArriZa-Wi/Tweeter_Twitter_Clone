
from django.contrib import admin
 
from .models import Twit, Comment
 
class CommentInline(admin.TabularInline):
     """Inline for seeing comments related to twits"""
     model = Comment
 
 
class TwitAdmin(admin.ModelAdmin):
    """Custom twit admin"""
    inlines = [
        CommentInline,
    ]
 
admin.site.register(Twit, TwitAdmin)
admin.site.register(Comment)