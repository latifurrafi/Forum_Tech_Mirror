from rest_framework import serializers
from .models import Discussion


class TrendingTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['title', 'tags', 'description']

