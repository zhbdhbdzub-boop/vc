"""
Views for interview simulation module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from apps.core.permissions import HasModuleAccess
from .models import (
    InterviewTemplate, InterviewSession, Question,
    SessionQuestion, InterviewFeedback, ConversationMessage
)
from .serializers import (
    InterviewTemplateSerializer, InterviewSessionSerializer,
    StartSessionSerializer, CandidateResponseSerializer,
    EndSessionSerializer, ConversationMessageSerializer
)
from .realtime_service import RealTimeInterviewService


class InterviewSimulatorViewSet(viewsets.ModelViewSet):
    """Real-time Interview Simulation API"""
    permission_classes = [IsAuthenticated, HasModuleAccess]
    module_code = 'interview_simulator'
    serializer_class = InterviewSessionSerializer
    
    def get_queryset(self):
        return InterviewSession.objects.filter(
            tenant=self.request.user.tenant,
            user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'], url_path='start')
    def start_session(self, request):
        """
        Start a new interview simulation session
        POST /api/interviews/simulator/start/
        {
            "title": "Software Engineer Interview Practice",
            "job_role": "Senior Software Engineer",
            "company_name": "TechCorp",
            "mode": "simulation"
        }
        """
        serializer = StartSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create session
        session = InterviewSession.objects.create(
            tenant=request.user.tenant,
            user=request.user,
            title=serializer.validated_data['title'],
            job_role=serializer.validated_data.get('job_role', ''),
            company_name=serializer.validated_data.get('company_name', ''),
            mode=serializer.validated_data.get('mode', 'practice'),
            status='pending'
        )
        
        # Start real-time service
        service = RealTimeInterviewService(session)
        result = service.start_session()
        
        return Response({
            'session_id': str(session.id),
            'status': 'started',
            'opening_message': result['message'],
            'session': InterviewSessionSerializer(session).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        """
        Submit candidate response and get next question
        POST /api/interviews/simulator/{session_id}/respond/
        {
            "response_text": "I have 5 years of experience...",
            "audio_url": "https://...",
            "timestamp": 45.5
        }
        """
        session = self.get_object()
        
        if session.status != 'in_progress':
            return Response(
                {'error': 'Session is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CandidateResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process response
        service = RealTimeInterviewService(session)
        result = service.process_candidate_response(
            response_text=serializer.validated_data['response_text'],
            audio_url=serializer.validated_data.get('audio_url', ''),
            timestamp=serializer.validated_data.get('timestamp', 0)
        )
        
        return Response({
            'next_question': result['question'],
            'analysis': result['analysis'],
            'message_id': result['message_id']
        })
    
    @action(detail=True, methods=['post'], url_path='end')
    def end_session(self, request, pk=None):
        """
        End the interview session and get feedback
        POST /api/interviews/simulator/{session_id}/end/
        """
        session = self.get_object()
        
        if session.status == 'completed':
            return Response(
                {'error': 'Session already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # End session and generate feedback
        service = RealTimeInterviewService(session)
        result = service.end_session()
        
        # Refresh session from DB
        session.refresh_from_db()
        
        return Response({
            'session': InterviewSessionSerializer(session).data,
            'feedback': result['feedback'],
            'scores': result['scores']
        })
    
    @action(detail=True, methods=['get'], url_path='transcript')
    def get_transcript(self, request, pk=None):
        """
        Get full conversation transcript
        GET /api/interviews/simulator/{session_id}/transcript/
        """
        session = self.get_object()
        service = RealTimeInterviewService(session)
        transcript = service.get_transcript()
        
        return Response({
            'session_id': str(session.id),
            'transcript': transcript
        })
    
    @action(detail=True, methods=['get'], url_path='messages')
    def get_messages(self, request, pk=None):
        """
        Get all conversation messages for a session
        GET /api/interviews/simulator/{session_id}/messages/
        """
        session = self.get_object()
        messages = ConversationMessage.objects.filter(
            session=session
        ).order_by('timestamp_seconds')
        
        serializer = ConversationMessageSerializer(messages, many=True)
        return Response({
            'session_id': str(session.id),
            'messages': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='history')
    def get_history(self, request):
        """
        Get user's interview history
        GET /api/interviews/simulator/history/
        """
        sessions = self.get_queryset()
        serializer = self.get_serializer(sessions, many=True)
        
        return Response({
            'count': sessions.count(),
            'sessions': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='templates')
    def get_templates(self, request):
        """
        Get available interview templates
        GET /api/interviews/simulator/templates/
        """
        templates = InterviewTemplate.objects.filter(
            is_active=True,
            is_public=True
        )
        
        serializer = InterviewTemplateSerializer(templates, many=True)
        return Response({
            'templates': serializer.data
        })


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    """Interview template and session management (legacy)"""
    permission_classes = [IsAuthenticated, HasModuleAccess]
    module_code = 'interviews'  # Require Interview module
    
    def get_queryset(self):
        return InterviewTemplate.objects.filter(tenant=self.request.user.tenant)
