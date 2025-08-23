from django.contrib import admin
from .models import *
from django.conf import settings
from django.core.mail import send_mail

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'locality', 'city', 'state', 'zipcode']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'status', 'ordered_date', 'delivery_boy']

    def save_model(self, request, obj, form, change):
        if 'delivery_boy' in form.changed_data and obj.delivery_boy:
            delivery_boy = obj.delivery_boy
            customer = obj.customer
            product = obj.product

            subject = f"New Order Assigned - Order #{obj.id}"
            message = (
                f"Hello {delivery_boy.name},\n\n"
                f"You have been assigned a new order.\n\n"
                f"Order ID: {obj.id}\n"
                f"Product: {product.title}\n"
                f"Quantity: {obj.quantity}\n"
                f"Customer: {customer.user.get_full_name()} ({customer.user.email})\n"
                f"Address: {customer.locality}, {customer.city}, {customer.state} - {customer.zipcode}\n"
                f"Order Date: {obj.ordered_date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Please proceed with the delivery.\n\n"
                f"Thanks,\nYour Store Team"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [delivery_boy.email], fail_silently=False)

        super().save_model(request, obj, form, change)

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'selling_price', 'discounted_price', 'description', 'composition', 'prodapp', 'category', 'product_image', 'average_rating']

@admin.register(Review)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'review_text', 'created_at']

@admin.register(DeliveryBoy)
class DeliveryBoyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity']
    search_fields = ['product__title']