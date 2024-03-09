from rest_framework import filters, mixins, viewsets


class BaseTagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
