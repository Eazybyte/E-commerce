from django.urls import path
from . import views 


urlpatterns = [
    path('', views.redirect_to_login),
    path('login', views.manager_login, name="manager_login"),
    path('logout', views.manager_logout, name='manager_logout'),
    path('dashboard', views.manager_dashboard, name='manager_dashboard'),
    path('manage_user', views.manage_user, name="manage_user"),
    path('manage_product/', views.manage_product, name='manage_product'),
    path('manage_category/', views.manage_category, name='manage_category'),
    path('manage_order/', views.manage_order, name='manage_order'),
    path('manage_variation/', views.manage_variation, name='manage_variation'),
    path('review_management/', views.review_management, name='review_management'),
  
    path('delete_variation/<int:variation_id>/', views.delete_variation, name='delete_variation'),
    path('update_variation/<int:variation_id>/', views.update_variation, name='update_variation'),
    path('add_variation/', views.add_variation, name='add_variation'),


    path('ban_user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('unban_user/<int:user_id>/', views.unban_user, name='unban_user'),

    path('add_product/', views.add_product, name='add_product'),  
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),

    path('add_category/', views.add_category, name='add_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name="delete_category"),

    path('admin_cancel_order/<int:order_number>/', views.cancel_order, name='admin_cancel_order'),
    path('accept_order/<int:order_number>/', views.accept_order, name='accept_order'),
    path('complete_order/<int:order_number>/', views.complete_order, name='complete_order'),

    path('change_password/', views.admin_change_password, name='admin_change_password'),
    # path('admin_orders/', views.admin_order, name='admin_orders'),

    path('review_block/<int:review_id>/', views.review_block, name="review_block"),
    path('review_unblock/<int:review_id>/', views.review_unblock, name="review_unblock"),
    path('review_delete/<int:review_id>/', views.review_delete, name="review_delete"),
]