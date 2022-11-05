
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Product, Cart, OrderPlaced, Customer
from .forms import CustomerProfile, CustomerRegistrationForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Class Based View
class ProductView(View):
    def get(self, request):
        total_item = 0
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')

        if request.user.is_authenticated:
            total_item = len(Cart.objects.filter(user=request.user))

        return render(request, 'app/home.html', {'topwears': topwears, 'bottomwears': bottomwears, 'mobiles': mobiles, 'total_item': total_item})


class ProductViewDetail(View):
    def get(self, request, pk):
        total_item = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()
            if request.user.is_authenticated:
                total_item = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/productdetail.html', {'product': product, 'item_already_in_cart': item_already_in_cart, 'total_item':total_item})


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    cart_items = Cart(user=user, product=product)
    cart_items.save()

    return redirect('/cart')


@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        # print(cart)
        amount = 0.0
        shipping_amount = 5.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        # print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount

                return render(request, 'app/addtocart.html', {"carts": cart, 'total_amount': total_amount, 'amount': amount, 'shipping_amount': shipping_amount})
        else:
            return render(request, 'app/cartitemempty.html')


def plust_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        amount = 0.0
        shipping_amount = 5.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            # float(total_amount = amount + shipping_amount) #Convert it into the floats

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)


@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()

        amount = 0.0
        shipping_amount = 5.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            # float(total_amount = amount + shipping_amount) #Convert it into the floats

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)


@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()

        amount = 0.0
        shipping_amount = 5.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            # float(total_amount = amount + shipping_amount) #Convert it into the floats

        data = {
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)


def buy_now(request):
    return render(request, 'app/buynow.html')


@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary'})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'op': op})


@login_required
def paymentdone(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)

    for c in cart:
        OrderPlaced(user=user, customer=customer,
                    product=c.product, quantity=c.quantity).save()
        c.delete()

    return redirect('orders')


def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Redmi' or data == 'Infinix' or data == 'Oppo' or data == 'Vivo' or data == 'Vivo' or data == 'Samsung':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__lt=30000)
    elif data == 'above':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__gt=30000)
    return render(request, 'app/mobile.html', {'mobiles': mobiles})


def topwear(request, data=None):
    if data == None:
        topwears = Product.objects.filter(category='TW')

    elif data == 'Nike' or data == 'Carrot' or data == 'Denim' or data == 'Gentleman' or data == 'CasualDress' or data == 'AwesomeTShirt':
        topwears = Product.objects.filter(category='TW').filter(brand=data)

    elif data == 'below':
        topwears = Product.objects.filter(
            category='TW').filter(discounted_price__lt=1000)

    elif data == 'above':
        topwears = Product.objects.filter(
            category='TW').filter(discounted_price__gt=1000)
    return render(request, 'app/topwears.html', {'topwears': topwears, 'active': 'btn-primary'})


# Authentication Registration and Login

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Congratulations, Registered successfully.")
        return render(request, 'app/customerregistration.html', {'form': form})


@login_required
def checkout(request):
    if request.user.is_authenticated:
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 5.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
            total_amount = amount + shipping_amount

        return render(request, 'app/checkout.html', {'add': add, 'cart_items': cart_items, 'total_amount': total_amount})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfile()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

    def post(self, request):
        form = CustomerProfile(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            zipcode = form.cleaned_data['zipcode']
            state = form.cleaned_data['state']
            reg = Customer(user=usr, name=name, locality=locality,
                           city=city, zipcode=zipcode, state=state)
            reg.save()
            messages.success(
                request, 'Congrulations, profile has been update.')

        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})




#Search Products
def search(request):
    query = None
    result = []
    if request.method == 'GET':
        query = request.GET.get('search')
        result = Product.objects.filter(Q(title__icontains=query) | Q(category__icontains=query))
    return render(request, 'app/search.html', {'query':query, 'result':result})