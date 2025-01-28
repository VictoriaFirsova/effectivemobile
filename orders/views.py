from typing import Optional
from django.db.models import Sum
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.http import  HttpRequest, HttpResponse, HttpResponseRedirect
from django.views import View
from .models import Order, Dish, OrderDish
from .forms import OrderForm, OrderSearchForm


class OrderListView(View):
    """
    Handles the functionality for displaying and creating orders within a web application.

    OrderListView is a Django class-based view responsible for rendering a list of orders
    and managing the creation of new orders. It supports two request types: GET and POST.
    For GET requests, it retrieves and displays the list of orders alongside a form for
    creating new orders. For POST requests, it validates and processes form submissions
    to create new orders.
    """

    @staticmethod
    def get(request: HttpRequest) -> HttpResponse:
        """
        Handles the HTTP GET request to retrieve and display a list of orders with their total price
        and initialize the order creation form.

        :param request:
            The HTTP request object representing the client request.
        :return:
            The HTTP response object rendering the order list view with the annotated
            order data and form object.
        """
        orders = Order.objects.annotate(total_price_sum=Sum('items__price'))
        form = OrderForm()
        search_form = OrderSearchForm(request.GET or None)
        if search_form.is_valid():
            table_number = search_form.cleaned_data.get('table_number')
            status = search_form.cleaned_data.get('status')

            if table_number:
                orders = orders.filter(table_number=table_number)
            if status:
                orders = orders.filter(status=status)
        return render(request, 'order_list.html', {'orders': orders, 'form': form, 'search_form': search_form})

    @staticmethod
    def post(request: HttpRequest) -> HttpResponse:

        """
            Handles the HTTP POST request for processing and saving an order. It validates the received
            form data, saves the order if valid, and redirects to the order list view. If the form data
            is invalid, it fetches all orders and returns the order list view with errors and an
            unprocessed form.

            :param request: Represents the HTTP request received by the server.
            :type request: HttpRequest
            :return: In case of valid form submission, redirects the user to the order list view.
                     Otherwise, renders the 'order_list.html' template with the order data and form errors.
            :rtype: HttpResponse
            """
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.save()
            return redirect('orders:order_list')
        orders = Order.objects.all()
        search_form = OrderSearchForm()
        return render(request, 'order_list.html', {'orders': orders, 'form': form,'search_form': search_form})


class OrderCreateView(View):
    """
    Handles the creation of orders in the system.

    This view provides two primary methods to handle HTTP GET and POST
    requests for creating orders. When accessed via a GET request, it
    renders a form and displays available dishes. For a valid POST
    request, it saves the order with the provided data and associates
    the selected dishes with the order.

    """

    @staticmethod
    def get(request):

        """
            Handles GET requests for the order creation page.

            This method retrieves all the available dishes from the database and instantiates
            an empty order form. It then renders the 'order_create.html' template with the
            provided form and list of dishes.

            :param request: The HTTP request object.
            :type request: HttpRequest
            :return: The rendered HTML response containing the order creation form and the
                list of dishes.
            :rtype: HttpResponse
            """
        form = OrderForm()
        dishes = Dish.objects.all()
        return render(request, 'order_create.html', {'form': form, 'dishes': dishes})

    @staticmethod
    def post(request: HttpRequest) -> HttpResponse:

        """
            Handles HTTP POST requests for creating a new order. Processes form data to
            create an order, associates selected dishes with the order, and redirects
            to the order update page upon success. If the form is invalid, re-renders
            the form along with the list of dishes.

            :param request: Django's HTTP request object containing POST data.
            :type request: HttpRequest
            :return: A redirect to the order update page if the order is successfully created,
                otherwise re-renders the order creation page with the provided form.
            :rtype: HttpResponse
            """
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.save()

            for dish in form.cleaned_data['items']:
                OrderDish.objects.create(order=order, dish=dish, quantity=1)

            return redirect('orders:order_update', pk=order.pk)

        dishes = Dish.objects.all()
        return render(request, 'order_create.html', {'form': form, 'dishes': dishes})


class OrderUpdateView(View):
    """
    Provides functionality to view and update an existing order. This class-based view
    allows rendering the order and associated dishes for displaying and provides
    logic for handling order updates such as modifying the order's status, managing
    associated dishes, and recalculating the total price.

    This view supports GET and POST requests for interaction with the order.
    """

    @staticmethod
    def get(request: HttpRequest, pk: int) -> HttpResponse:
        """
        Handles the GET method to retrieve an order by its primary key and
        renders an order update page with the order details and list of dishes.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :param pk: The primary key of the order to retrieve.
        :type pk: int
        :return: An HTTP response with the rendered order update page.
        :rtype: HttpResponse
        """
        order = get_object_or_404(Order, pk=pk)
        dishes = Dish.objects.all()
        return render(request, 'order_update.html', {'order': order, 'dishes': dishes})

    @staticmethod
    def post(request: HttpRequest, pk: int) -> HttpResponseRedirect:
        """
        Handles POST request for updating an order. This method updates the order's
        status based on the data submitted through the form in the request. It also
        manages the addition of selected dishes to the order. If a dish is already
        present in the order, its quantity will be incremented. Finally, the total
        price of the order is recalculated based on the updated dish quantities.

        :param request: The HTTP request object containing form data for updating
            the order status and adding dishes.
            :type request: HttpRequest
        :param pk: The primary key of the Order to be updated.
            :type pk: int
        :return: An HTTP response redirecting to the order update page after
            successfully processing the POST request.
            :rtype: HttpResponseRedirect
        """
        order = get_object_or_404(Order, pk=pk)

        if 'status_change' in request.POST:
            status = request.POST.get('status')
            if status:
                order.status = status
                order.save()

        dish_ids = request.POST.getlist('dishes')

        for dish_id in dish_ids:
            dish = get_object_or_404(Dish, id=dish_id)

            order_dish, created = OrderDish.objects.get_or_create(order=order, dish=dish)

            if not created:
                order_dish.quantity += 1
                order_dish.save()

        order.total_price = sum(order_dish.dish.price * order_dish.quantity for order_dish in order.orderdishes.all())
        order.save()

        return redirect('orders:order_update', pk=order.pk)

class OrderRemoveDishView(View):
    """
    Handles the removal of a dish from an order.

    Provides logic to handle the removal of a dish from a specific order, either
    by decrementing the dish's quantity in the order if it has more than one, or
    by completely removing it. Also recalculates the total price of the order
    once the dish has been removed.
    """

    @staticmethod
    def post(request: HttpRequest, order_id: int) -> HttpResponse:
        """
        Handles the removal of a dish from an order. If the quantity of the dish in the order
        is greater than 1, it decreases the quantity by 1. If the quantity is 1, it removes
        the dish entirely from the order. After modifying the dish quantity or removing it,
        the total price of the order is recalculated and saved.

        :param request: HttpRequest object that contains details of the HTTP request made
            by the user, including POST data used to identify the dish to be removed.
        :param order_id: int Unique identifier of the order from which the dish is being
            removed.
        :return: HttpResponse that redirects the user to the `order_update` view of the
            specified order.
        """
        order = get_object_or_404(Order, pk=order_id)
        dish_id = request.POST.get('dish_id')

        if dish_id:
            dish = get_object_or_404(Dish, id=dish_id)
            order_dish = get_object_or_404(OrderDish, order=order, dish=dish)

            if order_dish.quantity > 1:
                order_dish.quantity -= 1
                order_dish.save()
            else:
                order_dish.delete()

            order.total_price = sum(order_dish.dish.price * order_dish.quantity for order_dish in order.orderdishes.all())
            order.save()

        return redirect('orders:order_update', pk=order.pk)

class OrderDeleteView(View):
    """
    Represents a view responsible for deleting an order.

    This class provides functionality to handle GET requests for deleting
    an order instance identified by its primary key (pk). It fetches the
    specific order, deletes it from the database, and redirects to the
    order list page.
    """

    @staticmethod
    def get(request: HttpRequest, pk: int) -> HttpResponseRedirect:
        """
        Handles the GET request to delete an order object and then redirects to the order list.

        This view retrieves an order object using its primary key (pk). If the object
        exists, it deletes the object from the database and redirects the user to
        the order list page.

        :param request: HttpRequest object representing the current request.
        :type request: HttpRequest
        :param pk: Primary key of the order to be deleted.
        :type pk: int
        :return: HttpResponseRedirect to the order list page after order deletion.
        :rtype: HttpResponseRedirect
        """
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return redirect('orders:order_list')

def revenue_calculation(request):
    """
    Calculates the total revenue from all paid orders and renders the result in the given
    HTML template. It retrieves all orders with a 'paid' status, calculates the cumulative
    total of their prices, and provides the calculated revenue along with the list of
    paid orders to the render context.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: An HTTP response rendering the 'revenue_calculation.html' template with the
             total revenue and list of paid orders in the context.
    :rtype: HttpResponse
    """
    paid_orders = Order.objects.filter(status='paid')
    total_revenue = paid_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    return render(request, 'revenue_calculation.html', {
        'total_revenue': total_revenue,
        'paid_orders': paid_orders
    })

def order_search(request: HttpRequest) -> HttpResponse:
    """
    Handles the search functionality for orders based on user input provided
    in the search form. Filters the order list based on table number and/or
    status if the provided form data is valid.

    :param request: The HTTP request object containing the GET data from the
        search form.
    :type request: HttpRequest
    :return: A rendered template displaying the filtered list of orders
        and the search form.
    :rtype: HttpResponse
    """
    search_form = OrderSearchForm(request.GET or None)
    orders = Order.objects.all()

    if search_form.is_valid():
        table_number = search_form.cleaned_data.get('table_number')
        status = search_form.cleaned_data.get('status')

        if table_number:
            orders = orders.filter(table_number=table_number)
        if status:
            orders = orders.filter(status=status)

    context = {
        'search_form': search_form,
        'orders': orders,
    }
    return render(request, 'order_list.html', context)
