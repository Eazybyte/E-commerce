from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),

    path('',views.dashboard,name='dashboard'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),

    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path("forgotPassword/", views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validator/<uidb64>/<token>/',views.resetpassword_validator,name='resetpassword_validator'),
    path("resetPassword/", views.resetPassword, name='resetPassword'),

    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('user_cancel_order/<int:order_number>/', views.user_cancel_order, name='user_cancel_order'),
]