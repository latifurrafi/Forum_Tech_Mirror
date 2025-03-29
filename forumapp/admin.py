from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Tag, Category, Post, Comment, Vote, Report, Bookmark, Discussion
)

# Inline model for displaying UserProfile in the User admin page
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profiles"

# Extend UserAdmin to include UserProfile
class UserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

# Register User with the updated UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_score', 'created_at', )
    search_fields = ('user__username', 'user__email')
    list_filter = ('activity_score',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'views')
    search_fields = ('title', 'author__username')
    list_filter = ('category', 'created_at')
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    search_fields = ('post__title', 'user__username')
    list_filter = ('created_at',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value')
    search_fields = ('user__username', 'post__title')
    list_filter = ('value',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'post', 'comment', 'reason', 'reviewed', 'created_at')
    search_fields = ('reporter__username', 'post__title', 'comment__text')
    list_filter = ('reason', 'reviewed', 'created_at')
    ordering = ('-created_at',)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')
    list_filter = ('created_at',)

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'upvotes', 'views', 'comments_count')
    search_fields = ('title', 'tags')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Customize admin site appearance
admin.site.site_header = "Forum Admin Panel"
admin.site.site_title = "Forum Admin"
admin.site.index_title = "Welcome to the Forum Admin Panel"

