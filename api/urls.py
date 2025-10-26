from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AnalysisViewSet, ReviewViewSet, UserViewSet, analysis_overview, login_view

router = DefaultRouter()
router.register('reviews', ReviewViewSet, basename='review')
router.register('analysis', AnalysisViewSet, basename='analysis')
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('analysis/summary/', analysis_overview, name='analysis_overview'),
    path('login/', login_view, name='login'),
]
