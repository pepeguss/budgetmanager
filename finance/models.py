from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=60)
    color = models.CharField('Цвет', max_length=7, default='#8EB69B')
    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['user','name'], name='unique_user_category')]
    def __str__(self): return self.name

class RecurringIncome(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=100)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    start_date = models.DateField('Первое пополнение')
    active = models.BooleanField('Активно', default=True)
    def __str__(self): return self.name

class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kind = models.CharField('Тип', max_length=7, choices=[(INCOME,'Пополнение'),(EXPENSE,'Расход')])
    title = models.CharField('Название', max_length=100)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField('Дата')
    category = models.ForeignKey(Category, verbose_name='Категория', null=True, blank=True, on_delete=models.SET_NULL)
    recurring = models.ForeignKey(RecurringIncome, null=True, blank=True, on_delete=models.SET_NULL)
    occurrence = models.DateField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    class Meta:
        ordering = ['-date','-id']
        constraints = [models.UniqueConstraint(fields=['recurring','occurrence'], name='unique_recurring_occurrence')]
