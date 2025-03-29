from rest_framework import serializers
from .models import Discussion


# Trending Topic Serializer
class TrendingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['title', 'upvotes', 'description']
