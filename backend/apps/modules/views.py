"""
Views for module marketplace.
"""
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import Module, ModuleLicense
from .serializers import ModuleSerializer, ModuleLicenseSerializer, ModulePurchaseSerializer
from apps.billing.services import StripeService


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for browsing available modules.
    """
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    permission_classes = [permissions.AllowAny]  # Allow public viewing of marketplace
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'created_at', 'price_monthly']
    ordering = ['name']
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def purchase(self, request, pk=None):
        """Purchase or start trial for a module"""
        module = self.get_object()
        serializer = ModulePurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        license_type = serializer.validated_data['license_type']
        tenant = request.user.tenant
        
        if not tenant:
            return Response(
                {'error': 'You must belong to a tenant to purchase modules'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already has license
        existing_license = ModuleLicense.objects.filter(
            tenant=tenant,
            module=module,
            is_active=True
        ).first()
        
        # If upgrading from trial to paid, deactivate trial
        if existing_license and license_type != 'trial':
            if existing_license.license_type == 'trial':
                # Allow upgrade from trial to paid
                existing_license.is_active = False
                existing_license.save()
            else:
                return Response(
                    {'error': 'You already have an active paid license for this module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif existing_license and license_type == 'trial':
            return Response(
                {'error': 'You already have an active license for this module'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle trial
        if license_type == 'trial':
            expires_at = timezone.now() + timedelta(days=module.trial_days)
            license = ModuleLicense.objects.create(
                tenant=tenant,
                module=module,
                license_type='trial',
                is_active=True,
                expires_at=expires_at
            )
            
            return Response({
                'message': f'Trial started successfully. Expires in {module.trial_days} days.',
                'license': ModuleLicenseSerializer(license).data
            }, status=status.HTTP_201_CREATED)
        
        # Handle paid licenses
        payment_method_id = serializer.validated_data.get('payment_method_id')
        
        # Determine price
        price_map = {
            'monthly': module.price_monthly,
            'annual': module.price_annual,
            'lifetime': module.price_lifetime
        }
        price = price_map.get(license_type)
        
        if not price:
            return Response(
                {'error': 'Invalid license type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process payment with Stripe
        try:
            stripe_service = StripeService()
            
            # Create or get customer
            if not tenant.stripe_customer_id:
                customer = stripe_service.create_customer(
                    email=request.user.email,
                    name=tenant.name
                )
                tenant.stripe_customer_id = customer.id
                tenant.save()
            
            # Charge the customer
            charge = stripe_service.create_charge(
                amount=int(price * 100),  # Convert to cents
                currency='usd',
                customer=tenant.stripe_customer_id,
                description=f'{module.name} - {license_type} license',
                metadata={
                    'tenant_id': str(tenant.id),
                    'module_id': str(module.id),
                    'license_type': license_type
                }
            )
            
            # Create license
            expires_at = None
            if license_type == 'monthly':
                expires_at = timezone.now() + timedelta(days=30)
            elif license_type == 'annual':
                expires_at = timezone.now() + timedelta(days=365)
            # lifetime has no expiration
            
            license = ModuleLicense.objects.create(
                tenant=tenant,
                module=module,
                license_type=license_type,
                is_active=True,
                expires_at=expires_at
            )
            
            return Response({
                'message': 'Module purchased successfully!',
                'license': ModuleLicenseSerializer(license).data,
                'charge_id': charge.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Payment failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MyModulesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing tenant's active modules.
    """
    serializer_class = ModuleLicenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter licenses by current tenant."""
        if not self.request.user.tenant:
            return ModuleLicense.objects.none()
        return ModuleLicense.objects.filter(
            tenant=self.request.user.tenant,
            is_active=True
        ).select_related('module')
