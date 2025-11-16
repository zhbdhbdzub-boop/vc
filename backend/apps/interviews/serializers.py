"""
Serializers for Interview Simulation API
"""
from rest_framework import serializers
from .models import InterviewSession, ConversationMessage, InterviewTemplate


class InterviewTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewTemplate
        fields = [
            'id', 'name', 'description', 'interview_type', 'difficulty',
            'job_role', 'experience_level', 'duration_minutes', 'question_count',
            'is_public', 'usage_count', 'created_at'
        ]


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = [
            'id', 'role', 'content', 'audio_url', 'duration_seconds',
            'sentiment', 'confidence_score', 'keywords_detected',
            'timestamp_seconds', 'created_at'
        ]


class InterviewSessionSerializer(serializers.ModelSerializer):
    messages = ConversationMessageSerializer(source='conversation_messages', many=True, read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'title', 'job_role', 'company_name', 'status', 'mode',
            'started_at', 'completed_at', 'duration_seconds',
            'overall_score', 'technical_score', 'communication_score',
            'confidence_score', 'problem_solving_score',
            'overall_feedback', 'strengths', 'areas_for_improvement',
            'recommendations', 'interviewer_avatar_url', 'recording_url',
            'transcript', 'response_times', 'filler_words_count',
            'speaking_pace', 'template_name', 'messages', 'created_at'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'created_at']


class StartSessionSerializer(serializers.Serializer):
    """Serializer for starting a new interview session"""
    title = serializers.CharField(max_length=255)
    job_role = serializers.CharField(max_length=255, required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    mode = serializers.ChoiceField(choices=['practice', 'simulation'], default='practice')
    template_id = serializers.UUIDField(required=False, allow_null=True)


class CandidateResponseSerializer(serializers.Serializer):
    """Serializer for candidate responses during interview"""
    response_text = serializers.CharField()
    audio_url = serializers.URLField(required=False, allow_blank=True)
    timestamp = serializers.FloatField(default=0)


class EndSessionSerializer(serializers.Serializer):
    """Serializer for ending an interview session"""
    pass  # No additional fields needed
