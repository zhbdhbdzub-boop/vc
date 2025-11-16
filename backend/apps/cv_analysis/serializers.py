from rest_framework import serializers
from .models import (
    CV, CVAnalysis, Skill, CVSkill, Experience, Education,
    JobPosting, JobSkill, JobMatch
)


class CVSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CV
        fields = [
            'id', 'tenant', 'user', 'user_email', 'file', 'file_url',
            'filename', 'file_type', 'file_size', 'status',
            'processed_at', 'processing_error',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'user', 'status', 'processed_at', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class CVSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    
    class Meta:
        model = CVSkill
        fields = [
            'id', 'skill', 'skill_name', 'skill_category',
            'proficiency', 'years_experience', 'confidence', 'context'
        ]


class ExperienceSerializer(serializers.ModelSerializer):
    duration_years = serializers.SerializerMethodField()
    
    class Meta:
        model = Experience
        fields = [
            'id', 'company', 'position', 'location',
            'start_date', 'end_date', 'is_current',
            'description', 'achievements', 'duration_months', 'duration_years'
        ]
    
    def get_duration_years(self, obj):
        if obj.duration_months:
            return round(obj.duration_months / 12, 1)
        return None


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'is_current', 'grade', 'description'
        ]


class CVAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVAnalysis
        fields = [
            'id', 'cv', 'full_name', 'email', 'phone', 'location',
            'linkedin_url', 'github_url', 'portfolio_url',
            'professional_summary', 'total_years_experience', 'highest_degree',
            'overall_score', 'experience_score', 'education_score',
            'skills_score', 'formatting_score',
            'strengths', 'weaknesses', 'suggestions',
            'analysis_version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CVDetailSerializer(serializers.ModelSerializer):
    """Detailed CV serializer with nested data"""
    analysis = CVAnalysisSerializer(read_only=True)
    skills = CVSkillSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = CV
        fields = [
            'id', 'tenant', 'user', 'user_email', 'filename', 'file_type',
            'file_size', 'status', 'processed_at', 'processing_error',
            'analysis', 'skills', 'experiences', 'education',
            'created_at', 'updated_at'
        ]


class SkillSerializer(serializers.ModelSerializer):
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'synonyms', 'importance_weight', 'usage_count']
    
    def get_usage_count(self, obj):
        return obj.cv_skills.count()


class JobSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = JobSkill
        fields = ['id', 'skill', 'skill_name', 'requirement_level', 'years_required']


class JobPostingSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    required_skills = JobSkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'tenant', 'created_by', 'created_by_name',
            'title', 'company', 'location',
            'salary_min', 'salary_max', 'description', 'requirements',
            'status', 'external_url', 'source',
            'years_experience_required', 'required_skills',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_by', 'created_at', 'updated_at']


class JobMatchSerializer(serializers.ModelSerializer):
    cv_filename = serializers.CharField(source='cv.filename', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)
    
    class Meta:
        model = JobMatch
        fields = [
            'id', 'cv', 'cv_filename', 'job', 'job_title', 'job_company',
            'overall_score', 'skills_match_score', 'experience_match_score',
            'education_match_score', 'matched_skills', 'missing_skills',
            'match_summary', 'recommendations',
            'is_bookmarked', 'applied_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CVUploadSerializer(serializers.Serializer):
    """Serializer for CV file upload"""
    file = serializers.FileField(required=True)
    
    def validate_file(self, file):
        # Check file type
        valid_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        if file.content_type not in valid_types:
            raise serializers.ValidationError("Only PDF, DOCX, and TXT files are allowed")
        
        # Check file size (10MB max)
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError("File size must be under 10MB")
        
        return file


class JobMatchingSerializer(serializers.Serializer):
    """Serializer for job matching request"""
    cv_id = serializers.IntegerField(required=True)
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=50)
    min_score = serializers.IntegerField(required=False, default=50, min_value=0, max_value=100)
