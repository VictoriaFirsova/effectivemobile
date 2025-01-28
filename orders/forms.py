from django import forms
from .models import Order, Dish

class OrderForm(forms.ModelForm):
    """
    Represents a form for handling orders in a ModelForm structure.

    This class is used to facilitate the creation and handling of
    Order instances, allowing users to interact with the relevant
    model fields through a Django form. It includes specific fields
    such as table_number, items, and status, with custom widgets
    and queryset configurations.

    :ivar items: Field for selecting multiple dish items associated
                 with an order.
    :type items: ModelMultipleChoiceField
    """
    items = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Блюда"
    )

    class Meta:
        model = Order
        fields = ['table_number', 'items', 'status']


class OrderUpdateForm(forms.ModelForm):
    """
    Represents a form for updating orders.

    This form is used for updating the status and dishes associated with a given
    order. It includes fields for selecting the order's status from predefined
    choices and for choosing multiple dishes associated with the order.

    :ivar status: The status of the order, selected from predefined choices such as
        "В ожидании", "Готово", and "Оплачено".
    :type status: forms.ChoiceField
    :ivar dishes: The list of dishes selected for the order using a checkbox
        selection widget.
    :type dishes: forms.ModelMultipleChoiceField
    """
    status = forms.ChoiceField(
        choices=[('pending', 'В ожидании'), ('ready', 'Готово'), ('paid', 'Оплачено')],
        label="Статус"
    )
    dishes = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Выберите блюда"
    )

    class Meta:
        model = Order
        fields = ['status', 'dishes']

class OrderSearchForm(forms.Form):
    """
    Form to search for orders based on table number and order status.

    This form is used to filter and search for orders by providing a table number
    and/or selecting a specific status from the list of available order statuses.

    :ivar table_number: The number of the table used for filtering orders. It is an
        optional integer field.
    :type table_number: int
    :ivar status: The status of the order used for filtering. It is an optional
        choice field, allowing selection from predefined order statuses.
    :type status: str
    """
    table_number = forms.IntegerField(
        required=False,
        label="Номер стола",
        widget=forms.NumberInput(attrs={'placeholder': 'Введите номер стола'}),
    )
    STATUS_CHOICES = [('', 'Все')] + list(Order.STATUS_CHOICES)
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        label="Статус заказа",
        widget=forms.Select(attrs={'placeholder': 'Выберите статус'})
    )

