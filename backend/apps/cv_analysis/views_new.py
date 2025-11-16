"""
Views for the 3 CV Analysis modules:
1. ATS Score Checker (Free with limits)
2. CV-Job Matcher (Free with limits) 
3. Advanced CV Analyzer (Premium)
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
import PyPDF2
import io

logger = logging.getLogger(__name__)

from .models import (
    CV, ATSAnalysis, CVJobMatch, AdvancedCVAnalysis,
    ChatMessage, CVAnalysisUsageTracker
)
from .serializers_new import (
    CVSerializer, ATSAnalysisSerializer, ATSAnalysisRequestSerializer,
    CVJobMatchSerializer, CVJobMatchRequestSerializer,
    AdvancedCVAnalysisSerializer, AdvancedCVAnalysisRequestSerializer,
    ChatMessageRequestSerializer, ChatMessageSerializer, UsageTrackerSerializer
)
from .services import CVAnalysisService
from apps.core.permissions import HasModuleAccess


class ATSCheckerViewSet(viewsets.ViewSet):
    """
    Module 1: ATS Score Checker
    - FREE: Unlimited ATS score checks
    - LIMITED: 3 free detailed reports, then paid
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Allow free access for basic score, require module for detailed reports"""
        # Basic ATS score is always free, no module required
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Analyze CV for ATS compatibility
        Returns basic score (always free) or detailed report (3 free, then paid)
        """
        serializer = ATSAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cv_file = serializer.validated_data['cv_file']
        request_detailed = serializer.validated_data.get('request_detailed_report', False)
        tenant = request.user.tenant
        
        if not tenant:
            return Response(
                {'error': 'You must belong to a tenant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract text from CV
        cv_text = self._extract_text(cv_file)
        
        # Save CV
        cv = CV.objects.create(
            tenant=tenant,
            user=request.user,
            file=cv_file,
            filename=cv_file.name,
            file_type=cv_file.name.split('.')[-1].lower(),
            file_size=cv_file.size,
            raw_text=cv_text,
            status='analyzed'
        )
        
        # Always calculate basic ATS score (FREE)
        service = CVAnalysisService()
        ats_data = service.calculate_ats_score(cv_text)
        
        # Check if detailed report requested
        can_get_detailed = False
        is_free_detailed = False
        
        if request_detailed:
            # Check usage tracker
            tracker, created = CVAnalysisUsageTracker.objects.get_or_create(
                tenant=tenant,
                module_type='ats_detailed',
                defaults={'free_limit': 3, 'used_count': 0}
            )
            
            # Check if has paid module access
            has_paid_access = request.user.has_module_access('ats_checker')
            
            if has_paid_access:
                # Paid user - always get detailed
                can_get_detailed = True
                is_free_detailed = False
            elif tracker.can_use_free:
                # Free user within limit
                can_get_detailed = True
                is_free_detailed = True
                tracker.used_count += 1
                tracker.save()
            else:
                # Free user exceeded limit - still return basic analysis
                basic_analysis = ATSAnalysis.objects.create(
                    tenant=tenant,
                    user=request.user,
                    cv=cv,
                    ats_score=ats_data['score'],
                    keyword_matches=ats_data.get('keyword_matches', []),
                    missing_keywords=ats_data.get('missing_keywords', []),
                    quick_suggestions=ats_data.get('suggestions', []),
                    has_detailed_report=False,
                    detailed_report='',
                    is_free_detailed_report=False
                )
                
                return Response({
                    'error': 'You have used all 3 free detailed reports. Please upgrade to continue.',
                    'upgrade_required': True,
                    'module_code': 'ats_checker',
                    'analysis': ATSAnalysisSerializer(basic_analysis).data
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        # Create analysis record with appropriate detail level
        analysis = ATSAnalysis.objects.create(
            tenant=tenant,
            user=request.user,
            cv=cv,
            ats_score=ats_data['score'],
            keyword_matches=ats_data.get('keyword_matches', []),
            missing_keywords=ats_data.get('missing_keywords', []),
            quick_suggestions=ats_data.get('suggestions', []),
            has_detailed_report=can_get_detailed,
            detailed_report=ats_data.get('detailed_report', '') if can_get_detailed else '',
            is_free_detailed_report=is_free_detailed
        )
        
        return Response(ATSAnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        """Get usage statistics for detailed reports"""
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        tracker, created = CVAnalysisUsageTracker.objects.get_or_create(
            tenant=tenant,
            module_type='ats_detailed',
            defaults={'free_limit': 3, 'used_count': 0}
        )
        
        has_paid = request.user.has_module_access('ats_checker')
        
        return Response({
            'has_paid_access': has_paid,
            'free_limit': tracker.free_limit,
            'used_count': tracker.used_count,
            'remaining_free': tracker.remaining_uses,
            'can_use_free': tracker.can_use_free
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get ATS analysis history"""
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        analyses = ATSAnalysis.objects.filter(tenant=tenant).order_by('-created_at')[:20]
        return Response(ATSAnalysisSerializer(analyses, many=True).data)
    
    @action(detail=True, methods=['post'], url_path='detailed_report')
    def request_detailed_report(self, request, pk=None):
        """Request detailed report for an existing analysis"""
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            analysis = ATSAnalysis.objects.get(id=pk, tenant=tenant)
        except ATSAnalysis.DoesNotExist:
            return Response({'error': 'Analysis not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # If already has detailed report, return it
        if analysis.has_detailed_report:
            return Response(ATSAnalysisSerializer(analysis).data)
        
        # Check usage tracker
        tracker, created = CVAnalysisUsageTracker.objects.get_or_create(
            tenant=tenant,
            module_type='ats_detailed',
            defaults={'free_limit': 3, 'used_count': 0}
        )
        
        # Check if has paid access
        has_paid_access = request.user.has_module_access('ats_checker')
        
        if not has_paid_access and not tracker.can_use_free:
            return Response({
                'error': 'You have used all 3 free detailed reports. Please upgrade to continue.',
                'upgrade_required': True,
                'module_code': 'ats_checker'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        # Generate detailed report
        service = CVAnalysisService()
        ats_data = service.calculate_ats_score(analysis.cv.raw_text)
        
        # Update analysis with detailed report
        analysis.has_detailed_report = True
        analysis.detailed_report = ats_data.get('detailed_report', '')
        analysis.is_free_detailed_report = not has_paid_access
        analysis.save()
        
        # Increment usage if free
        if not has_paid_access:
            tracker.used_count += 1
            tracker.save()
        
        return Response(ATSAnalysisSerializer(analysis).data)
    
    def _extract_text(self, file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            file.seek(0)  # Reset file pointer
            return text
        except:
            return ''


class CVJobMatcherViewSet(viewsets.ViewSet):
    """
    Module 2: CV-Job Matcher
    - FREE: 3 job matches
    - PAID: Unlimited matches
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def match(self, request):
        """
        Match CV against job description
        3 free matches, then requires paid access
        """
        # Debug logging
        logger.info(f"CV-Job Matcher request.data keys: {request.data.keys()}")
        logger.info(f"CV-Job Matcher request.FILES keys: {request.FILES.keys()}")
        
        serializer = CVJobMatchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check usage tracker
        tracker, created = CVAnalysisUsageTracker.objects.get_or_create(
            tenant=tenant,
            module_type='cv_matcher',
            defaults={'free_limit': 3, 'used_count': 0}
        )
        
        has_paid_access = request.user.has_module_access('cv_job_matcher')
        
        if not has_paid_access and not tracker.can_use_free:
            return Response({
                'error': 'You have used all 3 free job matches. Please upgrade to continue.',
                'upgrade_required': True,
                'module_code': 'cv_job_matcher'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        # Extract CV text
        cv_file = serializer.validated_data['cv_file']
        cv_text = self._extract_text(cv_file)
        
        # Save CV
        cv = CV.objects.create(
            tenant=tenant,
            user=request.user,
            file=cv_file,
            filename=cv_file.name,
            file_type=cv_file.name.split('.')[-1].lower(),
            file_size=cv_file.size,
            raw_text=cv_text,
            status='analyzed'
        )
        
        # Perform matching
        service = CVAnalysisService()
        match_data = service.match_cv_to_job(
            cv_text,
            serializer.validated_data['job_title'],
            serializer.validated_data['job_description']
        )
        
        # Increment usage if free
        is_free_match = False
        if not has_paid_access:
            tracker.used_count += 1
            tracker.save()
            is_free_match = True
        
        # Create match record
        match = CVJobMatch.objects.create(
            tenant=tenant,
            user=request.user,
            cv=cv,
            job_title=serializer.validated_data['job_title'],
            job_description=serializer.validated_data['job_description'],
            match_score=match_data['match_score'],
            matched_skills=match_data['matched_skills'],
            missing_skills=match_data['missing_skills'],
            matching_report=match_data['matching_report'],
            recommendations=match_data['recommendations'],
            is_free_match=is_free_match
        )
        
        return Response(CVJobMatchSerializer(match).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        """Get usage statistics"""
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        tracker, created = CVAnalysisUsageTracker.objects.get_or_create(
            tenant=tenant,
            module_type='cv_matcher',
            defaults={'free_limit': 3, 'used_count': 0}
        )
        
        has_paid = request.user.has_module_access('cv_job_matcher')
        
        return Response({
            'has_paid_access': has_paid,
            'free_limit': tracker.free_limit,
            'used_count': tracker.used_count,
            'remaining_free': tracker.remaining_uses,
            'can_use_free': tracker.can_use_free
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get matching history"""
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        matches = CVJobMatch.objects.filter(tenant=tenant).order_by('-created_at')[:20]
        return Response(CVJobMatchSerializer(matches, many=True).data)
    
    def _extract_text(self, file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            file.seek(0)
            return text
        except:
            return ''


class AdvancedCVAnalyzerViewSet(viewsets.ViewSet):
    """
    Module 3: Advanced CV Analyzer (PREMIUM ONLY)
    - Full ATS analysis
    - Job matching
    - CV formatting
    - AI chatbot
    """
    permission_classes = [permissions.IsAuthenticated, HasModuleAccess]
    module_code = 'advanced_cv_analyzer'
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Perform comprehensive CV analysis
        Requires paid module access
        """
        serializer = AdvancedCVAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract CV text
        cv_file = serializer.validated_data['cv_file']
        cv_text = self._extract_text(cv_file)
        
        # Save CV
        cv = CV.objects.create(
            tenant=tenant,
            user=request.user,
            file=cv_file,
            filename=cv_file.name,
            file_type=cv_file.name.split('.')[-1].lower(),
            file_size=cv_file.size,
            raw_text=cv_text,
            status='processing'
        )
        
        # Create analysis record
        analysis = AdvancedCVAnalysis.objects.create(
            tenant=tenant,
            user=request.user,
            cv=cv,
            status='processing'
        )
        
        # Perform comprehensive analysis
        service = CVAnalysisService()
        analysis_data = service.analyze_advanced_cv(cv_text)
        
        # Update analysis with results
        analysis.full_analysis = analysis_data['full_analysis']
        analysis.strengths = analysis_data['strengths']
        analysis.weaknesses = analysis_data['weaknesses']
        analysis.improvement_suggestions = analysis_data['improvement_suggestions']
        analysis.career_recommendations = analysis_data['career_recommendations']
        analysis.status = 'completed'
        analysis.save()
        
        cv.status = 'analyzed'
        cv.save()
        
        return Response(AdvancedCVAnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """
        Chat with Llama 3.1 AI about the CV analysis
        Send message and get AI response
        """
        try:
            analysis = AdvancedCVAnalysis.objects.get(
                id=pk,
                tenant=request.user.tenant
            )
        except AdvancedCVAnalysis.DoesNotExist:
            return Response({'error': 'Analysis not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ChatMessageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_message = serializer.validated_data['message']
        
        # Save user message
        ChatMessage.objects.create(
            advanced_analysis=analysis,
            role='user',
            content=user_message
        )
        
        # Generate AI response using Llama 3.1
        service = CVAnalysisService()
        ai_response = service.chat_about_cv_llama(
            analysis.cv.raw_text,
            user_message,
            analysis
        )
        
        # Save AI response
        assistant_message = ChatMessage.objects.create(
            advanced_analysis=analysis,
            role='assistant',
            content=ai_response
        )
        
        return Response(ChatMessageSerializer(assistant_message).data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get advanced analysis history"""
        tenant = request.user.tenant
        if not tenant:
            return Response({'error': 'No tenant'}, status=status.HTTP_400_BAD_REQUEST)
        
        analyses = AdvancedCVAnalysis.objects.filter(
            tenant=tenant
        ).order_by('-created_at')[:20]
        return Response(AdvancedCVAnalysisSerializer(analyses, many=True).data)
    
    def _extract_text(self, file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            file.seek(0)
            return text
        except:
            return ''
