from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('pos/', pos, name='pos'),
    path('receipt/<int:sale_id>/', receipt, name='receipt'),
    path('take-stock/', take_stock, name='take-stock'),
    path('booking-create/', booking_create, name='booking-create'),
    path('booking-list/', bookings_list, name='booking-list'),
    path('bar-stock/', bar_stock_page, name='bar_stock_page'),
    path('lnk-stock/', lnk_stock_page, name='lnk_stock_page'),
    path('kitchen-stock/', kitchen_stock_page, name='kitchen_stock_page'),
    # path('mpesa/callback/', mpesa_callback, name='mpesa-callback'),
]