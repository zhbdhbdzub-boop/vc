from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel
from apps.modules.models import Module


class StripeCustomer(TimestampedModel):
    """Stripe customer linked to a tenant"""
    tenant = models.OneToOneField('core.Tenant', on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    
    class Meta:
        db_table = 'billing_stripe_customers'
        verbose_name = 'Stripe Customer'
        verbose_name_plural = 'Stripe Customers'
    
    def __str__(self):
        return f"{self.tenant.name} - {self.stripe_customer_id}"


class Payment(TimestampedModel):
    """Payment transactions"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('canceled', 'Canceled'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('module_purchase', 'Module Purchase'),
        ('subscription', 'Subscription'),
        ('one_time', 'One-time Payment'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TND')  # Changed to TND
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPE_CHOICES)
    
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    description = models.TextField(blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'billing_payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - ${self.amount} ({self.status})"


class Subscription(TimestampedModel):
    """Recurring subscriptions"""
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('trialing', 'Trialing'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
        ('incomplete', 'Incomplete'),
    ]
    
    INTERVAL_CHOICES = [
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='subscriptions')
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_price_id = models.CharField(max_length=255)
    
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscriptions')
    
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES)
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'billing_subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.module.name if self.module else 'Unknown'} ({self.status})"
    
    @property
    def is_active(self):
        return self.status in ['active', 'trialing']


class Invoice(TimestampedModel):
    """Stripe invoices"""
    INVOICE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
        ('uncollectible', 'Uncollectible'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='invoices')
    stripe_invoice_id = models.CharField(max_length=255, unique=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES)
    
    invoice_number = models.CharField(max_length=100, blank=True)
    invoice_pdf = models.URLField(blank=True)
    hosted_invoice_url = models.URLField(blank=True)
    
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'billing_invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.tenant.name} (${self.amount_due})"


class PaymentMethod(TimestampedModel):
    """Saved payment methods"""
    PAYMENT_METHOD_TYPE_CHOICES = [
        ('card', 'Credit Card'),
        ('bank_account', 'Bank Account'),
    ]
    
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name='payment_methods')
    stripe_payment_method_id = models.CharField(max_length=255, unique=True)
    
    type = models.CharField(max_length=20, choices=PAYMENT_METHOD_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    
    # Card details (masked)
    card_brand = models.CharField(max_length=20, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    
    # Bank account details (masked)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_last4 = models.CharField(max_length=4, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'billing_payment_methods'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.type == 'card':
            return f"{self.card_brand} ****{self.card_last4}"
        return f"{self.bank_name} ****{self.bank_last4}"
    
    def save(self, *args, **kwargs):
        # If this is set as default, unset all other defaults for this tenant
        if self.is_default:
            PaymentMethod.objects.filter(tenant=self.tenant, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UsageRecord(TimestampedModel):
    """Track metered billing usage"""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usage_records')
    
    quantity = models.IntegerField()
    action = models.CharField(max_length=100)  # e.g., 'api_call', 'cv_analysis', 'interview_simulation'
    
    timestamp = models.DateTimeField(auto_now_add=True)
    stripe_usage_record_id = models.CharField(max_length=255, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'billing_usage_records'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['subscription', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.subscription.tenant.name} - {self.action} x{self.quantity}"
