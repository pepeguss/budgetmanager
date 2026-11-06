from datetime import date
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Category, RecurringIncome, Transaction
from .services import process_recurring

class FinanceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='one', password='strong-password')
        self.other = get_user_model().objects.create_user(username='other', password='strong-password')
        self.client.force_login(self.user)
    def test_recurring_short_month_and_idempotency(self):
        RecurringIncome.objects.create(user=self.user,name='Salary',amount=100,start_date=date(2024,1,31))
        with patch('finance.services.timezone.localdate',return_value=date(2024,3,31)):
            self.assertEqual(process_recurring(self.user),3)
            self.assertEqual(process_recurring(self.user),0)
        self.assertEqual(list(Transaction.objects.order_by('date').values_list('date',flat=True)),[date(2024,1,31),date(2024,2,29),date(2024,3,31)])
    def test_deleted_recurring_not_recreated(self):
        schedule=RecurringIncome.objects.create(user=self.user,name='Salary',amount=100,start_date=date(2024,1,1))
        with patch('finance.services.timezone.localdate',return_value=date(2024,1,1)):
            process_recurring(self.user)
            item=Transaction.objects.get(recurring=schedule)
            self.client.post(reverse('operation_delete',args=[item.pk]))
            self.assertEqual(process_recurring(self.user),0)
            self.assertTrue(Transaction.objects.get(pk=item.pk).hidden)
    def test_private_data_and_category_validation(self):
        cat=Category.objects.create(user=self.other,name='Private')
        item=Transaction.objects.create(user=self.other,kind='expense',title='Secret',amount=1,date=date.today(),category=cat)
        self.assertEqual(self.client.get(reverse('operation_edit',args=[item.pk])).status_code,404)
        response=self.client.post(reverse('operation_add'),{'kind':'expense','title':'x','amount':'10','date':'2024-01-01','category':cat.pk})
        self.assertEqual(response.status_code,200)
        self.assertFalse(Transaction.objects.filter(user=self.user).exists())
    def test_dashboard_and_login(self):
        self.assertEqual(self.client.get(reverse('dashboard')).status_code,200)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('dashboard')).status_code,302)
        self.assertEqual(self.client.get(reverse('login')).status_code,200)
