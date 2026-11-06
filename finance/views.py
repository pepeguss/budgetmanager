import calendar, json
from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CategoryForm, RecurringForm, TransactionForm
from .models import Category, RecurringIncome, Transaction
from .services import process_recurring

def base(request):
    process_recurring(request.user)
    return Transaction.objects.filter(user=request.user, hidden=False)
@login_required
def dashboard(request):
    qs = base(request); today = timezone.localdate()
    month = qs.filter(date__year=today.year,date__month=today.month)
    total = lambda q: q.aggregate(s=Sum('amount'))['s'] or Decimal('0')
    income = total(month.filter(kind='income')); expense = total(month.filter(kind='expense'))
    balance = total(qs.filter(kind='income')) - total(qs.filter(kind='expense'))
    months=[]
    for offset in range(5,-1,-1):
        n = today.year * 12 + today.month - 1 - offset; y, m = divmod(n, 12); m += 1
        subset=qs.filter(date__year=y,date__month=m)
        months.append({'label':['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек'][m-1], 'income':float(total(subset.filter(kind='income'))), 'expense':float(total(subset.filter(kind='expense')))})
    max_value=max([max(x['income'],x['expense']) for x in months] or [0]) or 1
    for item in months:
        item['income_height']=round(item['income']/max_value*100,2); item['expense_height']=round(item['expense']/max_value*100,2)
    categories=list(month.filter(kind='expense').values('category__name','category__color').annotate(total=Sum('amount')).order_by('-total'))
    for c in categories: c['percent']=round(float(c['total']/expense*100)) if expense else 0
    return render(request,'finance/dashboard.html',{'balance':balance,'income':income,'expense':expense,'months':months,'categories':categories,'recent':qs[:5], 'today':today})
@login_required
def operations(request):
    qs=base(request)
    kind=request.GET.get('kind',''); category=request.GET.get('category',''); month=request.GET.get('month','')
    if kind in ('income','expense'): qs=qs.filter(kind=kind)
    if category.isdigit(): qs=qs.filter(category_id=category)
    try:
        if month: y,m=map(int,month.split('-')); date(y,m,1); qs=qs.filter(date__year=y,date__month=m)
    except (ValueError,TypeError): month=''
    return render(request,'finance/operations.html',{'transactions':qs[:300], 'categories':Category.objects.filter(user=request.user),'selected_kind':kind,'selected_category':category,'selected_month':month})
@login_required
def operation_form(request,pk=None):
    obj=get_object_or_404(Transaction,user=request.user,pk=pk) if pk else None
    form=TransactionForm(request.POST or None,instance=obj,user=request.user)
    if request.method=='POST' and form.is_valid():
        item=form.save(commit=False); item.user=request.user; item.save(); messages.success(request,'Операция сохранена.'); return redirect('operations')
    return render(request,'finance/form.html',{'form':form,'title':'Изменить операцию' if obj else 'Новая операция','back':'operations'})
@login_required
@require_POST
def operation_delete(request,pk):
    obj=get_object_or_404(Transaction,user=request.user,pk=pk)
    # Keep the occurrence marker so automatic processing cannot recreate a deleted entry.
    if obj.recurring_id: obj.hidden=True; obj.save(update_fields=['hidden'])
    else: obj.delete()
    messages.success(request,'Операция удалена.'); return redirect('operations')
@login_required
def categories(request):
    form=CategoryForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        if Category.objects.filter(user=request.user,name__iexact=form.cleaned_data['name']).exists(): form.add_error('name','Такая категория уже существует.')
        else:
            obj=form.save(commit=False); obj.user=request.user; obj.save(); messages.success(request,'Категория добавлена.'); return redirect('categories')
    return render(request,'finance/categories.html',{'form':form,'categories':Category.objects.filter(user=request.user)})
@login_required
@require_POST
def category_delete(request,pk):
    get_object_or_404(Category,user=request.user,pk=pk).delete(); messages.success(request,'Категория удалена. Операции сохранены.'); return redirect('categories')
@login_required
def recurring(request):
    base(request); form=RecurringForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        obj=form.save(commit=False); obj.user=request.user; obj.save(); process_recurring(request.user); messages.success(request,'Автопополнение добавлено.'); return redirect('recurring')
    return render(request,'finance/recurring.html',{'form':form,'schedules':RecurringIncome.objects.filter(user=request.user).order_by('-id')})
@login_required
@require_POST
def recurring_toggle(request,pk):
    obj=get_object_or_404(RecurringIncome,user=request.user,pk=pk); obj.active=not obj.active; obj.save(); return redirect('recurring')
@login_required
@require_POST
def recurring_delete(request,pk):
    get_object_or_404(RecurringIncome,user=request.user,pk=pk).delete(); messages.success(request,'Автопополнение удалено. Начисленные операции сохранены.'); return redirect('recurring')
