from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models.signals import post_save, post_delete

def validate_image_format(value):
    if not value.name.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise ValidationError('Only .jpg, .jpeg, and .png formats are supported.')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to='avatars/', validators=[validate_image_format], default='avatars/default.jpg')
    bio = models.TextField(blank=True, null=True)
    activity_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @staticmethod
    def get_or_create_profile(user):
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.get_or_create_profile(instance)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    views = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
        
@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def update_comment_count(sender, instance, **kwargs):
    post = instance.post
    post.comments_count = post.comments.count()
    post.save()


class Vote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1

    VOTE_CHOICES = [
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'post')  # Prevents duplicate votes

    def __str__(self):
        return f"Vote by {self.user.username} on {self.post.title}"

    @staticmethod
    def update_vote(user, post, value):
        vote, created = Vote.objects.update_or_create(
            user=user, post=post, defaults={'value': value}
        )
        return vote

        
# Report Model
class Report(models.Model):
    REPORT_REASONS = [
        ("spam", "Spam"),
        ("harassment", "Harassment"),
        ("hate_speech", "Hate Speech"),
        ("false_info", "False Information"),
        ("other", "Other"),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)  # User who reports
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    reason = models.CharField(max_length=50, choices=REPORT_REASONS)
    details = models.TextField(blank=True, null=True)  # Additional details
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)  # Indicates if the report has been reviewed

    def __str__(self):
        if self.post:
            return f"Report on Post: {self.post.title} by {self.reporter.username}"
        elif self.comment:
            return f"Report on Comment by {self.comment.user.username} by {self.reporter.username}"
        return "Invalid Report"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Ensure a user can bookmark a post only once

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"

class Discussion(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    upvotes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
