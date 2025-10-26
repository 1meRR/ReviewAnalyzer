from __future__ import annotations

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from reviews.models import Review
from reviews.services import detect_sentiment
from users.models import User


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product_name', 'author', 'content', 'rating', 'sentiment', 'source', 'created_at', 'updated_at']
        read_only_fields = ('sentiment', 'created_at', 'updated_at', 'source')

    def create(self, validated_data):
        request = self.context.get('request')
        review = Review(**validated_data)
        if request and request.user.is_authenticated:
            review.analyzed_by = request.user
        review.sentiment = detect_sentiment(review.content)
        review.save()
        return review

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.sentiment = detect_sentiment(instance.content)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        validate_password(password)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Неверные данные')
        attrs['user'] = user
        return attrs
