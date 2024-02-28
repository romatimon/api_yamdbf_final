from rest_framework.filters import SearchFilter
from rest_framework import viewsets, mixins

from .permissions import IsAdminOrReadOnly


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
