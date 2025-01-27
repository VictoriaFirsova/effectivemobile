from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver


class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    def __str__(self):
        return f"{self.name} - {self.price}₽"


class Order(models.Model):
    table_number = models.IntegerField(verbose_name="Номер стола")
    items = models.ManyToManyField(Dish, verbose_name="Блюда")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'В ожидании'),
            ('ready', 'Готово'),
            ('paid', 'Оплачено'),
        ],
        default='pending',
        verbose_name="Статус",
    )


    def __str__(self):
        dishes = ', '.join([dish.name for dish in self.items.all()])
        return f"Заказ {self.id} - Стол {self.table_number} - Блюда: {dishes}"

class OrderDish(models.Model):
    order = models.ForeignKey(Order, related_name='orderdishes', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"