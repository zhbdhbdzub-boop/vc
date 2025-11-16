"""
Script to populate the marketplace with sample modules
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.modules.models import Module

# Clear existing modules
Module.objects.all().delete()

# Create modules
modules_data = [
    {
        'name': 'CV-Job Matcher',
        'code': 'cv_job_matcher',
        'description': 'AI-powered CV analysis that matches your resume with real job opportunities from Google Jobs. Uses Llama 3.1 for intelligent matching across 15 countries.',
        'category': 'cv_analysis',
        'price_monthly': 29.99,
        'is_active': True,
        'icon': 'briefcase',
        'features': [
            'Real-time job scraping from Google Jobs',
            'AI-powered matching using Llama 3.1',
            '15 country support',
            'Customizable matching rate threshold',
            'Direct job application links',
            'Salary information when available'
        ]
    },
    {
        'name': 'ATS Checker',
        'code': 'ats_checker',
        'description': 'Comprehensive ATS (Applicant Tracking System) compatibility checker. Analyzes your CV for ATS optimization using Llama 3.1 AI to ensure maximum visibility.',
        'category': 'cv_analysis',
        'price_monthly': 19.99,
        'is_active': True,
        'icon': 'check-circle',
        'features': [
            'ATS compatibility score (0-100)',
            'Keyword optimization analysis',
            'Missing sections detection',
            'Contact information validation',
            'Action verbs and quantified achievements analysis',
            'Actionable improvement suggestions'
        ]
    },
    {
        'name': 'Advanced CV Analyzer',
        'code': 'advanced_analyzer',
        'description': 'Deep dive into your CV with comprehensive analysis including skills extraction, experience evaluation, and education assessment.',
        'category': 'cv_analysis',
        'price_monthly': 24.99,
        'is_active': True,
        'icon': 'file-text',
        'features': [
            'Skills extraction and categorization',
            'Experience timeline analysis',
            'Education verification',
            'Language proficiency detection',
            'Certifications tracking',
            'Career progression insights'
        ]
    },
    {
        'name': 'Interview Simulator',
        'code': 'interview_simulator',
        'description': 'Practice technical and behavioral interviews with AI-powered feedback. Get real-time coaching and improve your interview performance.',
        'category': 'interview_prep',
        'price_monthly': 34.99,
        'is_active': True,
        'icon': 'mic',
        'features': [
            'Technical interview practice',
            'Behavioral question simulation',
            'Speech-to-text integration',
            'Text-to-speech responses',
            'Performance scoring',
            'Industry-specific scenarios'
        ]
    },
    {
        'name': 'Code Assessment',
        'code': 'code_assessment',
        'description': 'Evaluate coding skills with automated assessments and detailed feedback across multiple programming languages.',
        'category': 'technical_assessment',
        'price_monthly': 39.99,
        'is_active': True,
        'icon': 'code',
        'features': [
            'Multi-language support',
            'Automated test execution',
            'Code quality analysis',
            'Performance benchmarking',
            'Detailed feedback reports',
            'Custom assessment creation'
        ]
    },
    {
        'name': 'Salary Insights',
        'code': 'salary_insights',
        'description': 'Get accurate salary data and market insights for your role and location. Make informed career decisions.',
        'category': 'career_tools',
        'price_monthly': 14.99,
        'is_active': True,
        'icon': 'dollar-sign',
        'features': [
            'Market salary data by role',
            'Location-based compensation',
            'Experience-level ranges',
            'Benefits analysis',
            'Negotiation strategies',
            'Career growth projections'
        ]
    }
]

# Create modules
for module_data in modules_data:
    module = Module.objects.create(**module_data)
    print(f'Created module: {module.name} (${module.price_monthly}/month)')

print(f'\nSuccessfully created {len(modules_data)} modules!')
