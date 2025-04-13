from rest_framework import serializers
from django.contrib.auth.models import User
from taggit.models import Tag
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    # Переписанный способ работы с тегами
    tags = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects.all(), many=True)
    author = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ("id", "h1", "title", "slug", "description", "content", "image", "created_at", "author", "tags")
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
