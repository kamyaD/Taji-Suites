from django.contrib import admin
from django.utils.timezone import localtime


from .models import *

# -------------------
# CUSTOMER ADMIN
# -------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone')
    search_fields = ('name', 'phone')


# -------------------
# PRODUCT ADMIN
# -------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department','location', 'category', 'price', 'stock')
    list_filter = ('category','department','location')
    search_fields = ('name',)



@admin.register(BarStockSheet)
class BarStockSheetAdmin(admin.ModelAdmin):
    list_display = ('item', 'opening_stock','add','total','closing_stock', 'sold','rate','amount','unit_cost', 'profit','date',)
    readonly_fields = ('total', 'closing_stock', 'amount', 'profit')
    list_filter = ('category', 'date')
    search_fields = ('item',)

@admin.register(LNKStockSheet)
class LNKStockSheetAdmin(admin.ModelAdmin):
    list_display = ('item', 'opening_stock','add','total','closing_stock', 'sold','rate','amount','date',)
    readonly_fields = ('total', 'closing_stock', 'amount')
    list_filter = ('item','date')
    search_fields = ('item',)

@admin.register(KitchenStockSheet)
class KitchenStockSheetAdmin(admin.ModelAdmin):
    list_display = ('item', 'opening_stock','add','total','closing_stock', 'sold','rate','amount','date',)
    readonly_fields = ('total', 'closing_stock', 'amount')
    list_filter = ('item','date')
    search_fields = ('item',)


# -------------------
# ROOM ADMIN
# -------------------
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_number', 'room_type', 'price_per_night', 'is_occupied')
    list_filter = ('room_type', 'is_occupied')
    search_fields = ('room_number',)


# -------------------
# SALE ITEM INLINE
# -------------------
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


# -------------------
# ROOM BOOKING INLINE
# -------------------
# class RoomBookingInline(admin.TabularInline):
#     model = RoomBooking
#     extra = 0


# -------------------
# SALE ADMIN
# -------------------
# @admin.register(Sale)
# class SaleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer', 'date', 'total_amount')
#     list_filter = ('date',)
#     search_fields = ('id',)

#     inlines = [SaleItemInline, RoomBookingInline]


# -------------------
# SALE ITEM ADMIN
# -------------------
@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'product', 'quantity', 'price')
    list_filter = ('product',)
    search_fields = ('sale__id',)


# -------------------
# ROOM BOOKING ADMIN
# -------------------
# @admin.register(RoomBooking)
# class RoomBookingAdmin(admin.ModelAdmin):
#     list_display = ('id', 'sale', 'room', 'check_in', 'check_out', 'total_cost')
#     list_filter = ('room',)
#     search_fields = ('sale__id',)




@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'phone',
        'service',
        'room_type',
        'room_number',
        'check_in',
        'check_out',
        'created_at_formatted'
    )

    search_fields = ('name', 'phone', 'room_number')

    list_filter = (
        'service',
        'room_type',
        'check_in',
        'created_at'
    )

    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

    list_per_page = 20

    fieldsets = (
        ('Customer Info', {
            'fields': ('name', 'phone')
        }),
        ('Booking Details', {
            'fields': ('service', 'room_type', 'room_number')
        }),
        ('Stay Details', {
            'fields': ('check_in', 'check_out')
        }),
        ('System Info', {
            'fields': ('created_at',)
        }),
    )

    def created_at_formatted(self, obj):
        return localtime(obj.created_at).strftime("%Y-%m-%d %H:%M")

    created_at_formatted.short_description = "Booked At"