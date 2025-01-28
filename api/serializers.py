from rest_framework import serializers
from orders.models import Order, OrderDish, Dish


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price']


class OrderDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)  # Подключаем вложенный сериализатор блюда

    class Meta:
        model = OrderDish
        fields = ['id', 'dish', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderDishSerializer(source='orderdish_set', many=True, read_only=False)  # Связанные блюда заказа

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'total_price', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('orderdish_set', [])  # Извлекаем связанные данные
        order = Order.objects.create(**validated_data)  # Создаем основной заказ
        for item_data in items_data:
            OrderDish.objects.create(order=order, **item_data)  # Создаем связанные блюда
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('orderdish_set', None)
        instance.table_number = validated_data.get('table_number', instance.table_number)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if items_data is not None:
            instance.orderdish_set.all().delete()  # Удаляем старые блюда
            for item_data in items_data:
                OrderDish.objects.create(order=instance, **item_data)  # Создаем новые блюда

        return instance