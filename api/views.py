from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from reviews.models import Review
from reviews.services import build_sentiment_summary

from . import authentication
from .serializers import LoginSerializer, ReviewSerializer, UserSerializer

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer; queryset = Review.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        product = self.request.query_params.get('product')
        return qs.filter(product_name__icontains=product) if product else qs


class AnalysisViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        summary = {item['sentiment']: item['count'] for item in Review.objects.values('sentiment').annotate(count=Count('id'))}
        data = {'positive': summary.get('positive', 0), 'neutral': summary.get('neutral', 0), 'negative': summary.get('negative', 0)}
        data['total'] = sum(data.values())
        return Response(data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all(); serializer_class = UserSerializer; permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data); serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    return Response({'access': authentication.encode({'user_id': user.id, 'username': user.username})})


@api_view(['GET'])
def analysis_overview(request):
    return Response(build_sentiment_summary(Review.objects.all()))
