from django.test import TestCase
from .models import Order

class OrderTests(TestCase):
    def test_order_creation(self):
        order = Order.objects.create(
            table_number=1,
            items=[{'name': 'Пицца', 'price': 10}, {'name': 'Салат', 'price': 5}],
        )
        self.assertEqual(order.total_price, 15)