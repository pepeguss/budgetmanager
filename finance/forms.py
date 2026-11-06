from django import forms
from django.utils import timezone
from .models import Category, Transaction, RecurringIncome
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['kind','title','amount','date','category']
        widgets = {'date':forms.DateInput(attrs={'type':'date'}), 'amount':forms.NumberInput(attrs={'step':'0.01','min':'0.01','placeholder':'0,00'}), 'title':forms.TextInput(attrs={'placeholder':'Например, продукты'})}
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['date'].initial = timezone.localdate()
        self.fields['category'].required = False
    def clean(self):
        data = super().clean()
        if data.get('kind') == Transaction.EXPENSE and not data.get('category'): self.add_error('category','Выберите категорию расхода.')
        if data.get('kind') == Transaction.INCOME: data['category'] = None
        return data
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','color']
        widgets = {'name':forms.TextInput(attrs={'placeholder':'Например, продукты'}), 'color':forms.TextInput(attrs={'type':'color'})}
class RecurringForm(forms.ModelForm):
    class Meta:
        model = RecurringIncome
        fields = ['name','amount','start_date']
        widgets = {'name':forms.TextInput(attrs={'placeholder':'Например, зарплата'}), 'amount':forms.NumberInput(attrs={'step':'0.01','min':'0.01','placeholder':'0,00'}), 'start_date':forms.DateInput(attrs={'type':'date'})}
