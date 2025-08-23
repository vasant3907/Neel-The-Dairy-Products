from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
import stripe
import logging
from django.db import transaction
from django.db.models import F

from .models import *
from .serializers import *
from .pagination import ProductPagination

# Configure logging
logger = logging.getLogger(__name__)

# Authentication APIs
class RegisterAPI(APIView):
    def post(self, request):
        # Basic user fields
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Customer fields
        name = request.data.get('name')
        locality = request.data.get('locality')
        city = request.data.get('city')
        mobile = request.data.get('mobile')
        zipcode = request.data.get('zipcode')
        state = request.data.get('state')

        # Validate required user fields
        if not username or not password or not email:
            return Response({'error': 'Username, password, and email are required.'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Validate required customer fields
        if not all([name, locality, city, mobile, zipcode, state]):
            return Response({'error': 'All customer details are required.'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken.'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )

            # Create associated customer
            customer = Customer.objects.create(
                user=user,
                name=name,
                locality=locality,
                city=city,
                mobile=mobile,
                zipcode=zipcode,
                state=state
            )

            # Generate token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'message': 'User registered successfully.',
                'token': token.key,
                'user_id': user.id,
                'customer_id': customer.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # If something goes wrong, delete the user if it was created
            if 'user' in locals():
                user.delete()
            logger.error(f"Registration error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Both username and password are required.'}, 
                           status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful.',
                'token': token.key,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, 
                           status=status.HTTP_401_UNAUTHORIZED)


class HomeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': f'Welcome, {request.user.username}!'}, 
                       status=status.HTTP_200_OK)


# Product APIs
class ProductListCreateAPI(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']


class ProductRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# Customer APIs
class CustomerListCreateAPI(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomerRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)


# Cart APIs
class CartListCreateAPI(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


# Payment APIs
class PaymentListCreateAPI(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


# Order APIs
class OrderPlacedListCreateAPI(generics.ListCreateAPIView):
    serializer_class = OrderPlacedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderPlaced.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            order = serializer.save(user=self.request.user)
            
            # Lock the stock row for update
            product = Product.objects.get(id=order.product.id)
            stock = Stock.objects.select_for_update().get(product=product)

            if stock.quantity < order.quantity:
                raise ValueError("Insufficient stock available.")
            
            stock.quantity = F('quantity') - order.quantity
            stock.save()
            stock.refresh_from_db()
            
            self.send_order_notification_email(order)
            return order

    
    def send_order_notification_email(self, order):
        """Send email notification to admin when an order is placed."""
        try:
            customer = Customer.objects.get(user=order.user)
            subject = f'New Order Placed - Order #{order.id}'
            
            message = f"""
            A new order has been placed.
            
            Order Details:
            - Order ID: {order.id}
            - Customer: {customer.name} ({order.user.username})
            - Product: {order.product.title}
            - Quantity: {order.quantity}
            - Total Amount: {order.product.discounted_price * order.quantity}
            - Status: {order.status}
            - Order Date: {order.ordered_date}
            
            Customer Details:
            - Name: {customer.name}
            - Email: {order.user.email}
            - Phone: {customer.mobile}
            - Address: {customer.locality}, {customer.city}, {customer.state} - {customer.zipcode}
            
            Please process this order at your earliest convenience.
            """
            
            from_email = settings.DEFAULT_FROM_EMAIL
            admin_emails = [email for name, email in settings.ADMINS]
            
            if admin_emails:
                send_mail(
                    subject,
                    message,
                    from_email,
                    admin_emails,
                    fail_silently=False,
                )
                logger.info(f"Order notification email sent for order #{order.id}")
            else:
                logger.warning("No admin emails configured. Order notification not sent.")
                
        except Exception as e:
            logger.error(f"Failed to send order notification email: {str(e)}")


class OrderPlacedRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderPlacedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderPlaced.objects.filter(user=self.request.user)


# Wishlist APIs
class WishlistListCreateAPI(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


# Stripe Payment APIs
class CreateStripePaymentIntentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = request.data.get('amount')

            # Validate amount
            if not amount or not isinstance(amount, (int, float, str, Decimal)) or float(amount) <= 0:
                return Response({
                    'error': 'Valid amount is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Convert amount to float for calculation
            amount_float = float(amount)

            # Check minimum amount (₹50 or adjust based on your requirements)
            MIN_AMOUNT = 50
            if amount_float < MIN_AMOUNT:
                return Response({
                    'error': f'Minimum order amount is ₹{MIN_AMOUNT}'
                }, status=status.HTTP_400_BAD_REQUEST)

            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Create a payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount_float * 100),  # Convert to paisa
                currency="inr",
                payment_method_types=["card"],
                metadata={
                    "user_id": str(request.user.id),
                    "email": request.user.email
                }
            )

            # Store payment details
            payment = Payment.objects.create(
                user=request.user,
                amount=amount_float,
                stripe_payment_intent_id=payment_intent.id,
                paid=False
            )

            return Response({
                'client_secret': payment_intent.client_secret,
                'payment_id': payment.id,
                'publishableKey': settings.STRIPE_PUBLISHABLE_KEY
            }, status=status.HTTP_201_CREATED)

        except stripe.error.CardError as e:
            # Handle card errors
            return Response({
                'error': e.user_message
            }, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            # Handle other Stripe errors
            logger.error(f"Stripe error: {str(e)}")
            return Response({
                'error': 'Payment service unavailable. Please try again.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Unexpected error in payment creation: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyStripePaymentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            payment_intent_id = request.data.get('payment_intent_id')

            if not payment_intent_id:
                return Response({
                    'error': 'Payment Intent ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Retrieve payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            try:
                # Get payment record and verify it belongs to the current user
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent_id,
                    user=request.user
                )
            except Payment.DoesNotExist:
                return Response({
                    'error': 'Invalid payment'
                }, status=status.HTTP_404_NOT_FOUND)

            if payment.paid:
                return Response({
                    'error': 'Payment already processed'
                }, status=status.HTTP_400_BAD_REQUEST)

            if payment_intent.status == 'succeeded':
                # Update payment record
                payment.paid = True
                payment.save()

                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'message': 'Payment verified successfully'
                })
            else:
                return Response({
                    'error': f'Payment verification failed. Status: {payment_intent.status}'
                }, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe verification error: {str(e)}")
            return Response({
                'error': 'Failed to verify payment with payment provider'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Unexpected error in payment verification: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

# Review APIs
class ReviewListCreateAPI(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter reviews for a specific product if 'product' query param is provided."""
        product_id = self.request.query_params.get('product')
        queryset = Review.objects.all()
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        """Ensure the review is created by the logged-in user."""
        serializer.save(user=self.request.user)


class ReviewRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ensure users can only update/delete their own reviews."""
        return Review.objects.filter(user=self.request.user)
    
class StockListAPI(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class StockDetailAPI(generics.RetrieveAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    lookup_field = 'product__id'  # Allows lookup by product ID