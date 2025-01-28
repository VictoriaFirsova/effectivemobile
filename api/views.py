from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from orders.models import Order
from .serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    """
    ViewSet для управления заказами: позволяет добавлять, обновлять, удалять и искать заказы.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Поиск заказа по номеру стола и статусу через параметры запроса.
        Пример: /api/orders/search/?table_number=1&status=paid
        """
        table_number = request.query_params.get('table_number')
        status = request.query_params.get('status')

        # Фильтруем заказы на основе параметров
        queryset = self.queryset
        if table_number:
            queryset = queryset.filter(table_number=table_number)
        if status:
            queryset = queryset.filter(status=status)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

