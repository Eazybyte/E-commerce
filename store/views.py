from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from orders.models import OrderProduct
from .models import Product, ReviewRating
from category.models import Category
from store.models import Variation
from cart.models import CartItem
from django.db.models import Q
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from .forms import ReviewForm
from django.contrib import messages

from cart.views import _cart_id


# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
        }
    return render(request, 'store/store.html', context)

def filter_products(request):
    if request.method=='POST':
        color = request.POST.get('color') if 'color' in request.POST else None
        size = request.POST.get('size') if 'size' in request.POST else None
        category_slug = request.POST.get('category_slug') if 'category_slug' in request.POST else None
       
        variation2 = Variation.objects.filter(variation_value__iexact=color)
        categories = None
        products = Product.objects.none()
        products2 = Product.objects.none()
        products3 = Product.objects.none()
        if category_slug != None:
            categories = get_object_or_404(Category, slug=category_slug)
            products1 = Product.objects.filter(
                category=categories, is_available=True)
            
        else:
            products1 = Product.objects.all().filter(is_available=True).order_by('id')
    

        if color!=None and size!=None and category_slug !=None:
            variation1 = Variation.objects.filter(variation_value__iexact=size)
            variation2 = Variation.objects.filter(variation_value__iexact=color)
            temp1=Product.objects.none()
            temp=Product.objects.none()
            for i,v in enumerate(variation1):
                var=variation1[i]
                product=var.product
                temp = Product.objects.filter(id=product.id)
                temp1 = temp1.union(temp)
            products2=temp1
            temp1=Product.objects.none()
            temp=Product.objects.none()
            for i,v in enumerate(variation2):
                var=variation2[i]
                product=var.product
                temp = Product.objects.filter(id=product.id)
                temp1 = temp1.union(temp)
            products3=temp1
            products4 = products2.intersection(products3)
            
        elif color!=None and size!=None and category_slug == None:
            variation1 = Variation.objects.filter(variation_value__iexact=size)
            variation2 = Variation.objects.filter(variation_value__iexact=color)
            temp1=Product.objects.none()
            temp=Product.objects.none()
            for i,v in enumerate(variation1):
                var=variation1[i]
                product=var.product
                temp = Product.objects.filter(id=product.id)
                temp1 = temp1.union(temp)
            products2=temp1
            temp1=Product.objects.none()
            temp=Product.objects.none()
            for i,v in enumerate(variation2):
                var=variation2[i]
                product=var.product
                temp = Product.objects.filter(id=product.id)
                temp1 = temp1.union(temp)
            products3=temp1.all()
            print(products2)
            products4=products2.intersection(products3)       
        elif color!=None:
            temp1=Product.objects.none()
            temp=Product.objects.none()
            variation2 = Variation.objects.filter(variation_value__iexact=color)
            for i,v in enumerate(variation2):
                var=variation2[i]
                product=var.product
                temp = Product.objects.filter(id=product.id)
                temp1 = temp1.union(temp)
            products4=temp1.all()
        elif size!=None:
            temp1=Product.objects.none()
            temp=Product.objects.none()
            variation1 = Variation.objects.filter(variation_value__iexact=size)
            for i,v in enumerate(variation1):
                var=variation1[i]
                product=var.product
                temp = Product.objects.filter(id=product.id)
                temp1 = temp1.union(temp)
            products3=temp1.all()
        else:
            products4 = Product.objects.all().filter(is_available=True).order_by('id')


        products = products4.intersection(products1)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count
        context = {
            'products': paged_products,
            'product_count': product_count,
        }
        return render(request, 'store/store.html', context)
    else:
        return redirect('store')


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(
            request), product=single_product).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id = single_product.id).exists()

        except orderproduct.DoesNotExist:
            orderproduct = None 
    else:
        orderproduct = None 

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id = single_product.id, status=True)
    context = {
        'single_product': single_product,
        'orderproduct' : orderproduct,
        'in_cart': in_cart,
        'reviews' : reviews,
    }
    return render(request, 'store/product-detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER ')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product_id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success('Thank You! your review has been uploaded')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid:
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data, product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success('Thank You! your review has been Submitted')
                return redirect(url)
