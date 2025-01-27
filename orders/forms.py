from django import forms
from .models import Order, Dish

class OrderForm(forms.ModelForm):
    items = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Блюда"
    )

    class Meta:
        model = Order
        fields = ['table_number', 'items', 'status']


class OrderUpdateForm(forms.ModelForm):
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
    table_number = forms.IntegerField(required=False, label="Номер стола")
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Все статусы'), ('pending', 'В ожидании'), ('ready', 'Готово'), ('paid', 'Оплачено')],
        label="Статус"
    )