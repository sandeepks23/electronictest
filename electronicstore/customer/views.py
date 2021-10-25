from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from .forms import RegistrationForm, LoginForm, UserForm, UpdateForm, ReviewForm, PlaceOrderForm
from .models import Cart, Review, Userdetails, Orders
from seller.models import Products,Brand
from .decorators import signin_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import IntegerField, Case, Value, When,Sum



class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = "cust_registration.html"
    success_url = reverse_lazy("cust_signin")


class SignInView(TemplateView):
    template_name = "cust_login.html"
    form_class = LoginForm
    context = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context["form"] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("customer_home")
            else:
                self.context["form"] = form
                return render(request, self.template_name, self.context)


@signin_required
def signout(request):
    logout(request)
    return redirect("cust_signin")


def cart_count(user):
    cnt=Cart.objects.filter(user=user,status='ordernotplaced').count()
    return cnt
# @method_decorator(signin_required, name="dispatch")
# class HomePageView(ListView):
#     template_name = 'homepage.html'
#     model = Products
#     context_object_name = "products"

class HomePageView(TemplateView):
    template_name = 'homepage.html'
    context={}
    def get(self, request, *args, **kwargs):
        products=Products.objects.all()
        brands=Brand.objects.all()
        cnt=cart_count(request.user)
        self.context['products']=products
        self.context['cnt']=cnt
        self.context['brands']=brands
        return render(request,self.template_name,self.context)

def search(request):
    search = request.GET['q']
    product = Products.objects.filter(product_name__icontains=search)
    context = {'product': product}
    return render(request, 'search.html', context)


def mobiles(request):
    mobiles = Products.objects.filter(category='mobile')
    context = {'mobiles': mobiles}
    return render(request, 'category.html', context)


def laptops(request):
    laptops = Products.objects.filter(category="laptop")
    context = {'laptops': laptops}
    return render(request, 'category.html', context)


def tablets(request):
    tablets = Products.objects.filter(category="tablet")
    context = {'tablets': tablets}
    return render(request, 'category.html', context)


def price_low_to_high(request):
    low = Products.objects.all().order_by('price')
    context = {'low': low}
    return render(request, 'price_range.html', context)


def price_high_to_low(request):
    high = Products.objects.all().order_by('-price')
    context = {'high': high}
    return render(request, 'price_range.html', context)


class ViewDetails(TemplateView):
    template_name = "my_profile.html"


class EditDetails(TemplateView):
    user_form = UserForm
    profile_form = UpdateForm
    template_name = "user_details.html"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request):
        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = UpdateForm(post_data, file_data, instance=request.user)
        #profile_form = UpdateForm(post_data, file_data, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse_lazy('view_profile'))

        context = self.get_context_data(user_form=user_form, profile_form=profile_form)

        return self.render_to_response(context)


@method_decorator(signin_required, name="dispatch")
class ViewProduct(TemplateView):
    template_name = 'productdetail.html'
    context = {}

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        product = Products.objects.get(id=id)
        reviews = Review.objects.filter(product=product)
        similar_products=Products.objects.filter(brand=product.brand,category=product.category)

        self.context['product'] = product
        self.context['reviews'] = reviews
        self.context['similar_products']=similar_products
        return render(request, self.template_name, self.context)


@signin_required
def add_to_cart(request, *args, **kwargs):
    id = kwargs['id']
    product = Products.objects.get(id=id)
    if Cart.objects.filter(product=product,user=request.user,status='ordernotplaced').exists():
        cart=Cart.objects.get(product=product,user=request.user)
        cart.quantity+=1
        cart.save()
    else:
        cart = Cart(product=product, user=request.user)
        cart.save()
        print('product added')
    return redirect('mycart')


@method_decorator(signin_required, name="dispatch")
class MyCart(TemplateView):
    template_name = 'cart.html'
    context = {}
    def get(self, request, *args, **kwargs):
        cart_products = Cart.objects.filter(user=request.user, status='ordernotplaced')
        # total = Cart.objects.filter(status="ordernotplaced", user=request.user).aggregate(Sum('product__price'))
        total=0
        for cart in cart_products:
            total+=cart.product.price*cart.quantity
        # print(total)

        self.context['cart_products'] = cart_products
        self.context['total']=total
        # self.context['cnt']=cart_count(request.user)
        return render(request, self.template_name, self.context)


@method_decorator(signin_required, name="dispatch")
class DeleteFromCart(TemplateView):
    def get(self, request, *args, **kwargs):
        id = kwargs['pk']
        cart_product = Cart.objects.get(id=id)
        cart_product.delete()
        return redirect('mycart')


def place_order(request, *args, **kwargs):
    pid = kwargs["pid"]
    product = Products.objects.get(id=pid)
    instance = {
        "product": product.product_name
    }
    form = PlaceOrderForm(initial=instance)
    context = {}
    context["form"] = form

    if request.method == "POST":
        cid = kwargs["cid"]
        cart = Cart.objects.get(id=cid)
        form = PlaceOrderForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get("address")
            product = product
            order = Orders(address=address, product=product, user=request.user)
            order.save()
            cart.status = "orderplaced"
            cart.save()
            return redirect("customer_home")

    return render(request, "placeorder.html", context)


def view_orders(request, *args, **kwargs):
    orders = Orders.objects.filter(user=request.user, status="ordered")

    context = {
        "orders": orders,
    }
    return render(request, "vieworders.html", context)


def cancel_order(request, *args, **kwargs):
    id = kwargs.get("id")
    order = Orders.objects.get(id=id)
    order.status = "cancelled"
    order.save()
    return redirect("vieworders")


class WriteReview(TemplateView):
    template_name = 'review.html'
    context = {}

    def get(self, request, *args, **kwargs):
        form = ReviewForm()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        id = kwargs['id']
        product = Products.objects.get(id=id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data.get('review')
            new_review = Review(user=request.user, product=product, review=review)
            new_review.save()
            return redirect('viewproduct', product.id)


class FilterByBrand(TemplateView):
    template_name = 'brandfilter.html'
    context={}
    def get(self, request, *args, **kwargs):
        id=kwargs['pk']
        brand=Brand.objects.get(id=id)
        brands=Brand.objects.all()
        products=Products.objects.filter(brand=brand)
        self.context['products']=products
        self.context['brands']=brands
        return render(request,self.template_name,self.context)


class BasePage(TemplateView):
    template_name = 'cust_base.html'
    context = {}

    def get(self, request, *args, **kwargs):
        brands = Brand.objects.all()
        self.context['brands'] = brands
        return render(request, self.template_name, self.context)


def cart_plus(request,*args,**kwargs):
    id=kwargs['pk']
    cart=Cart.objects.get(id=id)
    cart.quantity+=1
    cart.save()
    return redirect('mycart')

def cart_minus(request,*args,**kwargs):
    id=kwargs['pk']
    cart=Cart.objects.get(id=id)
    cart.quantity-=1
    cart.save()
    if cart.quantity<1:
        return redirect('deletecart',cart.id)
    return redirect('mycart')
