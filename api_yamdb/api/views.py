from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .mixins import CategoryGenreMixin
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorModeratorAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          CustomTokenObtainSerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializerNonSafe,
                          TitleSerializerSafe, UserSerializer,
                          UserSignUpSerializer)

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class UserSignUpViewSet(CreateModelMixin, viewsets.GenericViewSet):
    """ViewSet для регистрации пользователей."""

    serializer_class = UserSignUpSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainView(TokenObtainPairView):
    """Представление для получения пользовательских JWT-токенов."""

    serializer_class = CustomTokenObtainSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользовательскими данными."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer
    )
    def me(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CategoryGenreMixin):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorModeratorAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        return self.get_item().comments.all()

    def get_item(self):
        title_object = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        review_object = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=title_object
        )
        return review_object

    def perform_create(self, serializer):
        review = self.get_item()
        title = review.title
        serializer.save(author=self.request.user, review=review, title=title)


class GenreViewSet(CategoryGenreMixin):
    """ViewSet для управления жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для управления отзывами."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorModeratorAdmin)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        title_object = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title_object)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления произведениями."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializerSafe
        return TitleSerializerNonSafe
