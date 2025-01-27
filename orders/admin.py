from django.contrib import admin
from .models import Dish, Order

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_number', 'total_price', 'status')
    filter_horizontal = ('items',)

