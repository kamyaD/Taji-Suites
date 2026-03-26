
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator 


from .models import *
from .services import update_sale_total
from .forms import KitchenStockForm, LNKStockForm, ProductCreateForm, ProductStockForm, BarStockForm



def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'admin':
            return HttpResponseForbidden("Not allowed")
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    return render(request, "index.html")

@login_required(login_url='login')
@admin_required
def pos_dashboard(request):
    # Your POS logic here
    user = request.user
    if user.department == 'bar':
        products = Product.objects.filter(department='bar')
    elif user.department == 'kitchen':
        products = Product.objects.filter(department='kitchen')
    elif user.department == 'rooms':
        products = Product.objects.filter(department='rooms')
    else:
        products = Product.objects.all()
    return render(request, 'pos_dashboard.html', {'products': products})

@login_required(login_url='login')
def pos(request):
    user = request.user
    if user.department == 'bar':
        products = Product.objects.filter(department='bar')
    elif user.department == 'kitchen':
        products = Product.objects.filter(department='kitchen')
    elif user.department == 'rooms':
        products = Product.objects.filter(department='rooms')
    else:
        products = Product.objects.all()
    rooms = Room.objects.filter(is_occupied=False)

    if request.method == "POST":
        sale = Sale.objects.create()

        # Add products
        for product in products:
            qty = request.POST.get(f"product_{product.id}")
            if qty and int(qty) > 0:
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=int(qty),
                    price=product.price
                )
                product.stock -= int(qty)
                product.save()

        update_sale_total(sale)
        return redirect("receipt", sale_id=sale.id)

    return render(request, "pos.html", {
        "products": products,
        "rooms": rooms
    })



@login_required(login_url='login')
def receipt(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    return render(request, "receipt.html", {"sale": sale})



@login_required(login_url='login')
def take_stock(request):
    ProductFormSet = modelformset_factory(Product, form=ProductStockForm, extra=0)

    products = Product.objects.all()
    
    if request.method == 'POST':
        formset = ProductFormSet(request.POST, queryset=products)
        create_form = ProductCreateForm(request.POST, request.FILES)

        # ✅ Handle stock update
        if formset.is_valid():
            formset.save()
            messages.success(request, "Stock updated successfully!")

        # ✅ Handle new product creation
        if create_form.is_valid():
            create_form.save()
            messages.success(request, "New product added!")

        return redirect('take-stock')

    else:
        formset = ProductFormSet(queryset=products)
        create_form = ProductCreateForm()

    return render(request, 'take_stock.html', {
        'formset': formset,
        'create_form': create_form
    })

@login_required(login_url='login')
def bar_stock_page(request):
    form = BarStockForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('bar_stock_page')

    stocks = BarStockSheet.objects.all().order_by('-date')

    context = {
        'form': form,
        'stocks': stocks
    }
    return render(request, 'bar_stock.html', context)

@login_required(login_url='login')
def lnk_stock_page(request):
    form = LNKStockForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('lnk_stock_page')

    stocks = LNKStockSheet.objects.all().order_by('-date')

    context = {
        'form': form,
        'stocks': stocks
    }
    return render(request, 'lnk_stock.html', context)

@login_required(login_url='login')
def kitchen_stock_page(request):
    form = KitchenStockForm(request.POST or None)
    print("Kitchen Stock Form Errors:", form.errors)  # Debugging line

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('kitchen_stock_page')

    stocks = KitchenStockSheet.objects.all().order_by('-date')

    context = {
        'form': form,
        'stocks': stocks
    }
    return render(request, 'kitchen_stock.html', context)

def booking_create(request):
    if request.method == "POST":
        if len(request.POST.get("delux_number")) > 0:
            room_number = request.POST.get("delux_number")
        elif len(request.POST.get("standard_number")) > 0:
            room_number = request.POST.get("standard_number")
        elif len(request.POST.get("double_number")) > 0:
            room_number = request.POST.get("double_number")
        else:
            room_number = None 

        print("Selected Room Number:", room_number)  # Debugging line
        service = request.POST.get("service")
        room_type = request.POST.get("room_type")
        check_in = parse_date(request.POST.get("check_in"))
        check_out = parse_date(request.POST.get("check_out"))

        if service == "rooms":
            # Check if the room is already booked for the selected dates
            overlapping = RoomBooking.objects.filter(
                room_number=room_number,
                room_type=room_type,
                service="rooms",
                check_in__lt=check_out,
                check_out__gt=check_in,
            )

            if overlapping.exists():
                messages.error(request, f"Room {room_number} is already booked for these dates!")
                return redirect("home")  # Redirect back or to an error page

            # If no overlap, create the booking
            RoomBooking.objects.create(
                name=request.POST.get("name"),
                phone=request.POST.get("phone"),
                service=service,
                room_type=room_type,
                room_number=room_number,
                check_in=check_in,
                check_out=check_out,
            )
            messages.success(request, "Booking created successfully!")
            return redirect("home")
        
        
@login_required(login_url='login')
def bookings_list(request):
    bookings = RoomBooking.objects.all().order_by('-created_at')

    # Search
    q = request.GET.get('q')
    if q:
        bookings = bookings.filter(
            Q(name__icontains=q) |
            Q(phone__icontains=q) |
            Q(room_number__icontains=q)
        )

    # Filters
    service = request.GET.get('service')
    if service:
        bookings = bookings.filter(service=service)

    room_type = request.GET.get('room_type')
    if room_type:
        bookings = bookings.filter(room_type=room_type)

    check_in = request.GET.get('check_in')
    if check_in:
        bookings = bookings.filter(check_in=check_in)

    # Pagination
    paginator = Paginator(bookings, 20)  # 20 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bookings': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
    }
    return render(request, 'bookings.html', context)