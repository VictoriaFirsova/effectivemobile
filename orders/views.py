from django.db.models import Sum
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import Order, Dish, OrderDish
from .forms import OrderForm, OrderSearchForm


class OrderListView(View):
    def get(self, request):
        orders = Order.objects.annotate(total_price_sum=Sum('items__price'))
        form = OrderForm()
        return render(request, 'order_list.html', {'orders': orders, 'form': form})

    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()  # Сохраняем заказ
            order.save()  # Дополнительно вызываем save для пересчета total_price
            return redirect('orders:order_list')
        orders = Order.objects.all()
        return render(request, 'order_list.html', {'orders': orders, 'form': form})


class OrderCreateView(View):
    def get(self, request):
        form = OrderForm()
        dishes = Dish.objects.all()  # Получаем все блюда
        return render(request, 'order_create.html', {'form': form, 'dishes': dishes})

    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # Создаем заказ, но не сохраняем его еще
            order.save()  # Сохраняем заказ в базе данных

            # Добавляем выбранные блюда в заказ
            for dish in form.cleaned_data['items']:
                OrderDish.objects.create(order=order, dish=dish, quantity=1)  # Устанавливаем начальное количество как 1

            # Перенаправляем на страницу редактирования заказа
            return redirect('orders:order_update', pk=order.pk)

        dishes = Dish.objects.all()  # Отображаем блюда в случае неуспешного создания
        return render(request, 'order_create.html', {'form': form, 'dishes': dishes})


class OrderUpdateView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        dishes = Dish.objects.all()  # Получаем все блюда
        return render(request, 'order_update.html', {'order': order, 'dishes': dishes})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # Обновляем статус заказа, если это была отправка формы с изменением статуса
        if 'status_change' in request.POST:
            status = request.POST.get('status')
            if status:
                order.status = status
                order.save()

        # Получаем список выбранных блюд из формы
        dish_ids = request.POST.getlist('dishes')

        for dish_id in dish_ids:
            dish = get_object_or_404(Dish, id=dish_id)

            # Проверяем, есть ли уже это блюдо в заказе
            order_dish, created = OrderDish.objects.get_or_create(order=order, dish=dish)

            if not created:
                # Если блюдо уже есть в заказе, увеличиваем его количество
                order_dish.quantity += 1
                order_dish.save()

        # Пересчитываем общую цену заказа
        order.total_price = sum(order_dish.dish.price * order_dish.quantity for order_dish in order.orderdishes.all())
        order.save()

        return redirect('orders:order_update', pk=order.pk)

class OrderRemoveDishView(View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        dish_id = request.POST.get('dish_id')

        if dish_id:
            # Получаем блюдо, которое нужно удалить
            dish = get_object_or_404(Dish, id=dish_id)

            # Получаем объект OrderDish, связывающий заказ и блюдо
            order_dish = get_object_or_404(OrderDish, order=order, dish=dish)

            if order_dish.quantity > 1:
                # Если количество блюда больше 1, уменьшаем его на 1
                order_dish.quantity -= 1
                order_dish.save()
            else:
                # Если количество блюда 1, удаляем блюдо из заказа
                order_dish.delete()

            # Пересчитываем общую цену заказа
            order.total_price = sum(order_dish.dish.price * order_dish.quantity for order_dish in order.orderdishes.all())
            order.save()

        return redirect('orders:order_update', pk=order.pk)

class OrderDeleteView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return redirect('orders:order_list')

def revenue_calculation(request):
    # Получаем все заказы со статусом "оплачено"
    paid_orders = Order.objects.filter(status='paid')

    # Рассчитываем общую сумму выручки
    total_revenue = sum(order.total_price for order in paid_orders)

    return render(request, 'revenue_calculation.html', {'total_revenue': total_revenue, 'paid_orders': paid_orders})

def order_search(request):
    form = OrderSearchForm(request.GET)
    orders = Order.objects.all()

    if form.is_valid():
        table_number = form.cleaned_data.get('table_number')
        status = form.cleaned_data.get('status')

        if table_number:
            orders = orders.filter(table_number=table_number)
        if status:
            orders = orders.filter(status=status)

    return render(request, 'order_search.html', {'form': form, 'orders': orders})