# social_media_manager/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Social Media API Configuration
SOCIAL_MEDIA_APIS = {
    'FACEBOOK': {
        'APP_ID': os.environ.get('FACEBOOK_APP_ID'),
        'APP_SECRET': os.environ.get('FACEBOOK_APP_SECRET'),
        'API_VERSION': 'v18.0',
        'BASE_URL': 'https://graph.facebook.com/',
        'RATE_LIMIT': 200,  # per hour
    },
    'INSTAGRAM': {
        'APP_ID': os.environ.get('INSTAGRAM_APP_ID'),
        'APP_SECRET': os.environ.get('INSTAGRAM_APP_SECRET'),
        'API_VERSION': 'v18.0',
        'BASE_URL': 'https://graph.instagram.com/',
        'RATE_LIMIT': 240,  # per hour
    },
    'LINKEDIN': {
        'CLIENT_ID': os.environ.get('LINKEDIN_CLIENT_ID'),
        'CLIENT_SECRET': os.environ.get('LINKEDIN_CLIENT_SECRET'),
        'API_VERSION': 'v2',
        'BASE_URL': 'https://api.linkedin.com/v2/',
        'RATE_LIMIT': 500,  # per day
    },
    'TWITTER': {
        'API_KEY': os.environ.get('TWITTER_API_KEY'),
        'API_SECRET': os.environ.get('TWITTER_API_SECRET'),
        'BEARER_TOKEN': os.environ.get('TWITTER_BEARER_TOKEN'),
        'API_VERSION': '2',
        'BASE_URL': 'https://api.twitter.com/2/',
        'RATE_LIMIT': 300,  # per 15 minutes
    },
}

# ============================================================================
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class SocialMediaAccount(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_id = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'platform', 'account_id']

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    platforms = models.JSONField(default=list)  # List of platform names
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateTimeField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}..."

class PostMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file_url = models.URLField()
    file_size = models.BigIntegerField()
    alt_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PostPublication(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='publications')
    account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE)
    platform_post_id = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    is_success = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['post', 'account']

class PostAnalytics(models.Model):
    publication = models.OneToOneField(PostPublication, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    raw_data = models.JSONField(default=dict)  # Store platform-specific data

# ============================================================================
# services/social_media_service.py
import requests
import json
from abc import ABC, abstractmethod
from django.conf import settings
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SocialMediaAPI(ABC):
    """Abstract base class for social media APIs"""
    
    def __init__(self, account: SocialMediaAccount):
        self.account = account
        self.config = self._get_config()
    
    @abstractmethod
    def _get_config(self) -> Dict:
        """Get platform-specific configuration"""
        pass
    
    @abstractmethod
    def create_post(self, content: str, media_urls: List[str] = None) -> Dict:
        """Create a post on the platform"""
        pass
    
    @abstractmethod
    def delete_post(self, post_id: str) -> bool:
        """Delete a post from the platform"""
        pass
    
    @abstractmethod
    def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a specific post"""
        pass
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        """Make HTTP request with error handling"""
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

class FacebookAPI(SocialMediaAPI):
    def _get_config(self):
        return settings.SOCIAL_MEDIA_APIS['FACEBOOK']
    
    def create_post(self, content: str, media_urls: List[str] = None) -> Dict:
        url = f"{self.config['BASE_URL']}/{self.config['API_VERSION']}/{self.account.account_id}/feed"
        
        data = {
            'message': content,
            'access_token': self.account.access_token
        }
        
        if media_urls:
            # Handle media upload separately for Facebook
            media_ids = []
            for media_url in media_urls:
                media_id = self._upload_media(media_url)
                if media_id:
                    media_ids.append(media_id)
            
            if media_ids:
                data['attached_media'] = json.dumps([{'media_fbid': mid} for mid in media_ids])
        
        return self._make_request('POST', url, data=data)
    
    def _upload_media(self, media_url: str) -> str:
        """Upload media to Facebook and return media ID"""
        url = f"{self.config['BASE_URL']}/{self.config['API_VERSION']}/{self.account.account_id}/photos"
        
        data = {
            'url': media_url,
            'published': 'false',  # Upload without publishing
            'access_token': self.account.access_token
        }
        
        result = self._make_request('POST', url, data=data)
        return result.get('id') if 'error' not in result else None
    
    def delete_post(self, post_id: str) -> bool:
        url = f"{self.config['BASE_URL']}/{self.config['API_VERSION']}/{post_id}"
        
        params = {'access_token': self.account.access_token}
        result = self._make_request('DELETE', url, params=params)
        
        return 'error' not in result
    
    def get_post_analytics(self, post_id: str) -> Dict:
        url = f"{self.config['BASE_URL']}/{self.config['API_VERSION']}/{post_id}"
        
        params = {
            'fields': 'reactions.summary(true),comments.summary(true),shares',
            'access_token': self.account.access_token
        }
        
        result = self._make_request('GET', url, params=params)
        
        if 'error' in result:
            return {}
        
        # Parse Facebook analytics format
        analytics = {
            'likes': result.get('reactions', {}).get('summary', {}).get('total_count', 0),
            'comments': result.get('comments', {}).get('summary', {}).get('total_count', 0),
            'shares': result.get('shares', {}).get('count', 0),
            'raw_data': result
        }
        
        return analytics

class TwitterAPI(SocialMediaAPI):
    def _get_config(self):
        return settings.SOCIAL_MEDIA_APIS['TWITTER']
    
    def create_post(self, content: str, media_urls: List[str] = None) -> Dict:
        url = f"{self.config['BASE_URL']}/tweets"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}",
            'Content-Type': 'application/json'
        }
        
        data = {'text': content}
        
        if media_urls:
            media_ids = []
            for media_url in media_urls:
                media_id = self._upload_media(media_url)
                if media_id:
                    media_ids.append(media_id)
            
            if media_ids:
                data['media'] = {'media_ids': media_ids}
        
        return self._make_request('POST', url, headers=headers, json=data)
    
    def _upload_media(self, media_url: str) -> str:
        """Upload media to Twitter and return media ID"""
        # Twitter media upload is more complex - requires chunked upload for large files
        # Simplified version here
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}"
        }
        
        # Download media first (in production, handle this better)
        media_response = requests.get(media_url)
        if media_response.status_code != 200:
            return None
        
        files = {'media': media_response.content}
        result = self._make_request('POST', upload_url, headers=headers, files=files)
        
        return result.get('media_id_string') if 'error' not in result else None
    
    def delete_post(self, post_id: str) -> bool:
        url = f"{self.config['BASE_URL']}/tweets/{post_id}"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}"
        }
        
        result = self._make_request('DELETE', url, headers=headers)
        return 'error' not in result
    
    def get_post_analytics(self, post_id: str) -> Dict:
        url = f"{self.config['BASE_URL']}/tweets/{post_id}"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}"
        }
        
        params = {
            'tweet.fields': 'public_metrics,created_at',
            'expansions': 'author_id'
        }
        
        result = self._make_request('GET', url, headers=headers, params=params)
        
        if 'error' in result or 'data' not in result:
            return {}
        
        metrics = result['data'].get('public_metrics', {})
        
        return {
            'likes': metrics.get('like_count', 0),
            'comments': metrics.get('reply_count', 0),
            'shares': metrics.get('retweet_count', 0),
            'impressions': metrics.get('impression_count', 0),
            'raw_data': result
        }

class LinkedInAPI(SocialMediaAPI):
    def _get_config(self):
        return settings.SOCIAL_MEDIA_APIS['LINKEDIN']
    
    def create_post(self, content: str, media_urls: List[str] = None) -> Dict:
        url = f"{self.config['BASE_URL']}/ugcPosts"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}",
            'Content-Type': 'application/json'
        }
        
        post_data = {
            "author": f"urn:li:person:{self.account.account_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        if media_urls:
            # Handle media upload for LinkedIn
            media_assets = []
            for media_url in media_urls:
                asset = self._upload_media(media_url)
                if asset:
                    media_assets.append(asset)
            
            if media_assets:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = media_assets
        
        return self._make_request('POST', url, headers=headers, json=post_data)
    
    def _upload_media(self, media_url: str) -> Dict:
        """Upload media to LinkedIn and return asset info"""
        # LinkedIn media upload process is complex - simplified here
        register_url = f"{self.config['BASE_URL']}/assets?action=registerUpload"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}",
            'Content-Type': 'application/json'
        }
        
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{self.account.account_id}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        result = self._make_request('POST', register_url, headers=headers, json=register_data)
        
        if 'error' in result:
            return None
        
        # In production, you would upload the actual media file here
        # and return the proper asset structure
        return {
            "status": "READY",
            "description": {
                "text": "Uploaded media"
            },
            "media": result.get('value', {}).get('asset', '')
        }
    
    def delete_post(self, post_id: str) -> bool:
        url = f"{self.config['BASE_URL']}/ugcPosts/{post_id}"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}"
        }
        
        result = self._make_request('DELETE', url, headers=headers)
        return 'error' not in result
    
    def get_post_analytics(self, post_id: str) -> Dict:
        url = f"{self.config['BASE_URL']}/socialActions/{post_id}"
        
        headers = {
            'Authorization': f"Bearer {self.account.access_token}"
        }
        
        result = self._make_request('GET', url, headers=headers)
        
        if 'error' in result:
            return {}
        
        # LinkedIn analytics structure varies
        return {
            'likes': result.get('numLikes', 0),
            'comments': result.get('numComments', 0),
            'shares': result.get('numShares', 0),
            'raw_data': result
        }

# ============================================================================
# services/post_service.py
from typing import Dict, List
from django.utils import timezone
from .models import Post, PostPublication, SocialMediaAccount
from .social_media_service import FacebookAPI, TwitterAPI, LinkedInAPI

class PostService:
    """Service for managing social media posts"""
    
    API_CLASSES = {
        'facebook': FacebookAPI,
        'twitter': TwitterAPI,
        'linkedin': LinkedInAPI,
        # Add Instagram when implemented
    }
    
    @classmethod
    def create_post(cls, user, content: str, platforms: List[str], 
                   scheduled_date=None, media_urls: List[str] = None) -> Post:
        """Create a new post"""
        post = Post.objects.create(
            user=user,
            content=content,
            platforms=platforms,
            scheduled_date=scheduled_date,
            status='scheduled' if scheduled_date else 'draft'
        )
        
        # If not scheduled, publish immediately
        if not scheduled_date:
            cls.publish_post(post, media_urls)
        
        return post
    
    @classmethod
    def publish_post(cls, post: Post, media_urls: List[str] = None) -> Dict:
        """Publish a post to all selected platforms"""
        results = {}
        
        for platform in post.platforms:
            try:
                # Get user's account for this platform
                account = SocialMediaAccount.objects.get(
                    user=post.user,
                    platform=platform,
                    is_active=True
                )
                
                # Get appropriate API class
                api_class = cls.API_CLASSES.get(platform)
                if not api_class:
                    results[platform] = {'error': f'Platform {platform} not supported'}
                    continue
                
                # Create API instance and publish
                api = api_class(account)
                result = api.create_post(post.content, media_urls)
                
                # Create publication record
                publication = PostPublication.objects.create(
                    post=post,
                    account=account,
                    platform_post_id=result.get('id', ''),
                    published_at=timezone.now() if 'error' not in result else None,
                    error_message=result.get('error', ''),
                    is_success='error' not in result
                )
                
                results[platform] = {
                    'success': publication.is_success,
                    'post_id': publication.platform_post_id,
                    'error': publication.error_message
                }
                
            except SocialMediaAccount.DoesNotExist:
                results[platform] = {'error': f'No active {platform} account found'}
            except Exception as e:
                results[platform] = {'error': str(e)}
        
        # Update post status
        successful_platforms = [p for p, r in results.items() if r.get('success')]
        if successful_platforms:
            post.status = 'published'
            post.published_date = timezone.now()
        else:
            post.status = 'failed'
        
        post.save()
        
        return results
    
    @classmethod
    def delete_post(cls, post: Post) -> Dict:
        """Delete a post from all platforms"""
        results = {}
        
        for publication in post.publications.filter(is_success=True):
            try:
                api_class = cls.API_CLASSES.get(publication.account.platform)
                if not api_class:
                    continue
                
                api = api_class(publication.account)
                success = api.delete_post(publication.platform_post_id)
                
                results[publication.account.platform] = {
                    'success': success,
                    'error': '' if success else 'Failed to delete from platform'
                }
                
            except Exception as e:
                results[publication.account.platform] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    @classmethod
    def get_post_analytics(cls, post: Post) -> Dict:
        """Get analytics for all publications of a post"""
        analytics = {}
        
        for publication in post.publications.filter(is_success=True):
            try:
                api_class = cls.API_CLASSES.get(publication.account.platform)
                if not api_class:
                    continue
                
                api = api_class(publication.account)
                platform_analytics = api.get_post_analytics(publication.platform_post_id)
                
                if platform_analytics:
                    # Update or create analytics record
                    from .models import PostAnalytics
                    post_analytics, created = PostAnalytics.objects.get_or_create(
                        publication=publication,
                        defaults=platform_analytics
                    )
                    
                    if not created:
                        for key, value in platform_analytics.items():
                            if key != 'raw_data':
                                setattr(post_analytics, key, value)
                        post_analytics.raw_data = platform_analytics.get('raw_data', {})
                        post_analytics.save()
                    
                    analytics[publication.account.platform] = platform_analytics
                
            except Exception as e:
                analytics[publication.account.platform] = {'error': str(e)}
        
        return analytics

# ============================================================================
# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Post, SocialMediaAccount
from .services.post_service import PostService
from .serializers import PostSerializer, SocialMediaAccountSerializer

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        
        # Handle immediate publishing or scheduling
        if post.scheduled_date is None:
            media_urls = self.request.data.get('media_urls', [])
            results = PostService.publish_post(post, media_urls)
            return Response({
                'post': PostSerializer(post).data,
                'publication_results': results
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Manually publish a draft post"""
        post = get_object_or_404(Post, pk=pk, user=request.user)
        
        if post.status != 'draft':
            return Response(
                {'error': 'Only draft posts can be published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        media_urls = request.data.get('media_urls', [])
        results = PostService.publish_post(post, media_urls)
        
        return Response({
            'post': PostSerializer(post).data,
            'publication_results': results
        })
    
    @action(detail=True, methods=['delete'])
    def delete_from_platforms(self, request, pk=None):
        """Delete post from all social media platforms"""
        post = get_object_or_404(Post, pk=pk, user=request.user)
        
        results = PostService.delete_post(post)
        
        return Response({
            'message': 'Post deletion attempted',
            'results': results
        })
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a post"""
        post = get_object_or_404(Post, pk=pk, user=request.user)
        
        analytics = PostService.get_post_analytics(post)
        
        return Response({
            'post_id': post.id,
            'analytics': analytics
        })

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    serializer_class = SocialMediaAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialMediaAccount.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def connect_account(self, request):
        """Connect a new social media account"""
        platform = request.data.get('platform')
        access_token = request.data.get('access_token')
        account_id = request.data.get('account_id')
        account_name = request.data.get('account_name')
        
        if not all([platform, access_token, account_id]):
            return Response(
                {'error': 'platform, access_token, and account_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update account
        account, created = SocialMediaAccount.objects.update_or_create(
            user=request.user,
            platform=platform,
            account_id=account_id,
            defaults={
                'account_name': account_name,
                'access_token': access_token,
                'is_active': True
            }
        )
        
        return Response({
            'message': 'Account connected successfully',
            'account': SocialMediaAccountSerializer(account).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

# ============================================================================
# serializers.py
from rest_framework import serializers
from .models import Post, SocialMediaAccount, PostMedia, PostPublication

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'platforms', 'status', 'scheduled_date', 
                 'published_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'published_date', 'created_at', 'updated_at']
    
    def validate_platforms(self, value):
        """Validate that user has connected accounts for selected platforms"""
        user = self.context['request'].user
        
        available_platforms = SocialMediaAccount.objects.filter(
            user=user,
            is_active=True
        ).values_list('platform', flat=True)
        
        for platform in value:
            if platform not in available_platforms:
                raise serializers.ValidationError(
                    f'No active {platform} account found. Please connect your account first.'
                )
        
        return value

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaAccount
        fields = ['id', 'platform', 'account_id', 'account_name', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# ============================================================================
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, SocialMediaAccountViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'accounts', SocialMediaAccountViewSet, basename='account')

urlpatterns = [
    path('api/', include(router.urls)),
]

# ============================================================================
# tasks.py (Celery tasks for scheduled posts)
from celery import shared_task
from django.utils import timezone
from .models import Post
from .services.post_service import PostService

@shared_task
def publish_scheduled_posts():
    """Publish posts that are scheduled for now or earlier"""
    now = timezone.now()
    
    scheduled_posts = Post.objects.filter(
        status='scheduled',
        scheduled_date__lte=now
    )
    
    for post in scheduled_posts:
        try:
            results = PostService.publish_post(post)
            print(f"Published post {post.id}: {results}")
        except Exception as e:
            print(f"Error publishing post {post.id}: {e}")
            post.status = 'failed'
            post.save()

@shared_task
def update_post_analytics():
    """Update analytics for all published posts"""
    published_posts = Post.objects.filter(status='published')
    
    for post in published_posts:
        try:
            analytics = PostService.get_post_analytics(post)
            print(f"Updated analytics for post {post.id}: {analytics}")
        except Exception as e:
            print(f"Error updating analytics for post {post.id}: {e}")

# ============================================================================
# requirements.txt
"""
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
celery==5.3.4
redis==5.0.1
requests==2.31.0
python-decouple==3.8
Pillow==10.0.1
django-storages==1.14.2
boto3==1.29.7
psycopg2-binary==2.9.9
"""

# ============================================================================
# Test Data Generator
def create_test_data():
    """Generate test data for development"""
    from django.contrib.auth.models import User
    from .models import SocialMediaAccount, Post
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Create test social media accounts
    platforms = ['facebook', 'twitter', 'linkedin', 'instagram']
    for platform in platforms:
        SocialMediaAccount.objects.get_or_create(
            user=user,
            platform=platform,
            account_id=f'test_{platform}_id',
            defaults={
                'account_name': f'Test {platform.title()} Account',
                'access_token': f'test_{platform}_token',
                'is_active': True
            }
        )
    
    # Create test posts
    test_posts = [
        {
            'content': 'Check out our new product launch! 🚀 #innovation #tech',
            'platforms': ['facebook', 'linkedin', 'twitter'],
            'status': 'published'
        },
        {
            'content': 'Behind the scenes at our office today 📸',
            'platforms': ['instagram', 'facebook'],
            'status': 'draft'
        },
        {
            'content': 'Exciting news coming soon! Stay tuned 🎉',
            'platforms': ['twitter', 'linkedin'],
            'status': 'scheduled',
            'scheduled_date': timezone.now() + timezone.timedelta(hours=2)
        }
    ]
    
    for post_data in test_posts:
        Post.objects.get_or_create(
            user=user,
            content=post_data['content'],
            defaults={
                'platforms': post_data['platforms'],
                'status': post_data['status'],
                'scheduled_date': post_data.get('scheduled_date')
            }
        )
