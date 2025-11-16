# Billing & Marketplace Design

## Overview

The billing system handles module purchases, subscriptions, trials, and invoicing. Integrated with Stripe for payment processing.

---

## Pricing Models

### 1. One-Time Purchase (Lifetime License)
**Use Case:** Customers who prefer to pay once and own forever.

**Example:**
- CV Analysis Module: $299 one-time
- Interview Simulation Module: $399 one-time

**Benefits:**
- No recurring charges
- Lifetime updates and support
- Transfer to different tenants (with restrictions)

**Implementation:**
```python
class Purchase:
    amount: Decimal = 299.00
    status: Enum = ['pending', 'completed', 'failed', 'refunded']
    stripe_payment_intent_id: str
    
    def activate_license(self):
        ModuleLicense.objects.create(
            tenant=self.tenant,
            module=self.module,
            license_type='purchased',
            expires_at=None  # Lifetime
        )
```

---

### 2. Monthly Subscription
**Use Case:** Lower upfront cost, flexible commitment.

**Example:**
- CV Analysis Module: $49/month
- Interview Simulation Module: $69/month

**Benefits:**
- Lower entry barrier
- Cancel anytime
- Auto-renewal with credit card on file

**Stripe Integration:**
```python
stripe.Subscription.create(
    customer=stripe_customer_id,
    items=[{'price': 'price_cv_analysis_monthly'}],
    payment_behavior='default_incomplete',
    expand=['latest_invoice.payment_intent']
)
```

---

### 3. Annual Subscription (20% discount)
**Use Case:** Committed users, better value.

**Example:**
- CV Analysis Module: $490/year (vs $588 monthly)
- Interview Simulation Module: $690/year (vs $828 monthly)

**Benefits:**
- 2 months free vs monthly
- Lower transaction fees for business
- Predictable annual revenue

---

### 4. Free Trial (14 days)
**Use Case:** Let users test before buying.

**Features:**
- Full feature access during trial
- No credit card required (optional)
- Auto-convert to paid or deactivate after expiration

**Implementation:**
```python
def start_trial(tenant, module):
    license = ModuleLicense.objects.create(
        tenant=tenant,
        module=module,
        license_type='trial',
        activated_at=timezone.now(),
        expires_at=timezone.now() + timedelta(days=14)
    )
    
    # Schedule reminder emails
    schedule_email(tenant, 'trial_day_7', delay=7*24*3600)
    schedule_email(tenant, 'trial_expiring', delay=13*24*3600)
```

---

### 5. Bundle Pricing (Future)
**Use Case:** Multiple modules at discounted rate.

**Example:**
- Recruitment Suite (CV + Interview): $99/month (vs $118 separate)
- Enterprise Package (All modules): $299/month

---

## Purchase Flow

### One-Time Purchase Flow

```
┌─────────────────────────────────────────────────────┐
│  Step 1: User Browses Marketplace                   │
│  - Views module details                             │
│  - Clicks "Purchase Now" button                     │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 2: Checkout Modal Opens                       │
│  ┌───────────────────────────────────────────────┐ │
│  │ Purchase: CV Analysis Module                  │ │
│  │ Price: $299.00                                │ │
│  │                                               │ │
│  │ [Stripe Card Element]                         │ │
│  │ Card: [1234 5678 9012 3456]                   │ │
│  │ Exp:  [12/25]  CVV: [123]                     │ │
│  │                                               │ │
│  │ Billing Info:                                 │ │
│  │ Name:    [John Doe]                           │ │
│  │ Email:   [john@example.com]                   │ │
│  │ Address: [123 Main St, City, Country]        │ │
│  │                                               │ │
│  │ ☑ I agree to Terms of Service                │ │
│  │                                               │ │
│  │ [Cancel]  [Complete Purchase - $299.00]       │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 3: Backend Processing                         │
│  1. Create Purchase record (status: pending)        │
│  2. Create Stripe PaymentIntent                     │
│  3. Return client_secret to frontend                │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 4: Stripe Payment Confirmation                │
│  - Frontend calls Stripe.confirmCardPayment()       │
│  - 3D Secure challenge if required                  │
│  - Stripe returns success/failure                   │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 5: Backend Confirmation                       │
│  1. Frontend calls POST /purchases/:id/confirm      │
│  2. Verify payment with Stripe                      │
│  3. Update Purchase.status = 'completed'            │
│  4. Create ModuleLicense (activated, lifetime)      │
│  5. Send confirmation email with invoice            │
│  6. Create Invoice record                           │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 6: User Redirected to Module                  │
│  - Success page with confetti animation 🎉          │
│  - "Your module is ready to use"                    │
│  - [Go to CV Analysis Dashboard]                    │
└─────────────────────────────────────────────────────┘
```

---

### Subscription Flow

```
┌─────────────────────────────────────────────────────┐
│  Step 1: User Selects Subscription                  │
│  - Chooses Monthly or Annual                        │
│  - Clicks "Subscribe" button                        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 2: Checkout (Similar to Purchase)             │
│  - Stripe card element                              │
│  - Billing information                              │
│  - Shows "First charge: $49.00 today"               │
│  - Shows "Renews: December 7, 2025"                 │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 3: Backend Processing                         │
│  1. Create or retrieve Stripe Customer              │
│  2. Attach PaymentMethod to Customer                │
│  3. Create Stripe Subscription                      │
│  4. Create Subscription record in DB                │
│  5. Create ModuleLicense (activated)                │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 4: Stripe Webhooks (Async)                    │
│  - invoice.payment_succeeded → Confirm activation   │
│  - customer.subscription.created → Log event        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Step 5: User Dashboard                             │
│  - Module appears in "My Modules"                   │
│  - Shows subscription details:                      │
│    * Next billing date                              │
│    * Amount                                         │
│    * [Cancel Subscription] button                   │
└─────────────────────────────────────────────────────┘
```

---

### Trial Flow

```
Step 1: Start Trial (No Payment)
    ↓
Create ModuleLicense (trial, expires in 14 days)
    ↓
Send welcome email: "Your trial has started"
    ↓
Day 7: Send email: "7 days left in trial"
    ↓
Day 13: Send email: "Trial expiring tomorrow"
    ↓
Day 14: 
    ├→ User subscribed → Keep license active
    └→ User did not subscribe → Deactivate license
    ↓
Send follow-up: "Trial ended. Subscribe to continue"
```

---

## Stripe Webhook Handling

### Critical Webhooks

#### 1. invoice.payment_succeeded
**Trigger:** Subscription payment successful.

**Action:**
```python
def handle_payment_succeeded(event):
    invoice = event['data']['object']
    subscription_id = invoice['subscription']
    
    # Find subscription in DB
    subscription = Subscription.objects.get(
        stripe_subscription_id=subscription_id
    )
    
    # Update period
    subscription.current_period_start = datetime.fromtimestamp(
        invoice['period_start']
    )
    subscription.current_period_end = datetime.fromtimestamp(
        invoice['period_end']
    )
    subscription.save()
    
    # Ensure license is active
    license = ModuleLicense.objects.get(
        tenant=subscription.tenant,
        module=subscription.module
    )
    license.is_active = True
    license.expires_at = subscription.current_period_end
    license.save()
    
    # Send receipt email
    send_email('receipt', subscription.tenant.admin_email)
```

#### 2. invoice.payment_failed
**Trigger:** Subscription payment failed.

**Action:**
```python
def handle_payment_failed(event):
    invoice = event['data']['object']
    subscription_id = invoice['subscription']
    
    subscription = Subscription.objects.get(
        stripe_subscription_id=subscription_id
    )
    
    # Grace period: Don't deactivate immediately
    # Stripe will retry automatically
    
    # Send dunning email
    send_email('payment_failed', subscription.tenant.admin_email, {
        'amount': invoice['amount_due'] / 100,
        'next_retry': invoice['next_payment_attempt']
    })
    
    # After 3 failed attempts (configured in Stripe):
    if invoice['attempt_count'] >= 3:
        # Suspend license (keep data, disable access)
        license = ModuleLicense.objects.get(
            tenant=subscription.tenant,
            module=subscription.module
        )
        license.is_active = False
        license.save()
```

#### 3. customer.subscription.deleted
**Trigger:** Subscription cancelled or expired.

**Action:**
```python
def handle_subscription_deleted(event):
    subscription_data = event['data']['object']
    subscription_id = subscription_data['id']
    
    subscription = Subscription.objects.get(
        stripe_subscription_id=subscription_id
    )
    subscription.status = 'expired'
    subscription.save()
    
    # Deactivate license
    license = ModuleLicense.objects.get(
        tenant=subscription.tenant,
        module=subscription.module
    )
    license.is_active = False
    license.save()
    
    # Send cancellation confirmation
    send_email('subscription_cancelled', subscription.tenant.admin_email)
```

---

## Cancellation & Refunds

### Subscription Cancellation

**Options:**
1. **Cancel at period end** (default)
   - User keeps access until current billing period ends
   - No charges after that
   
2. **Cancel immediately**
   - Access revoked instantly
   - Prorated refund for unused time

**Implementation:**
```python
def cancel_subscription(subscription_id, immediate=False):
    subscription = Subscription.objects.get(id=subscription_id)
    
    if immediate:
        # Cancel and refund
        stripe.Subscription.delete(
            subscription.stripe_subscription_id,
            prorate=True,
            invoice_now=True
        )
        subscription.status = 'cancelled'
        license.is_active = False
    else:
        # Cancel at period end
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        subscription.cancel_at_period_end = True
    
    subscription.cancelled_at = timezone.now()
    subscription.save()
    license.save()
```

### Refund Policy

**One-Time Purchases:**
- 30-day money-back guarantee
- Full refund, no questions asked
- License deactivated upon refund

**Subscriptions:**
- Cancel anytime (no refund for current month)
- Prorated refund only if immediate cancellation

**Implementation:**
```python
def refund_purchase(purchase_id, reason='requested_by_customer'):
    purchase = Purchase.objects.get(id=purchase_id)
    
    # Check eligibility (30 days)
    if timezone.now() - purchase.created_at > timedelta(days=30):
        raise RefundNotAllowed("Refund period expired")
    
    # Refund via Stripe
    refund = stripe.Refund.create(
        payment_intent=purchase.stripe_payment_intent_id,
        reason=reason
    )
    
    # Update purchase
    purchase.status = 'refunded'
    purchase.refunded_at = timezone.now()
    purchase.save()
    
    # Deactivate license
    license = ModuleLicense.objects.get(
        tenant=purchase.tenant,
        module=purchase.module
    )
    license.is_active = False
    license.save()
    
    # Notify user
    send_email('refund_processed', purchase.tenant.admin_email)
```

---

## Invoicing

### Invoice Generation

**Automatic Invoices:**
- Generated for every purchase and subscription payment
- PDF generated using ReportLab or WeasyPrint
- Stored in S3
- Emailed to customer

**Invoice Fields:**
```python
class Invoice:
    invoice_number: str  # "INV-2025-001234"
    tenant: ForeignKey
    amount: Decimal
    currency: str = "USD"
    status: Enum = ['draft', 'sent', 'paid', 'void']
    line_items: JSONField = [
        {
            'description': 'CV Analysis Module - Monthly',
            'quantity': 1,
            'unit_price': 49.00,
            'total': 49.00
        }
    ]
    tax_amount: Decimal = 0.00  # VAT/Sales Tax
    total: Decimal
    due_date: Date
    paid_at: DateTime
    pdf_url: str
```

**Invoice Number Format:**
- `INV-{YEAR}-{SEQUENCE}`
- Example: `INV-2025-000123`

---

## Marketplace UI Components

### Module Card (Purchase Options)

```tsx
<div className="module-card">
  <h3>CV Analysis</h3>
  <p>AI-powered CV matching and analysis</p>
  
  <div className="pricing-options">
    {/* Trial Option */}
    <div className="option trial">
      <span className="badge">Popular</span>
      <h4>Free Trial</h4>
      <p>14 days, full features</p>
      <Button>Start Free Trial</Button>
    </div>
    
    {/* Monthly */}
    <div className="option monthly">
      <h4>Monthly</h4>
      <div className="price">
        <span className="amount">$49</span>
        <span className="period">/month</span>
      </div>
      <ul>
        <li>✓ Cancel anytime</li>
        <li>✓ Unlimited analyses</li>
        <li>✓ Email support</li>
      </ul>
      <Button>Subscribe Monthly</Button>
    </div>
    
    {/* Annual (Best Value) */}
    <div className="option annual highlighted">
      <span className="badge">Best Value</span>
      <h4>Annual</h4>
      <div className="price">
        <span className="amount">$490</span>
        <span className="period">/year</span>
        <span className="savings">Save $98</span>
      </div>
      <ul>
        <li>✓ 2 months free</li>
        <li>✓ Unlimited analyses</li>
        <li>✓ Priority support</li>
      </ul>
      <Button>Subscribe Annually</Button>
    </div>
    
    {/* Lifetime */}
    <div className="option lifetime">
      <h4>Lifetime</h4>
      <div className="price">
        <span className="amount">$299</span>
        <span className="period">one-time</span>
      </div>
      <ul>
        <li>✓ Pay once, use forever</li>
        <li>✓ All future updates</li>
        <li>✓ Lifetime support</li>
      </ul>
      <Button>Purchase Lifetime</Button>
    </div>
  </div>
</div>
```

### Billing Dashboard

```tsx
<div className="billing-dashboard">
  <h2>Billing & Subscriptions</h2>
  
  {/* Active Subscriptions */}
  <section>
    <h3>Active Subscriptions</h3>
    <table>
      <tr>
        <td>CV Analysis</td>
        <td>$49.00/month</td>
        <td>Renews: Dec 7, 2025</td>
        <td><Button variant="outline">Manage</Button></td>
      </tr>
      <tr>
        <td>Interview Simulation</td>
        <td>$69.00/month</td>
        <td>Renews: Dec 15, 2025</td>
        <td><Button variant="outline">Manage</Button></td>
      </tr>
    </table>
  </section>
  
  {/* Payment Methods */}
  <section>
    <h3>Payment Methods</h3>
    <div className="payment-method">
      <CreditCardIcon />
      <span>Visa ending in 4242</span>
      <span>Expires 12/25</span>
      <Button variant="outline">Edit</Button>
    </div>
    <Button variant="link">+ Add Payment Method</Button>
  </section>
  
  {/* Invoices */}
  <section>
    <h3>Invoices</h3>
    <table>
      <tr>
        <td>INV-2025-001234</td>
        <td>Nov 7, 2025</td>
        <td>$49.00</td>
        <td><Badge>Paid</Badge></td>
        <td><Button variant="link">Download PDF</Button></td>
      </tr>
    </table>
  </section>
</div>
```

---

## License Enforcement

### Backend Middleware
```python
class ModuleLicenseMiddleware:
    def __call__(self, request):
        tenant = request.user.tenant
        module_slug = request.resolver_match.app_name
        
        # Check if module requires license
        if module_slug in LICENSED_MODULES:
            license = ModuleLicense.objects.filter(
                tenant=tenant,
                module__slug=module_slug,
                is_active=True
            ).first()
            
            if not license:
                return HttpResponseForbidden(
                    "Module not licensed. Please purchase from marketplace."
                )
            
            # Check expiration (trials, subscriptions)
            if license.expires_at and timezone.now() > license.expires_at:
                license.is_active = False
                license.save()
                return HttpResponseForbidden("License expired.")
        
        return self.get_response(request)
```

### Frontend Route Guard
```tsx
function ProtectedModuleRoute({ moduleName, children }) {
  const { licenses } = useLicenses();
  
  const hasLicense = licenses.some(
    l => l.module.slug === moduleName && l.is_active
  );
  
  if (!hasLicense) {
    return <Redirect to={`/marketplace/${moduleName}`} />;
  }
  
  return children;
}
```

---

## Tax Handling

### Sales Tax / VAT
- Use Stripe Tax (automatic calculation)
- Store customer's tax ID if provided (EU VAT)
- Generate tax-compliant invoices

```python
stripe.TaxRate.create(
    display_name="VAT",
    percentage=20.0,  # 20% VAT
    inclusive=False,
    country="GB"
)
```

---

## Metrics & Analytics

### Key Metrics to Track
1. **MRR (Monthly Recurring Revenue)**: Sum of all active monthly subscriptions
2. **Churn Rate**: % of subscriptions cancelled per month
3. **LTV (Lifetime Value)**: Average revenue per customer
4. **CAC (Customer Acquisition Cost)**: Marketing spend / new customers
5. **Trial Conversion Rate**: % of trials that convert to paid

### Dashboard Queries
```sql
-- MRR
SELECT SUM(amount) FROM subscriptions 
WHERE status = 'active' AND interval = 'monthly';

-- Churn Rate
SELECT 
  COUNT(*) FILTER (WHERE cancelled_at IS NOT NULL) * 100.0 / 
  COUNT(*) 
FROM subscriptions 
WHERE created_at >= NOW() - INTERVAL '30 days';
```

---

## Summary

✓ Multiple pricing models (purchase, subscription, trial)
✓ Stripe integration for payments
✓ Webhook handling for automated renewals
✓ Refund and cancellation workflows
✓ Invoice generation and storage
✓ License enforcement at API level
✓ Tax compliance ready
✓ Analytics and reporting
