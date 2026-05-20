from django.urls import path
from .import views

urlpatterns=[
    path('loginpage/',views.loginpage,name='loginpage'),
    path('logoutpage',views.logoutpage,name='logoutpage'),
    path('registrationpage',views.registrationpage,name='registarionpage'),
    
    path('',views.Home,name='home'),
    path('product',views.Prod,name='product'),
#   path('customer',views.cust,name='customer'),
    path('customer/<int:pk_test>',views.cust,name='customer'),
    path('customer_list',views.Customer_list,name='customer_list'),
    path('place_order/<int:pk>',views.place_order,name='place_order'),
    path('create_order/',views.create_order,name='create_order'),
#    path('update_order/<int:pk>',views.update_order,name='update_order'),
    path('updateorder/<int:pk>',views.updateorder,name='updateorder'),
    path('deleteorder/<int:pk>',views.deleteorder,name='deleteorder'),
    path('order_list',views.order_list,name='order_list'),
    path('create_customer',views.create_customer,name='create_customer'),
    path('update_customer/<int:pk>',views.update_Customer,name='update_customer'),
    path('delete_customer/<int:pk>',views.delete_customer,name='delete_customer'),
    path('add_product',views.add_product,name='add_product'),
    path('update_product/<int:pk>',views.update_product,name='update_product'),
    path('delete_product/<int:pk>',views.deleteproduct,name='deleteproduct'),
    path('analytics/',views.analytics,name='analytics'),
    path('tag_list/',views.tag_list,name='tag_list'),
    path('import_csv',views.import_tag_csv,name='import_csv'),
]