from rest_framework import serializers
from .models import (
    CodingProblem,
    TestCase,
    Submission,
    TestCaseResult,
    UserProgress,
)


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'input_data', 'expected_output', 'is_hidden', 'is_sample', 'explanation', 'weight']
        read_only_fields = ['id']


class CodingProblemListSerializer(serializers.ModelSerializer):
    acceptance_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = CodingProblem
        fields = [
            'id', 'title', 'slug', 'difficulty', 'category', 'tags',
            'max_score', 'time_limit_seconds', 'total_submissions',
            'accepted_submissions', 'acceptance_rate'
        ]


class CodingProblemDetailSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True)
    sample_test_cases = serializers.SerializerMethodField()
    acceptance_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = CodingProblem
        fields = [
            'id', 'title', 'slug', 'description', 'difficulty', 'category', 'tags',
            'input_format', 'output_format', 'constraints', 'examples',
            'python_template', 'javascript_template', 'java_template',
            'max_score', 'time_limit_seconds', 'memory_limit_mb',
            'total_submissions', 'accepted_submissions', 'acceptance_rate',
            'test_cases', 'sample_test_cases', 'created_at', 'updated_at'
        ]
    
    def get_sample_test_cases(self, obj):
        """Only return sample test cases (not hidden ones)"""
        sample_cases = obj.test_cases.filter(is_sample=True)
        return TestCaseSerializer(sample_cases, many=True).data


class TestCaseResultSerializer(serializers.ModelSerializer):
    test_case = TestCaseSerializer(read_only=True)
    
    class Meta:
        model = TestCaseResult
        fields = [
            'id', 'test_case', 'passed', 'actual_output',
            'execution_time_ms', 'memory_used_mb', 'error_message'
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    test_results = TestCaseResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'problem', 'problem_title', 'user', 'user_email',
            'code', 'language', 'status', 'score',
            'passed_test_cases', 'total_test_cases',
            'execution_time_ms', 'memory_used_mb',
            'error_message', 'test_results',
            'submitted_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'score', 'passed_test_cases',
            'total_test_cases', 'execution_time_ms', 'memory_used_mb',
            'error_message', 'submitted_at', 'completed_at'
        ]


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['problem', 'code', 'language']
    
    def create(self, validated_data):
        # Add user and tenant from request context
        request = self.context.get('request')
        validated_data['user'] = request.user
        validated_data['tenant'] = request.user.tenant
        return super().create(validated_data)


class UserProgressSerializer(serializers.ModelSerializer):
    problem = CodingProblemListSerializer(read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'problem', 'is_solved', 'is_attempted',
            'best_score', 'attempts_count',
            'first_attempted_at', 'solved_at', 'last_attempted_at'
        ]


class ProblemStatisticsSerializer(serializers.Serializer):
    total_problems = serializers.IntegerField()
    easy_count = serializers.IntegerField()
    medium_count = serializers.IntegerField()
    hard_count = serializers.IntegerField()
    solved_count = serializers.IntegerField()
    attempted_count = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_submissions = serializers.IntegerField()
