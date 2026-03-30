
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum,Q
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.db import transaction
from urllib3 import request 


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
        products = BarStockSheet.objects.filter(department='bar')
    elif user.department == 'kitchen':
        products = KitchenStockSheet.objects.filter(department='kitchen')
    elif user.department == 'rooms':
        products = LNKStockSheet.objects.filter(department='rooms')
    else:
        return HttpResponseForbidden("Invalid department")
    return render(request, 'pos_dashboard.html', {'products': products})

@login_required(login_url='login')
def pos(request):
    user = request.user

    today = timezone.now().date()
    if user.department == 'bar':
        products = BarStockSheet.objects.filter(opening_stock__gt=0, date=today)
        all_dates = BarStockSheet.objects.values_list('date', flat=True)
    elif user.department == 'kitchen':
        products = KitchenStockSheet.objects.filter(opening_stock__gt=0, date=today)
    elif user.department == 'rooms':
        products = LNKStockSheet.objects.filter(opening_stock__gt=0, date=today)
    else:
        return HttpResponseForbidden("Invalid department")

    rooms = Room.objects.filter(is_occupied=False)
    for product in products:
        print(f"Product: {product.date}, Opening Stock: {product.opening_stock}")  # Debugging line

    if request.method == "POST":
        with transaction.atomic():
            sale = Sale.objects.create()

            for product in products:
                qty = request.POST.get(f"product_{product.id}")
                

                try:
                    qty = int(qty)
                except (TypeError, ValueError):
                    continue

                if qty <= 0:
                    continue

                if product.opening_stock < qty:
                    return HttpResponse(f"Not enough stock for {product.item}")

                content_type = ContentType.objects.get_for_model(product)

                SaleItem.objects.create(
                    sale=sale,
                    content_type=content_type,
                    object_id=product.id,
                    quantity=qty,
                    price=product.rate
                )

                product.closing_stock-= qty
                product.sold += qty
                product.user = request.user

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
    view = request.GET.get('view', 'stock')
    form = BarStockForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('bar_stock_page')

    search_query = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    stocks_qs = BarStockSheet.objects.all().order_by('-date')

    # 🔹 Filters
    if search_query:
        stocks_qs = stocks_qs.filter(item__icontains=search_query)

    if view == 'reports' and start_date and end_date:
        stocks_qs = stocks_qs.filter(date__range=[start_date, end_date])
    
    users = User.objects.all()
    # 🔹 REPORT DATA
    report_summary = None
    user_summary = None

    if view == 'reports':
        user_id = request.GET.get('user')
        if user_id:
            stocks_qs = stocks_qs.filter(user_id=user_id)

        report_summary = stocks_qs.aggregate(
            total_sales=Sum('amount'),
            total_profit=Sum('profit'),
            total_items_sold=Sum('sold')
        )

        user_summary = stocks_qs.values('user__username').annotate(
            total_sales=Sum('amount'),
            total_profit=Sum('profit'),
            total_items_sold=Sum('sold')
        ).order_by('-total_sales')

        stocks = stocks_qs  # no pagination

    else:
        paginator = Paginator(stocks_qs, 10)
        page_number = request.GET.get('page')
        stocks = paginator.get_page(page_number)

    context = {
        'form': form,
        'stocks': stocks,
        'view': view,
        'report_summary': report_summary,
        'user_summary': user_summary,
        'users':users
    }

    return render(request, 'bar_stock.html', context)

@login_required(login_url='login')
def edit_bar_stock(request, stock_id):
    stock = get_object_or_404(BarStockSheet, id=stock_id)
    print("opening_stock:", int(request.POST.get('opening_stock')))  # Debugging line
    
    if request.method == "POST":
        stock.item = request.POST.get('item')
        stock.category = request.POST.get('category')
        stock.opening_stock = int(request.POST.get('opening_stock'))
        stock.add = int(request.POST.get('add'))
        stock.sold = int(request.POST.get('sold'))
        stock.rate = float(request.POST.get('rate'))
        stock.unit_cost = float(request.POST.get('unit_cost')) if request.POST.get('unit_cost') else 0.0
        # stock.date = request.POST.get('date')

        stock.save()
        return redirect('bar_stock_page')  # 👈 change to your URL name

    return redirect('bar_stock_page')

@login_required(login_url='login')
def delete_bar_stock(request, stock_id):
    stock = get_object_or_404(BarStockSheet, id=stock_id)

    stock.delete()
    messages.success(request, "Record deleted successfully!")

    return redirect('bar_stock_page')


@login_required(login_url='login')
def generate_today_bar_stock(request):
    if request.method == "POST":
        today = timezone.now().date()
        # today = '2026-03-29'
        # print("today:", today)  # Debugging line

        # 🔹 Get latest stock per item (yesterday or last available)
        latest_stocks = []
        items = BarStockSheet.objects.values_list('item', flat=True).distinct()

        for item in items:
            latest = BarStockSheet.objects.filter(item=item).order_by('-date').first()
            if latest:
                latest_stocks.append(latest)

        created_count = 0

        for stock in latest_stocks:
            # Check if today's record already exists
            exists = BarStockSheet.objects.filter(
                item=stock.item,
                date=today
            ).exists()

            if not exists:
                BarStockSheet.objects.create(
                    item=stock.item,
                    category=stock.category,
                    opening_stock=stock.closing_stock,
                    add=0,
                    sold=0,
                    rate=stock.rate,
                    unit_cost=stock.unit_cost,
                    date=today
                )
                created_count += 1

        messages.success(request, f"✅ {created_count} stock records generated for today!")
        return redirect('bar_stock_page')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('bar_stock_page')
    
@login_required(login_url='login')
def bar_reports(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    records = BarStockSheet.objects.all()

    # 🔹 Filter by date range
    if start_date and end_date:
        records = records.filter(date__range=[start_date, end_date])

    # 🔹 Aggregations
    summary = records.aggregate(
        total_sales=Sum('amount'),
        total_profit=Sum('profit'),
        total_items_sold=Sum('sold'),
        total_stock=Sum('closing_stock')
    )

    context = {
        'records': records,
        'summary': summary,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'bar/reports.html', context)

@login_required(login_url='login')
def lnk_stock_page(request):
    form = LNKStockForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('lnk_stock_page')

    search_query = request.GET.get('q', '')
    today = timezone.now().date()

    stocks = LNKStockSheet.objects.all().order_by('-date')
    if search_query:
        stocks = stocks.filter(item__icontains=search_query)

    stocks = stocks.order_by('-date')

    # 🔹 PAGINATION
    paginator = Paginator(stocks, 10)  # 10 records per page
    page_number = request.GET.get('page')
    stocks = paginator.get_page(page_number)

    context = {
        'form': form,
        'stocks': stocks
    }
    return render(request, 'lnk_stock.html', context)

@login_required(login_url='login')
def edit_lnk_stock(request, stock_id):
    stock = get_object_or_404(LNKStockSheet, id=stock_id)

    if request.method == "POST":
        stock.item = request.POST.get('item')
        stock.opening_stock = int(request.POST.get('opening_stock'))
        stock.add = int(request.POST.get('add'))
        stock.sold = int(request.POST.get('sold'))
        stock.rate = float(request.POST.get('rate'))
        stock.date = request.POST.get('date')

        stock.save()
        return redirect('lnk_stock_page')  # 👈 change to your URL name

    return redirect('lnk_stock_page')

@login_required(login_url='login')
def delete_lnk_stock(request, stock_id):
    stock = get_object_or_404(LNKStockSheet, id=stock_id)

    stock.delete()
    messages.success(request, "Record deleted successfully!")

    return redirect('lnk_stock_page')

@login_required(login_url='login')
def generate_today_lnk_stock(request):
    if request.method == "POST":
        # today = timezone.now().date()
        today = '2026-03-28'
        # print("today:", today)  # Debugging line

        # 🔹 Get latest stock per item (yesterday or last available)
        latest_stocks = []
        items = LNKStockSheet.objects.values_list('item', flat=True).distinct()

        for item in items:
            latest = LNKStockSheet.objects.filter(item=item).order_by('-date').first()
            if latest:
                latest_stocks.append(latest)

        created_count = 0

        for stock in latest_stocks:
            # Check if today's record already exists
            exists = LNKStockSheet.objects.filter(
                item=stock.item,
                date=today
            ).exists()

            if not exists:
                LNKStockSheet.objects.create(
                    item=stock.item,
                    opening_stock=stock.closing_stock,
                    add=0,
                    sold=0,
                    rate=stock.rate,
                    date=today
                )
                created_count += 1

        messages.success(request, f"✅ {created_count} stock records generated for today!")
        return redirect('lnk_stock_page')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('lnk_stock_page')




@login_required(login_url='login')
def kitchen_stock_page(request):
    form = KitchenStockForm(request.POST or None)
    print("Kitchen Stock Form Errors:", form.errors)  # Debugging line

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('kitchen_stock_page')
    
     # 🔹 Search + Filter FIRST
    search_query = request.GET.get('q', '')
    today = timezone.now().date()

    stocks = KitchenStockSheet.objects.all().order_by('-date')
    if search_query:
        stocks = stocks.filter(item__icontains=search_query)

    stocks = stocks.order_by('-date')
    # 🔹 PAGINATION
    paginator = Paginator(stocks, 10)  # 10 records per page
    page_number = request.GET.get('page')
    stocks = paginator.get_page(page_number)

    

    context = {
        'form': form,
        'stocks': stocks
    }
    return render(request, 'kitchen_stock.html', context)

@login_required(login_url='login')
def edit_kitchen_stock(request, stock_id):
    stock = get_object_or_404(KitchenStockSheet, id=stock_id)

    if request.method == "POST":
        stock.item = request.POST.get('item')
        stock.opening_stock = int(request.POST.get('opening_stock'))
        stock.add = int(request.POST.get('add'))
        stock.sold = int(request.POST.get('sold'))
        stock.rate = float(request.POST.get('rate'))
        stock.date = request.POST.get('date')

        stock.save()
        return redirect('kitchen_stock_page')  # 👈 change to your URL name

    return redirect('kitchen_stock_page')

@login_required(login_url='login')
def delete_kitchen_stock(request, stock_id):
    stock = get_object_or_404(KitchenStockSheet, id=stock_id)

    stock.delete()
    messages.success(request, "Record deleted successfully!")

    return redirect('kitchen_stock_page')

@login_required(login_url='login')
def generate_today_kitchen_stock(request):
    if request.method == "POST":
        today = timezone.now().date()
        # today = '2027-04-01'
        # print("today:", today)  # Debugging line

        # 🔹 Get latest stock per item (yesterday or last available)
        latest_stocks = []
        items = KitchenStockSheet.objects.values_list('item', flat=True).distinct()

        for item in items:
            latest = KitchenStockSheet.objects.filter(item=item).order_by('-date').first()
            if latest:
                latest_stocks.append(latest)

        created_count = 0

        for stock in latest_stocks:
            # Check if today's record already exists
            exists = KitchenStockSheet.objects.filter(
                item=stock.item,
                date=today
            ).exists()

            if not exists:
                KitchenStockSheet.objects.create(
                    item=stock.item,
                    opening_stock=stock.closing_stock,
                    add=0,
                    sold=0,
                    rate=stock.rate,
                    date=today
                )
                created_count += 1

        messages.success(request, f"✅ {created_count} stock records generated for today!")
        return redirect('kitchen_stock_page')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('kitchen_stock_page')


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