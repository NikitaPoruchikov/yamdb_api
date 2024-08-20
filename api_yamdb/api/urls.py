from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, CustomUserViewSet,
                    GenreViewSet, ReviewViewSet, TitleViewSet, TokenObtainView,
                    UserRegistrationViewSet)

app_name = 'api'

router = DefaultRouter()

router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'titles', TitleViewSet, basename='title')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [path('v1/', include(router.urls))]

auth_urls = [
    path(
        'signup/',
        UserRegistrationViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path('token/', TokenObtainView.as_view(), name='token_obtain'),
]

urlpatterns += [path('v1/auth/', include(auth_urls))]
