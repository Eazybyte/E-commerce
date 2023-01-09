from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from store.models import Product, Variation
from .models import Wishlist, WishlistItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from cart.models import Cart,CartItem



def _wishlist_id(request):
    user = request.user
    if user.is_authenticated:
        wishlist=request.user.email
    else:
        return redirect('login')
    return wishlist

def add_wishlist(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # if user is authenticated
    if current_user.is_authenticated:
        product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(
                    product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(
            wishlist_id=_wishlist_id(request)
        )
    wishlist.save()

    is_wishlist_item_exists = WishlistItem.objects.filter(
        product=product, wishlist=wishlist).exists()
    if is_wishlist_item_exists:
        wishlist_item = WishlistItem.objects.filter(product=product, wishlist=wishlist)
        ex_var_list = []
        id = []
        for item in wishlist_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in ex_var_list:
            # increase item quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = WishlistItem.objects.get(product=product, id=item_id)
            item.save()
        else:
            item = WishlistItem.objects.create(
                product=product, wishlist=wishlist)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        wishlist_item = WishlistItem.objects.create(
            product=product,
            wishlist=wishlist,
        )
        if len(product_variation) > 0:
            wishlist_item.variations.clear()
            wishlist_item.variations.add(*product_variation)
        wishlist_item.save()
    return redirect('wishlist')

    # product = Product.objects.get(id=product_id)
    # try:
    #     wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
    # except Wishlist.DoesNotExist:
    #     wishlist = Wishlist.objects.create(
    #         wishlist_id=_wishlist_id(request)
    #     )
    # wishlist.save()

    # try:
    #     wishlist_item = WishlistItem.objects.get(product=product, wishlist=wishlist)
    #     wishlist_item.save()
    # except WishlistItem.DoesNotExist:
    #     wishlist_item = WishlistItem.objects.create(
    #         product=product,
    #         wishlist=wishlist,
    #     )
    #     wishlist_item.save()
    # return redirect('wishlist')

def wishlist(request, wishlist_items=None):
    try:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist, is_active=True)
    except ObjectDoesNotExist:
        pass
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist/wishlist.html', context)

def move_to_cart(request, product_id):
    current_user = request.user
    wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
    product = Product.objects.get(id=product_id)
    wishlist_item = WishlistItem.objects.get(product=product,wishlist=wishlist)
    product_variation =list(wishlist_item.variations.all())
    try:
        is_cart_item_exists = CartItem.objects.filter(
                product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, user=current_user)
                if len(product_variation) >= 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,

            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        wishlist_item.delete()
        return redirect('cart')
    except:
        pass


def remove_wishlist_item(request, product_id,wishlist_item_id):
    wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = WishlistItem.objects.get(product=product, wishlist=wishlist, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')