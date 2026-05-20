import json
import csv
from django.shortcuts import render,redirect
from .models import Product,Customer,Order,Tag
from .forms import OrderForm, UpdateOrder, CustomerForm, productForm
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.http import HttpResponse
from.forms import CreateUserForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def loginpage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method=="POST":
            username=request.POST.get('username')
            password=request.POST.get('password')

            user=authenticate(request,username=username,password=password)

            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.info(request,"username or password is incorrect...!")
        return render(request,'account/login_page.html')


def logoutpage(request):
    logout(request)
    return redirect('loginpage')

def registrationpage(request):
    if request.user.is_authenticated:
        return redirect('home')
    form=CreateUserForm()
           
    if request.method=="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user=form.cleaned_data.get('username')
            messages.success(request,"Account was Created for"+ user)
            return redirect('loginpage')
            
    context={'form':form}
    return render(request,'account/registration_page.html',context)

@login_required(login_url='loginpage')
def analytics(request):
    orders = Order.objects.all()
    status_data = orders.values('status').annotate(count=Count('status'))
    orders_per_day = (
        orders
        .annotate(date=TruncDate('date_created'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    context = {
        'status_data': json.dumps(list(status_data), default=str),
        'orders_per_day': json.dumps(list(orders_per_day), default=str),
    }
    return render(request, 'account/analytics.html', context)

@login_required(login_url='loginpage')
def Home(request):
    orders=Order.objects.all()
    customers=Customer.objects.all()
    total_customer=customers.count()
    total_order=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='pending').count()
    out_for_delivery=orders.filter(status='out for delivery').count()
    
    context={
        'total_customer':total_customer,
        'total_order':total_order,
        'delivered':delivered,
        'pending':pending,
        'out_for_delivery':out_for_delivery,
        'customers':customers,
        'orders':orders,
    }

    return render(request,'account/dashboard.html',context)

@login_required(login_url='loginpage')
def Prod(request):
    product=Product.objects.all()
    context={'product':product}
    return render(request,'account/product.html',context)

@login_required(login_url='loginpage')
def cust(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()
    myFilter=OrderFilter(request.GET,queryset=orders)
    orders=myFilter.qs
    context = {
        'customer': customer,
        'orders': orders,
        'order_count': order_count,
        'myFilter':myFilter
    }

    return render(request, 'account/customer.html', context)

@login_required(login_url='loginpage')
def import_tag_csv(request):
    if request.method=="POST":
        csv_file=request.FILES.get("csv_file")

        if not csv_file:    
            return HttpResponse("No file uploaded", status=400)
        
        decoded_file=csv_file.read().decode("utf-8").splitlines()
        reader=csv.DictReader(decoded_file)

        for row in reader:
            Tag.objects.get_or_create(name=row["name"])
        return redirect('tag_list')
    
    return render(request,'account/manage_tag.html')

@login_required(login_url='loginpage')
def Customer_list(request):
    customer=Customer.objects.all()
    context={'customer':customer}
    return render(request,'account/customer_list.html',context)

@login_required(login_url='loginpage')
def create_customer(request):
    form=CustomerForm()
    if request.method == "POST":
        form=CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context={'form':form}
    return render(request,'account/create_customer.html',context)

@login_required(login_url='loginpage')
def update_Customer(request,pk):
    customer=Customer.objects.get(id=pk)
    form=CustomerForm(instance=customer)
    # update_form=CustomerForm(instance=customer)

    if request.method == 'POST':
        form=CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('/')
    context={'form':form}
    return render(request,'account/update_customer.html',context)

@login_required(login_url='loginpage')
def delete_customer(request,pk):
    customer=Customer.objects.get(id=pk)
    if request.method=="POST":
        customer.delete()
        return redirect('/')
    context={'customer':customer}
    return render(request,'account/delete_customer.html',context)

@login_required(login_url='loginpage')
def create_order(request):
    form=OrderForm()
    if request.method == "POST":
        form=OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context={'form':form}
    return render(request,'account/order_form.html',context)

@login_required(login_url='loginpage')
def place_order(request,pk):
    orderformset=inlineformset_factory(Customer,Order,fields=('Product','status'),extra=7)
    customer=Customer.objects.get(id=pk)
    formset=orderformset(queryset=Order.objects.none(),instance=customer)
    if request.method=="POST":
        formset=orderformset(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context={'form':formset}
    return render (request,'account/place_order.html',context)
        
@login_required(login_url='loginpage')
def updateorder(request,pk):
    order=Order.objects.get(id=pk)
    if request.method == 'POST':
        form=UpdateOrder(request.POST, instance=order)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.customer=order.customer
            instance.save()
            return redirect('/')
    else:
        form=UpdateOrder(instance=order)
    context={'form':form, 'order':order, 'customer_name':order.customer.name}
    return render(request, 'account/update_order.html', context)

@login_required(login_url='loginpage')
def deleteorder(request,pk):
    order=Order.objects.get(id=pk)
    if request.method=="POST":
        order.delete()
        return redirect('/')
    context={'order':order}
    return render(request,'account/delete_order.html',context)

@login_required(login_url='loginpage')
def order_list(request):
    order=Order.objects.all()
    return render(request,'account/order_list.html',{'order':order})

@login_required(login_url='loginpage')
def tag_list(request):
    tag=Tag.objects.all()
    context={'tag':tag}
    return render(request,'account/tag_list.html',context)

@login_required(login_url='loginpage')
def add_product(request):
    form=productForm()
    if request.method == "POST":
        form=productForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product')
    context={'form':form}
    return render(request,'account/add_product.html',context)

@login_required(login_url='loginpage')
def update_product(request,pk):
    product=Product.objects.get(id=pk)
    form=productForm(instance=product)

    if request.method == 'POST':
        form=productForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product')
    context={'form':form}
    return render(request,'account/update_product.html',context)

@login_required(login_url='loginpage')
def deleteproduct(request,pk):
    product=Product.objects.get(id=pk)
    if request.method=="POST":
        product.delete()
        return redirect('product')
    context={'product':product}
    return render(request,'account/delete_product.html',context)


# def update_order(request,pk):
#     order=Order.objects.get(id=pk)
#     form=OrderForm(instance=order)
#     update_form=UpdateOrder(instance=order)

#     if request.method == 'POST':
#         form=OrderForm(request.POST, instance=order)
#         if form.is_valid():
#             form.save()
#             return redirect('/')
#     context={'form':form}
#     return render(request,'account/order_form.html',context)

# def update_product(request,pk):
#     product=Product.objects.get(id=pk)
#     form=CustomerForm(instance=customer)
#    # update_form=CustomerForm(instance=customer)

#     if request.method == 'POST':
#         form=CustomerForm(request.POST, instance=customer)
#         if form.is_valid():
#             form.save()
#             return redirect('/')
#     context={'form':form}
#     return render(request,'account/delete_customer.html',context)
