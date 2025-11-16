"""
Management command to set up default modules and free plan.
"""
from django.core.management.base import BaseCommand
from apps.modules.models import Module


class Command(BaseCommand):
    help = 'Initialize default modules in the marketplace'
    
    def handle(self, *args, **kwargs):
        modules_data = [
            {
                'code': 'ats_checker',
                'name': 'ATS Score Checker',
                'description': 'Check your CV ATS compatibility score unlimited times. Get 1 free detailed report, then pay 4.99 TND per analysis.',
                'icon': 'file-check',
                'price_monthly': 4.99,
                'price_annual': 49.90,
                'price_lifetime': 99.00,
                'trial_days': 0,  # 1 free use included
                'category': 'CV Analysis',
                'tags': ['ATS', 'Score', 'Free', 'CV Check'],
                'features': [
                    '✅ ATS compatibility score (0-100)',
                    '✅ Basic formatting issues detection',
                    '✅ Keyword analysis',
                    '🎁 1 FREE detailed report',
                    '📊 Section-by-section scoring',
                    '💡 Actionable improvement suggestions',
                    '🔄 Track score improvements over time',
                    '💳 Pay-per-use: 4.99 TND per analysis',
                ],
            },
            {
                'code': 'cv_job_matcher',
                'name': 'CV-Job Matcher',
                'description': 'Match your CV against job descriptions to see how well you fit. Get 1 free match, then 9.99 TND per match.',
                'icon': 'target',
                'price_monthly': 9.99,
                'price_annual': 99.90,
                'price_lifetime': 199.00,
                'trial_days': 0,  # 1 free match included
                'category': 'Job Matching',
                'tags': ['Matching', 'Job', 'Skills', 'Free'],
                'features': [
                    '🎁 1 FREE job match',
                    '📊 Match score percentage',
                    '✅ Matched skills highlighted',
                    '❌ Missing skills identification',
                    '📝 Detailed gap analysis',
                    '💡 Recommendations to improve fit',
                    '🎯 Compare multiple job descriptions',
                    '💳 Pay-per-use: 9.99 TND per match',
                ],
            },
            {
                'code': 'advanced_cv_analyzer',
                'name': 'Advanced CV Analyzer',
                'description': 'Comprehensive AI-powered CV analysis with GPT-4. Get expert insights on strengths, weaknesses, and career recommendations. Includes real-time AI chat.',
                'icon': 'sparkles',
                'price_monthly': 19.99,
                'price_annual': 199.90,
                'price_lifetime': 399.00,
                'trial_days': 0,  # 1 free analysis
                'category': 'Premium AI',
                'tags': ['Premium', 'AI', 'GPT-4', 'Chatbot'],
                'features': [
                    '🤖 GPT-4 powered analysis',
                    '💪 Detailed strengths assessment',
                    '⚠️ Weaknesses identification',
                    '💡 Improvement suggestions',
                    '🎯 Career path recommendations',
                    '💬 Real-time AI chat with Llama 3.1',
                    '📊 Comprehensive professional feedback',
                    '💳 Pay-per-use: 19.99 TND per analysis',
                ],
            },
            {
                'code': 'interview_simulator',
                'name': 'Real-time Interview Simulation',
                'description': 'Practice interviews with AI in real-time. Get instant feedback on your performance, communication skills, and technical knowledge. Video-based with AI interviewer avatar.',
                'icon': 'video',
                'price_monthly': 24.99,
                'price_annual': 249.90,
                'price_lifetime': 499.00,
                'trial_days': 0,  # 1 free session
                'category': 'Interview Prep',
                'tags': ['Interview', 'Practice', 'AI', 'Video', 'Real-time'],
                'features': [
                    '🎁 1 FREE practice session',
                    '🎥 Video-based AI interviewer',
                    '🗣️ Real-time conversation with AI',
                    '📊 Performance scoring (technical, communication, confidence)',
                    '⏱️ Response time analytics',
                    '💬 Full transcript with analysis',
                    '📝 Detailed feedback report',
                    '🎯 Custom interview scenarios',
                    '📈 Track improvement over time',
                    '🔊 Speaking pace & filler words analysis',
                    '💳 Pay-per-use: 24.99 TND per session',
                ],
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for module_data in modules_data:
            module, created = Module.objects.update_or_create(
                code=module_data['code'],
                defaults=module_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created module: {module.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated module: {module.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: {created_count} created, {updated_count} updated'
        ))
