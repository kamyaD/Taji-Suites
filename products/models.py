from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from user.models import User

# Create your models here.

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('beer', 'Beer'),
        ('whisky', 'Whisky'),
        ('wine', 'Wine'),
        ('vodka', 'Vodka'),
        ('rum', 'Rum'),
        ('tequila', 'Tequila'),
        ('gin', 'Gin'),
        ('non-alcoholic', 'Non-Alcoholic'),
        ('food', 'Food'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    department = models.CharField(max_length=20, choices=[('lnk', 'LNK'),('bar', 'Bar'), ('kitchen', 'Kitchen'), ('rooms', 'Rooms'),('all', 'All')], default='kitchen')
    location = models.CharField(max_length=100, choices=[('kisumu', 'Kisumu'),('kakamega', 'Kakamega'),('all','All')],default='kisumu')  # e.g., "Bar Counter", "Kitchen Shelf A"
    image = models.ImageField(upload_to='products/', blank=True, null=True)


class BarStockSheet(models.Model):
    CATEGORY_CHOICES = [
        ('beer', 'Beers'),
        ('cans', 'Cans'),
        ('whiskeys', 'Whiskeys'),
        ('brandies', 'Brandies'),
        ('vodka', 'Vodka'),
        ('gin', 'Gin'),
        ('rum', 'Rum'),
        ('liquers', 'Liquers'),
        ('wines', 'Wines'),
        ('soft drinks', 'Soft Drinks'),
        ('shots/tots', 'Shots/Tots'),
        ('ciders/others', 'Ciders/Others')
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    item = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    opening_stock = models.IntegerField(blank=True, null=True, default=0)
    add = models.IntegerField(blank=True, null=True, default=0)
    total = models.IntegerField(editable=False, null=True, blank=True)
    closing_stock = models.IntegerField(editable=False, null=True, blank=True)
    sold = models.IntegerField(default=0)
    rate = models.FloatField(default=0.0)
    amount = models.FloatField(editable=False, null=True, blank=True)
    unit_cost = models.FloatField(default=0.0)
    sales_cost = models.FloatField(editable=False, null=True, blank=True)
    profit = models.FloatField(editable=False, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    department = models.CharField(max_length=20, choices=[('bar', 'Bar')], default='bar')
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    class Meta:
        unique_together = ('item', 'date')
        ordering = ['-date']

    def clean(self):
        # Prevent negative or invalid stock
        if self.sold < 0:
            raise ValidationError("Sold cannot be negative")

    def save(self, *args, **kwargs):

        # 🔹 Get previous record
        previous = BarStockSheet.objects.filter(
            item=self.item,
            date__lt=self.date
        ).order_by('-date').first()

        # 🔹 Opening stock logic
        if previous:
            self.opening_stock = previous.closing_stock
        elif self.opening_stock is None:
            self.opening_stock = 0

        # 🔹 Normalize values (VERY IMPORTANT)
        add_value = self.add if self.add else 0
        sold_value = self.sold if self.sold else 0
        rate_value = self.rate if self.rate else 0

        # 🔹 Total stock
        self.total = self.opening_stock + add_value

        # 🔹 Validation
        if sold_value > self.total:
            raise ValidationError("Sold cannot be greater than total stock")

        # 🔹 Closing stock
        self.closing_stock = self.total - sold_value

        # 🔹 Amount
        self.amount = sold_value * rate_value

        # (Optional future)
        # sales_cost = sold_value * (self.unit_cost or 0)
        # self.profit = self.amount - sales_cost

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item} - {self.date}"
    
class LNKStockSheet(models.Model):
    item = models.CharField(max_length=100)
    opening_stock = models.IntegerField(blank=True, null=True)
    add = models.IntegerField(blank=True, null=True, default=0)
    total = models.IntegerField(editable=False, null=True, blank=True)
    closing_stock = models.IntegerField(editable=False, null=True, blank=True)
    sold = models.IntegerField(default=0)
    rate = models.FloatField(default=0.0)
    amount = models.FloatField(editable=False, null=True, blank=True)
    # unit_cost = models.FloatField(default=0.0)
    sales_cost = models.FloatField(editable=False, null=True, blank=True)
    # profit = models.FloatField(editable=False, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    department = models.CharField(max_length=20, choices=[('lnk', 'LNK')], default='lnk')
    image = models.ImageField(upload_to='products/', blank=True, null=True)


    class Meta:
        unique_together = ('item', 'date')
        ordering = ['-date']

    def clean(self):
        # Prevent negative or invalid stock
        if self.sold < 0:
            raise ValidationError("Sold cannot be negative")

    def save(self, *args, **kwargs):

        # 🔹 Get previous record
        previous = LNKStockSheet.objects.filter(
            item=self.item,
            date__lt=self.date
        ).order_by('-date').first()

        # 🔹 Opening stock logic
        if previous:
            self.opening_stock = previous.closing_stock
        elif self.opening_stock is None:
            self.opening_stock = 0

        # 🔹 Normalize values (VERY IMPORTANT)
        add_value = self.add if self.add else 0
        sold_value = self.sold if self.sold else 0
        rate_value = self.rate if self.rate else 0

        # 🔹 Total stock
        self.total = self.opening_stock + add_value

        # 🔹 Validation
        if sold_value > self.total:
            raise ValidationError("Sold cannot be greater than total stock")

        # 🔹 Closing stock
        self.closing_stock = self.total - sold_value

        # 🔹 Amount
        self.amount = sold_value * rate_value

        # (Optional future)
        # sales_cost = sold_value * (self.unit_cost or 0)
        # self.profit = self.amount - sales_cost

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item} - {self.date}"
    
class KitchenStockSheet(models.Model):
    item = models.CharField(max_length=100)
    opening_stock = models.IntegerField(blank=True, null=True)
    add = models.IntegerField(blank=True, null=True, default=0)
    total = models.IntegerField(editable=False, null=True, blank=True)
    closing_stock = models.IntegerField(editable=False, null=True, blank=True)
    sold = models.IntegerField(default=0)
    rate = models.FloatField(default=0.0)
    amount = models.FloatField(editable=False, null=True, blank=True)
    # unit_cost = models.FloatField(default=0.0)
    sales_cost = models.FloatField(editable=False, null=True, blank=True)
    # profit = models.FloatField(editable=False, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    department = models.CharField(max_length=20, choices=[('kitchen', 'Kitchen')], default='kitchen')
    image = models.ImageField(upload_to='products/', blank=True, null=True)


    class Meta:
        unique_together = ('item', 'date')
        ordering = ['-date']

    def clean(self):
        # Prevent negative or invalid stock
        if self.sold < 0:
            raise ValidationError("Sold cannot be negative")


    def save(self, *args, **kwargs):

        # 🔹 Get previous record
        previous = KitchenStockSheet.objects.filter(
            item=self.item,
            date__lt=self.date
        ).order_by('-date').first()

        # 🔹 Opening stock logic
        if previous:
            self.opening_stock = previous.closing_stock
        elif self.opening_stock is None:
            self.opening_stock = 0

        # 🔹 Normalize values (VERY IMPORTANT)
        add_value = self.add if self.add else 0
        sold_value = self.sold if self.sold else 0
        rate_value = self.rate if self.rate else 0

        # 🔹 Total stock
        self.total = self.opening_stock + add_value

        # 🔹 Validation
        if sold_value > self.total:
            raise ValidationError("Sold cannot be greater than total stock")

        # 🔹 Closing stock
        self.closing_stock = self.total - sold_value

        # 🔹 Amount
        self.amount = sold_value * rate_value

        # (Optional future)
        # sales_cost = sold_value * (self.unit_cost or 0)
        # self.profit = self.amount - sales_cost

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item} - {self.date}"







class Room(models.Model):
    ROOM_NUMBER_CHOICES = [
        ('101', '101'),
        ('102', '102'),
        ('103', '103'),
        ('104', '104'),
        ('105', '105'),
        ('201', '201'),
        ('202', '202'),
        ('203', '203'),
        ('204', '204'),
        ('205', '205'),
    ]

    ROOM_TYPE_CHOICES = [
        ('delux', 'Deluxe'),
        ('standard', 'Standard'),
        ('double', 'Double'),
    ]

    
    room_number = models.CharField(max_length=10, choices=ROOM_NUMBER_CHOICES)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_occupied = models.BooleanField(default=False)


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)


class Sale(models.Model):
    sales_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    department = models.CharField(max_length=20, choices=[('bar', 'Bar'), ('lnk', 'LNK'), ('kitchen', 'Kitchen'), ('rooms', 'Rooms')], default='bar')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')



class SaleItem(models.Model):
    sale = models.ForeignKey(
        'Sale',
        on_delete=models.CASCADE,
        related_name='items'   # ✅ THIS IS REQUIRED
    )

    # Generic relation
    department = models.CharField(max_length=20, choices=[('bar', 'Bar'), ('lnk', 'LNK'), ('kitchen', 'Kitchen'), ('rooms', 'Rooms')], default='bar')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True,blank=True)
    product = GenericForeignKey('content_type', 'object_id')

    quantity = models.IntegerField(null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price
    

class RoomBooking(models.Model):
    SERVICE_CHOICES = [
        ('rooms', 'Rooms'),
        ('bar', 'Bar'),
        ('conference', 'Conference'),
        ('roof_top', 'Roof Top'),
        ('office_delivery', 'Office Delivery'),
    ]

    ROOM_TYPE_CHOICES = [
        ('deluxe', 'Deluxe Room'),
        ('double', 'Double Room'),
        ('standard', 'Standard Room'),
    ]

    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20 , blank=True, null=True)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, blank=True, null=True)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    check_in = models.DateField(blank=True, null=True)
    check_out = models.DateField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid")],
        default="pending"
    )

    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)

    date = models.DateField(blank=True, null=True)  # for other services
    created_at = models.DateTimeField(default=timezone.now)