from rest_framework import viewsets, mixins

from logistic.models import Product, Stock
from logistic.serializers import ProductSerializer, StockSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    # при необходимости добавьте параметры фильтрации


class StockViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    # при необходимости добавьте параметры фильтрации
