from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver


class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    def __str__(self):
        return f"{self.name} - {self.price}₽"


class Order(models.Model):
    """
    Represents an order within the system.

    This class is designed to handle orders in a restaurant or similar business.
    It stores information about the items included in the order, the total
    price, the table number associated with the order, and the current status
    of the order. The status can be updated as the order progresses, and each
    item in the order references the `Dish` model.

    :ivar items: The dishes included in the order.
    :type items: ManyToManyField
    :ivar total_price: The total cost of all items in the order. Uses decimal
        precision to accurately handle monetary values.
    :type total_price: DecimalField
    :ivar table_number: The table number associated with this order.
    :type table_number: IntegerField
    :ivar status: The current status of the order, which can be one of
        'pending', 'ready', or 'paid'.
    :type status: CharField
    """
    items = models.ManyToManyField(Dish, verbose_name="Блюда")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено'),
    ]

    table_number = models.IntegerField(verbose_name="Номер стола")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )


    def __str__(self):
        dishes = ', '.join([dish.name for dish in self.items.all()])
        return f"Заказ {self.id} - Стол {self.table_number} - Блюда: {dishes}"

class OrderDish(models.Model):
    """
    Represents the association between an order and a dish with the quantity
    of the dish in the specific order.

    The `OrderDish` class models a many-to-one relationship where each
    instance associates a particular order with a specific dish and the number
    of times the dish is ordered. It helps in maintaining and retrieving
    detailed information about the composition of an order.

    :ivar order: The order associated with this dish instance.
    :type order: Order
    :ivar dish: The dish associated with this order instance.
    :type dish: Dish
    :ivar quantity: The quantity of the dish in the specific order.
    :type quantity: int
    """
    order = models.ForeignKey(Order, related_name='orderdishes', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"