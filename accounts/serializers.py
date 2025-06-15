from rest_framework import serializers
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'password', 'password_repeat']

    def validate(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_repeat')
        return User.objects.create_user(**validated_data)



class CompleteProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password', 'password_repeat']

    def validate(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.set_password(validated_data['password'])
        instance.is_profile_completed = True
        instance.save()
        return instance