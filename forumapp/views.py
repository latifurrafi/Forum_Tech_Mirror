from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from .models import *
from .forms import *
import logging
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils.timezone import timedelta, now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TrendingTopicSerializer



def homepage(request):
    posts = Post.objects.annotate(
        upvotes=Count('votes', filter=Q(votes__value=1)),
        downvotes=Count('votes', filter=Q(votes__value=-1))
    ).select_related('author', 'category').prefetch_related('comments')

    categories = Category.objects.annotate(post_count=Count('post')).order_by('-post_count')

    user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True)

    user = request.user
    post_count = Post.objects.filter(author=user).count()
    comment_count = Comment.objects.filter(user=user).count()
    upvotes_received = Vote.objects.filter(post__author=user, value=Vote.UPVOTE).count()

    tags = Post.objects.values_list('tags', flat=True)
    unique_tags = set(tag for tag_list in tags for tag in tag_list.split(','))

    return render(request, 'dashboard.html', {
        'posts': posts,
        'categories': categories,
        'tags': unique_tags,
        'post_count': post_count,
        'comment_count': comment_count,
        'upvotes_received': upvotes_received,
        'user_bookmarks': user_bookmarks,
    })

def post_detail(request, post_id):
    # Fetch post with related author, profile, category and aggregated vote counts
    post = get_object_or_404(
        Post.objects.select_related('author__profile', 'category')
        .prefetch_related('comments__user')
        .annotate(
            upvotes=Count('votes', filter=Q(votes__value=1)),
            downvotes=Count('votes', filter=Q(votes__value=-1))
        ),
        id=post_id
    )
    is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()
    
    # Fetch comments related to the post (already prefetched for efficiency)
    
    comments = post.comments.all()

    return render(request, 'post-detail.html', {
        'post': post,
        'upvotes': post.upvotes,
        'downvotes': post.downvotes,
        'comments': comments,
        'is_bookmarked': is_bookmarked,
    })

@login_required
@require_POST
def vote_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    try:
        vote_value = int(request.POST.get('value'))
    except (TypeError, ValueError):
        messages.error(request, "Invalid vote value.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('post-detail', args=[post.id])))

    if vote_value not in [Vote.UPVOTE, Vote.DOWNVOTE]:
        messages.error(request, "Invalid vote value.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('post-detail', args=[post.id])))

    vote, created = Vote.objects.get_or_create(
        user=request.user, post=post,
        defaults={'value': vote_value}
    )

    if not created:
        if vote.value == vote_value:
            vote.delete()
            messages.success(request, "Your vote has been removed.")
        else:
            vote.value = vote_value
            vote.save()
            messages.success(request, "Your vote has been updated.")
    else:
        messages.success(request, "Your vote has been added.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('post-detail', args=[post.id])))

@login_required
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

        if not created:
            bookmark.delete()
            return JsonResponse({'bookmarked': False, 'message': 'Bookmark removed'})
        
        return JsonResponse({'bookmarked': True, 'message': 'Post bookmarked'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

logger = logging.getLogger(__name__)

@login_required
def createPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST)  # Use Django's form handling
        if form.is_valid():
            post = form.save(commit=False)  # Save but don’t commit yet
            post.author = request.user  # Assign the logged-in user
            post.save()
            form.save_m2m()  # Save many-to-many relationships if needed
            logger.info("✅ Post saved successfully!")
            return redirect('homepage')
        else:
            logger.warning(f"❌ Form Errors: {form.errors}")

    else:
        form = PostForm()

    categories = Category.objects.all()
    return render(request, 'create-post.html', {'form': form, 'categories': categories})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment_text = request.POST.get('text')

    if not comment_text.strip():
        messages.error(request, "Comment Cannot be Empty.")
        return redirect('post-detail', post_id = post.id)

    Comment.objects.create(post=post, user=request.user, text=comment_text)
    messages.success(request, "your comment has been posted successfully")
    return redirect('post-detail', post_id = post.id)


def category_posts(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    post_list = Post.objects.filter(category=category).order_by('-created_at')
    
    # Handle sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        post_list = post_list.order_by('created_at')
    elif sort == 'popular':
        post_list = post_list.order_by('-view_count')
    
    # Pagination
    paginator = Paginator(post_list, 9)  # 9 posts per page
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    return render(request, 'category_wise_post.html', {
        'category': category,
        'posts': posts,
    })

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    post_count = posts.paginator.count
    comment_count = Comment.objects.filter(user=user).count()
    upvote_count = Vote.objects.filter(user=user, value=1).count()
    downvote_count = Vote.objects.filter(user=user, value=-1).count()

    context = {
        'user': user,
        'posts': posts,
        'post_count': post_count,
        'comment_count': comment_count,
        'upvote_count': upvote_count,
        'downvote_count': downvote_count,
        'profile_created_at': user.profile.created_at,  # Add this line
    }

    return render(request, 'user_profile.html', context)



@login_required
def update_avatar(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('user_profile', username=request.user.username)

    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST' and request.FILES.get('avatar'):
        profile.avatar = request.FILES['avatar']
        profile.save()

    return redirect('user_profile', username=user.username)

@api_view(['GET'])
def trending_topics_api(request):
    trending_topics = get_trending_topics()
    serializer = TrendingTopicSerializer(trending_topics, many=True)
    return Response(serializer.data)

def get_trending_topics():
    last_24_hours = now() - timedelta(hours=24)
    trending_topics = Discussion.objects.filter(created_at__gte=last_24_hours) \
        .annotate(activity_score=(Count('upvotes') + Count('comments_count'))) \
        .order_by('-activity_score')[:5]  # Get top 5 trending topics
    return trending_topics


