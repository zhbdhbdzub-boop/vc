"""
Serializers for the 3 CV Analysis modules
"""
from rest_framework import serializers
from .models import (
    CV, ATSAnalysis, CVJobMatch, AdvancedCVAnalysis, 
    ChatMessage, CVAnalysisUsageTracker
)


class CVSerializer(serializers.ModelSerializer):
    """Serializer for CV uploads"""
    
    class Meta:
        model = CV
        fields = ['id', 'filename', 'file', 'file_type', 'file_size', 'status', 'created_at']
        read_only_fields = ['id', 'filename', 'file_type', 'file_size', 'status', 'created_at']


class UsageTrackerSerializer(serializers.ModelSerializer):
    """Serializer for usage tracking"""
    
    class Meta:
        model = CVAnalysisUsageTracker
        fields = ['module_type', 'free_limit', 'used_count', 'can_use_free', 'remaining_uses']
        read_only_fields = fields


class ATSAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for ATS Score Checker results"""
    cv = CVSerializer(read_only=True)
    
    class Meta:
        model = ATSAnalysis
        fields = [
            'id', 'cv', 'ats_score', 'keyword_matches', 'missing_keywords',
            'quick_suggestions', 'has_detailed_report', 'detailed_report',
            'is_free_detailed_report', 'created_at'
        ]
        read_only_fields = fields


class ATSAnalysisRequestSerializer(serializers.Serializer):
    """Request serializer for ATS analysis"""
    cv_file = serializers.FileField(required=True)
    request_detailed_report = serializers.BooleanField(default=False)


class CVJobMatchSerializer(serializers.ModelSerializer):
    """Serializer for CV-Job Matcher results"""
    cv = CVSerializer(read_only=True)
    
    class Meta:
        model = CVJobMatch
        fields = [
            'id', 'cv', 'job_title', 'job_description', 'match_score',
            'matched_skills', 'missing_skills', 'matching_report',
            'recommendations', 'is_free_match', 'created_at'
        ]
        read_only_fields = ['id', 'cv', 'match_score', 'matched_skills', 
                            'missing_skills', 'matching_report', 'recommendations',
                            'is_free_match', 'created_at']


class CVJobMatchRequestSerializer(serializers.Serializer):
    """Request serializer for CV-Job matching"""
    cv_file = serializers.FileField(required=True)
    job_title = serializers.CharField(max_length=255, required=True)
    job_description = serializers.CharField(required=True)


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdvancedCVAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for Advanced CV Analyzer results"""
    cv = CVSerializer(read_only=True)
    
    class Meta:
        model = AdvancedCVAnalysis
        fields = [
            'id', 'cv', 'full_analysis', 'strengths', 'weaknesses',
            'improvement_suggestions', 'career_recommendations',
            'status', 'created_at'
        ]
        read_only_fields = fields


class AdvancedCVAnalysisRequestSerializer(serializers.Serializer):
    """Request serializer for Advanced CV analysis"""
    cv_file = serializers.FileField(required=True)
    job_description = serializers.CharField(required=False, allow_blank=True)


class ChatMessageRequestSerializer(serializers.Serializer):
    """Request serializer for chatbot messages"""
    message = serializers.CharField(required=True)
