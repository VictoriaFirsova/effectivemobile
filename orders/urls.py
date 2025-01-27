from django.urls import path
from .views import (
    OrderListView, OrderCreateView,
    OrderUpdateView, OrderDeleteView, revenue_calculation, OrderRemoveDishView
)

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('order/<int:order_id>/remove_dish/', OrderRemoveDishView.as_view(), name='order_remove_dish'),
    path('<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('revenue/', revenue_calculation, name='revenue_calculation'),
]