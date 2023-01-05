from django.urls import path
from . import views

urlpatterns = [
    path('place_order',views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('status/', views.payment_status, name='payment_status'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),
    # path('cod/', views.cod, name='cod'),

     path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('user_cancel_order/<int:order_number>/', views.user_cancel_order, name='user_cancel_order'),
     ]