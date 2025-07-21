from rest_framework import viewsets, mixins, filters
from django.shortcuts import get_object_or_404
from django.http import Http404

from logistic.models import Product, Stock
from logistic.serializers import ProductSerializer, StockSerializer, ReadStockSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    # при необходимости добавьте параметры фильтрации
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']


class StockViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Stock.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrive' or self.action == 'delete':
            return ReadStockSerializer
        return StockSerializer

    # при необходимости добавьте параметры фильтрации
    def get_queryset(self):
        queryset = Stock.objects.all()
        if self.action != 'list':
            return queryset

        product_pk = self.request.query_params.get('products')
        if product_pk is None:
            return queryset
        product = get_object_or_404(Product, pk=product_pk)
        
        queryset = queryset.filter(positions__product__exact=product, positions__quantity__gt=0)

        if not queryset.first():
            raise Http404(
                "No %s matches the given query." % queryset.model._meta.object_name
            )

        return queryset
