from django.shortcuts import render
from rest_framework import viewsets,permissions,pagination,generics,filters
from .serializers import PostSerializer, TagSerializer, ContactSerailizer, RegisterSerializer, UserSerializer, CommentSerializer
from .models import Post, Comment
from rest_framework.response import Response        
from taggit.models import Tag
from rest_framework.views import APIView
from django.core.mail import send_mail


class PageNumberSetPagination(pagination.PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    ordering = 'created_at'


class PostViewSet(viewsets.ModelViewSet):
    search_fields = ['content','h1']
    filter_backends = (filters.SearchFilter,) # запрос на поиск выглядит так, добавляются квери параметры http://localhost:8000/api/posts/?search=геологии
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    pagination_class = PageNumberSetPagination

class TagDetailView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PageNumberSetPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug'].lower()
        tag = Tag.objects.get(slug=tag_slug)
        return Post.objects.filter(tags=tag)
    
class TagViews(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class AsideView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-id')[:5]
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class FeedBackView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ContactSerailizer

    def post(self, request, *args, **kwargs):
        serializer_class = ContactSerailizer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get('name')
            from_email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            send_mail(f'from {name} | {subject}', message, from_email, ['example.example1928@gmail.com'])
            return Response({"success": "Sent"})
        


class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно создан",
        })


class ProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args,  **kwargs):
        return Response({
            "user": UserSerializer(request.user, context=self.get_serializer_context()).data,
        })

class CommentView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.save()
        return Response({
            'comment': CommentSerializer(text, context=self.get_serializer_context()).data,
            'massage': 'коммент успешно создан'
        })
    def get(self, request, post_slug):
        try:
            post = Post.objects.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({"error": "Пост не найден"}, status=404)
        
        comments = Comment.objects.filter(post=post).order_by('-create_date')
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)




