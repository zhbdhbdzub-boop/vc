from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_new

router = DefaultRouter()
router.register('cvs', views.CVViewSet, basename='cv')
router.register('skills', views.SkillViewSet, basename='skill')
router.register('jobs', views.JobPostingViewSet, basename='job')
router.register('matches', views.JobMatchViewSet, basename='match')

# New CV Analysis Module ViewSets
router.register('ats-checker', views_new.ATSCheckerViewSet, basename='ats-checker')
router.register('cv-job-matcher', views_new.CVJobMatcherViewSet, basename='cv-job-matcher')
router.register('advanced-cv-analyzer', views_new.AdvancedCVAnalyzerViewSet, basename='advanced-cv-analyzer')

app_name = 'cv_analysis'
urlpatterns = [
    path('', include(router.urls)),
    path('match/', views.match_cv_to_jobs, name='match-cv'),
    path('statistics/cvs/', views.cv_statistics, name='cv-statistics'),
    path('statistics/jobs/', views.job_statistics, name='job-statistics'),
]
