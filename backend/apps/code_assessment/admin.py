from django.contrib import admin
from .models import (
    CodingProblem,
    TestCase,
    Submission,
    TestCaseResult,
    UserProgress,
    CodeExecutionSession,
)


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ['input_data', 'expected_output', 'is_hidden', 'is_sample', 'weight']


@admin.register(CodingProblem)
class CodingProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'category', 'max_score', 'is_public', 'acceptance_rate', 'created_at']
    list_filter = ['difficulty', 'category', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TestCaseInline]
    readonly_fields = ['total_submissions', 'accepted_submissions', 'acceptance_rate', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['tenant', 'title', 'slug', 'description', 'difficulty', 'category', 'tags']
        }),
        ('Problem Details', {
            'fields': ['input_format', 'output_format', 'constraints', 'examples']
        }),
        ('Code Templates', {
            'fields': ['python_template', 'javascript_template', 'java_template'],
            'classes': ['collapse']
        }),
        ('Limits & Scoring', {
            'fields': ['max_score', 'time_limit_seconds', 'memory_limit_mb']
        }),
        ('Metadata', {
            'fields': ['is_public', 'created_by', 'created_at', 'updated_at']
        }),
        ('Statistics', {
            'fields': ['total_submissions', 'accepted_submissions', 'acceptance_rate'],
            'classes': ['collapse']
        }),
    ]


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem', 'is_hidden', 'is_sample', 'weight', 'created_at']
    list_filter = ['is_hidden', 'is_sample', 'problem__difficulty']
    search_fields = ['problem__title']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'problem', 'language', 'status', 'score', 'submitted_at']
    list_filter = ['status', 'language', 'submitted_at']
    search_fields = ['user__email', 'problem__title']
    readonly_fields = ['submitted_at', 'completed_at']
    
    fieldsets = [
        ('Submission Info', {
            'fields': ['tenant', 'user', 'problem', 'language', 'status']
        }),
        ('Code', {
            'fields': ['code'],
            'classes': ['collapse']
        }),
        ('Results', {
            'fields': ['score', 'passed_test_cases', 'total_test_cases', 'execution_time_ms', 'memory_used_mb']
        }),
        ('Error Details', {
            'fields': ['error_message', 'failed_test_case'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['submitted_at', 'completed_at']
        }),
    ]


@admin.register(TestCaseResult)
class TestCaseResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission', 'test_case', 'passed', 'execution_time_ms']
    list_filter = ['passed']
    search_fields = ['submission__user__email', 'test_case__problem__title']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'is_solved', 'best_score', 'attempts_count', 'solved_at']
    list_filter = ['is_solved', 'is_attempted']
    search_fields = ['user__email', 'problem__title']
    readonly_fields = ['first_attempted_at', 'solved_at', 'last_attempted_at']


@admin.register(CodeExecutionSession)
class CodeExecutionSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'problem', 'started_at', 'total_time_seconds', 'submissions_count', 'successful']
    list_filter = ['successful', 'started_at']
    search_fields = ['user__email', 'problem__title']
    readonly_fields = ['started_at', 'ended_at']
