from .models import *

def calculate_room_cost(check_in, check_out, price_per_night):
    days = (check_out - check_in).days or 1
    return days * price_per_night


def update_sale_total(sale):
    items_total = sum(
        item.price * item.quantity for item in sale.items.all()
    )

    # rooms_total = sum(
    #     room.total_cost for room in sale.rooms.all()
    # )

    sale.total_amount = items_total 
    sale.save()