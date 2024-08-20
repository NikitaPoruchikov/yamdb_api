from rest_framework import filters, viewsets

from api.permissions import IsAdminOrReadOnly


class CategoryGenreMixin(viewsets.GenericViewSet,
                         viewsets.mixins.CreateModelMixin,
                         viewsets.mixins.DestroyModelMixin,
                         viewsets.mixins.ListModelMixin,
                         ):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
