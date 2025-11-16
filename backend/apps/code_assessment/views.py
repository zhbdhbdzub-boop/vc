"""
Views for code assessment module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.core.permissions import HasModuleAccess
from .models import CodingProblem, Submission, UserProgress


class CodingProblemViewSet(viewsets.ReadOnlyModelViewSet):
    """Coding problems browsing"""
    permission_classes = [IsAuthenticated, HasModuleAccess]
    module_code = 'code_assessment'  # Require Code Assessment module
    
    def get_queryset(self):
        return CodingProblem.objects.filter(tenant=self.request.user.tenant, is_active=True)


class SubmissionViewSet(viewsets.ModelViewSet):
    """Code submission and execution"""
    permission_classes = [IsAuthenticated, HasModuleAccess]
    module_code = 'code_assessment'
    
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)
