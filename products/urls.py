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
    path('edit-bar-stock/<int:stock_id>/', edit_bar_stock, name='edit_bar_stock'),
    path('edit-lnk-stock/<int:stock_id>/', edit_lnk_stock, name='edit_lnk_stock'),
    path('edit-kitchen-stock/<int:stock_id>/', edit_kitchen_stock, name='edit_kitchen_stock'),
    path('delete-kitchen-stock/<int:stock_id>/', delete_kitchen_stock, name='delete_kitchen_stock'),
    path('delete-lnk-stock/<int:stock_id>/', delete_lnk_stock, name='delete_lnk_stock'),
    path('delete-bar-stock/<int:stock_id>/', delete_bar_stock, name='delete_bar_stock'),
    path('generate-bar-stock/', generate_today_bar_stock, name='generate_bar_stock'),
    path('generate-kitchen-stock/', generate_today_kitchen_stock, name='generate_kitchen_stock'),
    path('generate-lnk-stock/', generate_today_lnk_stock, name='generate_lnk_stock'),
    path('bar-reports/', bar_reports, name='bar_reports'),

    # path('mpesa/callback/', mpesa_callback, name='mpesa-callback'),
]