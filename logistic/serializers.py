from rest_framework import serializers
from .models import  Product, Stock, StockProduct
from django.core.exceptions import ObjectDoesNotExist


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = '__all__'


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = '__all__'
        write_only_fields = ['stock']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    # настройте сериализатор для склада

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        for position in positions:
            position['stock'] = stock.id
            serializer = ProductPositionSerializer(data=position)
            if serializer.is_valid():
                serializer.create(validated_data=serializer.validated_data)

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        for position in positions:
            position['stock'] = stock.id
            serializer = ProductPositionSerializer(data=position)
            if serializer.is_valid(raise_exception=True):
                try:
                    position_instance = StockProduct.objects.get(
                        stock=serializer.validated_data['stock'],
                        product=serializer.validated_data['product']
                    )
                    serializer.update(
                        instance=position_instance,
                        validated_data=serializer.validated_data
                    )
                except ObjectDoesNotExist:
                    serializer.create(validated_data=serializer.validated_data)
        return stock

    class Meta:
        model = Stock
        fields = '__all__'