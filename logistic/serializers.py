from rest_framework import serializers
from .models import  Product, Stock, StockProduct
from django.core.exceptions import ObjectDoesNotExist


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = '__all__'


class ReadProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        exclude = ['stock']

class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = '__all__'

class ReadStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        exclude = ['products']

class StockSerializer(serializers.ModelSerializer):
    positions = ReadProductPositionSerializer(many=True, write_only=True)

    # настройте сериализатор для склада

    def get_write_position_serializer(self, position, stock):
        product = position.pop('product')
        position['stock'], position['product'] = stock.id, product.id
        serializer = ProductPositionSerializer(data=position)
        serializer.is_valid()
        return serializer

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        for position in positions:
            serializer = self.get_write_position_serializer(position, stock)
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
            serializer = self.get_write_position_serializer(position, stock)
            try:
                position_instance = StockProduct.objects.get(
                    stock=position['stock'],
                    product=position['product']
                )
                serializer.update(validated_data=serializer.validated_data, instance=position_instance)
                
            except ObjectDoesNotExist:
                serializer.create(validated_data=serializer.validated_data)
        return stock

    class Meta:
        model = Stock
        exclude = ['products']
