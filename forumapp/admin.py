from django.contrib import admin
from .models import UserProfile, Category, Post, Comment, Vote, Report, Bookmark

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_score")
    search_fields = ("user__username", "bio")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "created_at")
    search_fields = ("title", "author__username", "content")
    list_filter = ("category", "created_at")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username", "post__title", "text")
    list_filter = ("created_at",)

class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "value")
    search_fields = ("user__username", "post__title")

class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "get_reported_item", "reason", "created_at", "reviewed")
    list_filter = ("reason", "reviewed", "created_at")
    search_fields = ("reporter__username", "post__title", "comment__text", "reason")

    def get_reported_item(self, obj):
        if obj.post:
            return f"Post: {obj.post.title}"
        elif obj.comment:
            return f"Comment: {obj.comment.text[:50]}..."  # Show first 50 characters
        return "N/A"
    
    get_reported_item.short_description = "Reported Item"

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Report, ReportAdmin)
# admin.site.register(Bookmark, BookmarkAdmin)