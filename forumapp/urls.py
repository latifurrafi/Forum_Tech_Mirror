from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .import views

urlpatterns = [
    path('',views.homepage, name='homepage'),
    path('create-post/', views.createPost, name="create-post"),
    path('post/<int:post_id>/', views.post_detail, name='post-detail'),  # Captures the post ID
    path('signup/', views.signup, name='signup'),
    path('post/<int:post_id>/comment/', views.add_comment, name="add_comment"),
    path('post/<int:post_id>/vote/', views.vote_post, name="vote_post"),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('bookmark/<int:post_id>/', views.bookmark_post, name="bookmark_post"),
    path('bookmark/<int:post_id>/', views.bookmark_post, name='bookmark-post'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/update-avatar/', views.update_avatar, name='update_avatar'),
    path('api/trending/', views.trending_topics_api, name='trending_topics_api'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)