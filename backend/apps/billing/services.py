"""
Stripe payment service integration.
"""
import stripe
from django.conf import settings
from typing import Dict, Any

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class StripeService:
    """Service for handling Stripe payments"""
    
    @staticmethod
    def create_customer(email: str, name: str, metadata: Dict[str, Any] = None) -> stripe.Customer:
        """Create a Stripe customer"""
        return stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {}
        )
    
    @staticmethod
    def create_charge(
        amount: int,
        currency: str,
        customer: str,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> stripe.Charge:
        """Create a one-time charge"""
        return stripe.Charge.create(
            amount=amount,
            currency=currency,
            customer=customer,
            description=description,
            metadata=metadata or {}
        )
    
    @staticmethod
    def create_payment_intent(
        amount: int,
        currency: str,
        customer: str = None,
        metadata: Dict[str, Any] = None
    ) -> stripe.PaymentIntent:
        """Create a payment intent"""
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer,
            metadata=metadata or {}
        )
    
    @staticmethod
    def create_subscription(
        customer: str,
        price_id: str,
        metadata: Dict[str, Any] = None
    ) -> stripe.Subscription:
        """Create a subscription"""
        return stripe.Subscription.create(
            customer=customer,
            items=[{'price': price_id}],
            metadata=metadata or {}
        )
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> stripe.Subscription:
        """Cancel a subscription"""
        return stripe.Subscription.delete(subscription_id)
    
    @staticmethod
    def get_customer(customer_id: str) -> stripe.Customer:
        """Retrieve a customer"""
        return stripe.Customer.retrieve(customer_id)
    
    @staticmethod
    def list_payment_methods(customer_id: str) -> list:
        """List payment methods for a customer"""
        return stripe.PaymentMethod.list(
            customer=customer_id,
            type='card'
        ).data
