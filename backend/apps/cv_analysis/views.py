from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count, Avg
from apps.core.permissions import HasModuleAccess
from .models import CV, CVAnalysis, Skill, CVSkill, Experience, Education, JobPosting, JobMatch
from .serializers import (
    CVSerializer, CVDetailSerializer, CVAnalysisSerializer,
    SkillSerializer, CVSkillSerializer, ExperienceSerializer, EducationSerializer,
    JobPostingSerializer, JobMatchSerializer, CVUploadSerializer, JobMatchingSerializer
)
from .tasks import process_cv_task
from .matching import JobMatchingService
from .job_scraper import JobScraperService
from .services import CVParser
import os


class CVViewSet(viewsets.ModelViewSet):
    """CV CRUD operations"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CVDetailSerializer
        return CVSerializer
    
    def get_queryset(self):
        return CV.objects.filter(tenant=self.request.user.tenant).select_related(
            'user', 'analysis'
        ).prefetch_related('skills', 'experiences', 'education')
    
    def create(self, request, *args, **kwargs):
        """Upload and process CV"""
        serializer = CVUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = serializer.validated_data['file']
        
        # Determine file type
        ext = os.path.splitext(file.name)[1].lower()
        file_type_map = {'.pdf': 'pdf', '.docx': 'docx', '.txt': 'txt'}
        file_type = file_type_map.get(ext, 'unknown')
        
        # Create CV record
        cv = CV.objects.create(
            tenant=request.user.tenant,
            user=request.user,
            file=file,
            filename=file.name,
            file_type=file_type,
            file_size=file.size,
            status='uploaded'
        )
        
        # Queue for processing
        process_cv_task.delay(cv.id)
        
        return Response(
            CVSerializer(cv, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a CV"""
        cv = self.get_object()
        
        # Queue for reprocessing
        process_cv_task.delay(cv.id)
        
        return Response({'message': 'CV queued for reprocessing'})
    
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Get CV analysis"""
        cv = self.get_object()
        
        if not hasattr(cv, 'analysis'):
            return Response(
                {'error': 'CV analysis not available yet'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(CVAnalysisSerializer(cv.analysis).data)
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """Get job matches for this CV"""
        cv = self.get_object()
        matches = cv.job_matches.all().order_by('-overall_score')[:20]
        
        return Response(JobMatchSerializer(matches, many=True).data)
    
    @action(detail=True, methods=['post'], parser_classes=[JSONParser])
    def find_jobs(self, request, pk=None):
        """
        Find real job postings matching this CV from Google Jobs
        Required params:
        - country: Target country (e.g., 'Tunisia', 'France', 'Canada')
        Optional params:
        - min_confidence: Minimum confidence score (default: 70)
        - max_jobs_per_title: Max jobs to fetch per job title (default: 5)
        """
        cv = self.get_object()
        
        # Get parameters
        country = request.data.get('country')
        if not country:
            return Response(
                {'error': 'Country is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        min_confidence = int(request.data.get('min_confidence', 70))
        max_jobs_per_title = int(request.data.get('max_jobs_per_title', 5))
        
        # Get CV text
        try:
            if cv.file and hasattr(cv.file, 'path'):
                cv_text = CVParser.extract_text(cv.file.path, cv.file_type)
            else:
                return Response(
                    {'error': 'CV file not found or inaccessible'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': f'Error reading CV: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Use job scraper service
        try:
            scraper = JobScraperService()
            results = scraper.scrape_jobs_for_cv(
                cv_text=cv_text,
                country=country,
                min_confidence=min_confidence,
                max_jobs_per_title=max_jobs_per_title
            )
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error finding jobs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """Skill catalog"""
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Skill.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(synonyms__contains=[search])
            )
        
        return queryset.annotate(cv_count=Count('cv_skills')).order_by('-cv_count')
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get skill categories"""
        categories = Skill.objects.values_list('category', flat=True).distinct()
        return Response(list(categories))
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending skills"""
        trending = Skill.objects.annotate(
            usage_count=Count('cv_skills')
        ).filter(usage_count__gt=0).order_by('-usage_count')[:20]
        
        return Response(SkillSerializer(trending, many=True).data)


class JobPostingViewSet(viewsets.ModelViewSet):
    """Job posting management"""
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = JobPosting.objects.filter(tenant=self.request.user.tenant)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(company__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.tenant,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """Get CV matches for this job"""
        job = self.get_object()
        matches = job.cv_matches.all().order_by('-overall_score')[:20]
        
        return Response(JobMatchSerializer(matches, many=True).data)


class JobMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """Job matching results"""
    serializer_class = JobMatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return JobMatch.objects.filter(
            cv__tenant=user.tenant
        ).select_related('cv', 'job')
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """Bookmark a match"""
        match = self.get_object()
        match.is_bookmarked = not match.is_bookmarked
        match.save()
        
        return Response({'is_bookmarked': match.is_bookmarked})
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Mark as applied"""
        from django.utils import timezone
        
        match = self.get_object()
        match.applied_at = timezone.now()
        match.save()
        
        return Response({'message': 'Marked as applied'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def match_cv_to_jobs(request):
    """Match a CV to all active jobs"""
    serializer = JobMatchingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    cv_id = serializer.validated_data['cv_id']
    limit = serializer.validated_data.get('limit', 10)
    min_score = serializer.validated_data.get('min_score', 50)
    
    try:
        cv = CV.objects.get(id=cv_id, tenant=request.user.tenant)
    except CV.DoesNotExist:
        return Response({'error': 'CV not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get active jobs
    jobs = JobPosting.objects.filter(
        tenant=request.user.tenant,
        status='active'
    )
    
    # Perform matching
    matching_service = JobMatchingService()
    matches = []
    
    for job in jobs:
        match = matching_service.match_cv_to_job(cv, job)
        if match.overall_score >= min_score:
            matches.append(match)
    
    # Sort by score and limit
    matches = sorted(matches, key=lambda m: m.overall_score, reverse=True)[:limit]
    
    return Response(JobMatchSerializer(matches, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cv_statistics(request):
    """Get CV analysis statistics for tenant"""
    tenant = request.user.tenant
    
    # Total CVs
    total_cvs = CV.objects.filter(tenant=tenant).count()
    
    # CVs by status
    by_status = CV.objects.filter(tenant=tenant).values('status').annotate(count=Count('id'))
    
    # Average scores
    avg_scores = CVAnalysis.objects.filter(cv__tenant=tenant).aggregate(
        avg_overall=Avg('overall_score'),
        avg_experience=Avg('experience_score'),
        avg_education=Avg('education_score'),
        avg_skills=Avg('skills_score')
    )
    
    # Most common skills
    common_skills = CVSkill.objects.filter(
        cv__tenant=tenant
    ).values('skill__name', 'skill__category').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'total_cvs': total_cvs,
        'by_status': list(by_status),
        'average_scores': avg_scores,
        'common_skills': list(common_skills)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_statistics(request):
    """Get job posting statistics"""
    tenant = request.user.tenant
    
    # Total jobs
    total_jobs = JobPosting.objects.filter(tenant=tenant).count()
    
    # Jobs by status
    by_status = JobPosting.objects.filter(tenant=tenant).values('status').annotate(count=Count('id'))
    
    # Average match scores
    avg_match_score = JobMatch.objects.filter(
        job__tenant=tenant
    ).aggregate(avg=Avg('overall_score'))
    
    # Most in-demand skills
    from django.db.models import Count
    from .models import JobSkill
    
    in_demand_skills = JobSkill.objects.filter(
        job__tenant=tenant,
        job__status='active'
    ).values('skill__name', 'requirement_level').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'total_jobs': total_jobs,
        'by_status': list(by_status),
        'average_match_score': avg_match_score.get('avg', 0),
        'in_demand_skills': list(in_demand_skills)
    })
