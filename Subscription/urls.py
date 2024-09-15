from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscription_success/', views.order_success, name='subscription_success'),
    path('pay/', views.subscribe, name='subscription_pay'),
    path('processed_callback/', views.processed_callback, name='processed_callback'),
    path('order_success/', views.order_success, name='order_success'),

]
