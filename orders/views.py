import datetime
from django.shortcuts import render, redirect
from cart.models import CartItem 
from store.models import Product
from .forms import OrderForm
from .models import Order,Payment, OrderProduct

import razorpay
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib import messages


# Create your views here.

@login_required(login_url='login')
def payments(request, total = 0):
    current_user = request.user
    cart_item = CartItem.objects.filter(user=current_user)

    delivery = 0
    grand_total = 0
    
    for item in cart_item:
        total += (item.product.price * item.quantity)
        
    if total <=  999:
        delivery = 80
    else:
        delivery = 0
    grand_total = total + delivery
    
    order_number = request.session['order_number']
    order = Order.objects.get(user=current_user, is_ordered=False,order_number = order_number)

    currency = 'INR'
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

    response_payment  = razorpay_client.order.create(dict(amount=int(grand_total) * 100,currency=currency))
    order_id = response_payment['id']
    order_status = response_payment['status']
    if order_status == 'created':
        payDetails = Payment(
            user = current_user,
            order_id = order_id,
            order_number = order_number,
            amount_paid = grand_total 
        )
        payDetails.save()

    context = {
        'order': order,
        'cart_items': cart_item,
        'total': total,
        'delivery': delivery,
        'grand_total': grand_total,
        
        'payment': response_payment,
        'razorpay_merchant_key':settings.RAZOR_KEY_ID,
        'grand_total': grand_total,
    }
    return render(request, 'orders/payments.html', context)

def place_order(request, total=0, quantity=0):
    current_user = request.user

    # if the cart is less than or equal to 0, then redirect back to shop

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0 :
        return redirect('store')
    

    
    delivery = 0
    grand_total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    if total <=  999:
        delivery = 80
    else:
        delivery = 0
    grand_total = total + delivery

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_total =  grand_total
            data.delivery = delivery
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date+str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            request.session['order_number'] = order_number
            return redirect('payments')
    else:
        return redirect('checkout')

    
def payment_success(request):
    order_number = request.session['order_number']
    transaction_id = Payment.objects.get(order_number=order_number)
  
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        
        # Change order status to Accepted when order is success
        order.status = 'Order Accepted' 
        order.save()
        
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        delivery = 0
        total = 0
        grand_total = 0
        
        for item in ordered_products:
            total += (item.product_price * item.quantity)
        
        if total <=  999:
            delivery = 80
        else:
            delivery = 0
        grand_total = total + delivery
        
        #Order Confirmmation Mail
        
        current_site = get_current_site(request)
        mail_subject = "Order Confirmation"
        message = render_to_string('orders/order_confirmation.html', {
        'order': order,
        'domain': current_site
        })
        to_mail = order.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_mail])
        send_email.send()
        messages.success(request, 'Order confirmation mail has been send to your registered email address')

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'transaction_id': transaction_id,
            'total': total,
            'delivery': delivery,
            'grand_total': grand_total
        }
        
        return render(request, 'orders/success.html', context)
    
    except Exception as e:
        raise e

def payment_fail(request):
  return render(request, 'orders/fail.html')





@csrf_exempt
def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    } 
    

    # authorize razorpay client with API Keys.
    razorpay_client = razorpay.Client(
      auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    client = razorpay_client

    try:
        status = client.utility.verify_payment_signature(params_dict)
        transaction = Payment.objects.get(order_id=response['razorpay_order_id'])
        transaction.status = status
        transaction.payment_id = response['razorpay_payment_id']
        transaction.save()

        # get order number
        order_number = transaction.order_number
        order = Order.objects.get(is_ordered=False, order_number=order_number)

        order.payment = transaction
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=order.user)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = transaction
            order_product.user_id = order.user.id
            order_product.product_id = item.product_id
            order_product.quantity = item.quantity 
            order_product.product_price = item.product.price
            order_product.ordered = True
            
            order_product.save()

            # Reducing Stock
            product = Product.objects.get(id=item.product_id)   
            product.stock -= item.quantity
            product.save()

            #  Clearing Cart Items
            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            order_product.variation.set(product_variation)
            order_product.save()
        
        CartItem.objects.filter(user=order.user).delete()

        return redirect('payment_success')

    except Exception as e:
        transaction = Payment.objects.get(order_id=response['razorpay_order_id'])
        transaction.delete()
        return redirect('payment_fail')
        
def payment_fail(request):
  return render(request, 'orders/fail.html')


@login_required(login_url ='login')
def my_orders(request): 
    order = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context ={
        'orders':  order,
    }
    return render(request, 'orders/my_orders.html', context)

@login_required(login_url='login')
def user_cancel_order(request, order_number):
    current_user = request.user
    order = Order.objects.get(user=current_user, is_ordered=True,order_number = order_number)
    payment=Payment.objects.get(order_number=order_number)
    currency = 'INR'
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    amount= float(payment.amount_paid)
    print(amount)
    payment_id = payment.payment_id
    refund = razorpay_client.payment.refund(payment_id,dict(amount=int(amount)*100))
    print((refund))
    current_user = request.user
    order = Order.objects.get(user=current_user, is_ordered=True,order_number = order_number)
    payment=Payment.objects.get(order_number=order_number)
    currency = 'INR'
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    amount= float(payment.amount_paid)
    print(amount)
    payment_id = payment.payment_id
    refund = razorpay_client.payment.refund(payment_id,dict(amount=int(amount)*100))
    print((refund))
    order.status = 'Order Cancelled'
    order.save()

    return render(request, 'orders/cancel_order.html')

@login_required(login_url ='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        
    }
    return render(request, 'orders/order_detail.html', context)