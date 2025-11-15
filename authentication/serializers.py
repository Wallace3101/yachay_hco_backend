# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    firstName = serializers.CharField(source='first_name', read_only=True)
    lastName = serializers.CharField(source='last_name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'firstName', 'lastName', 'is_staff', 'is_superuser', 'createdAt', 'updatedAt')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Intentar autenticación por username o email
            user = authenticate(username=username, password=password)
            if not user:
                # Si no funciona por username, intentar por email
                try:
                    user_by_email = User.objects.get(email=username)
                    user = authenticate(username=user_by_email.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('Credenciales inválidas')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Debe incluir username/email y password')

# NUEVO SERIALIZER PARA GOOGLE AUTH
class GoogleAuthSerializer(serializers.Serializer):
    idToken = serializers.CharField(required=True)
    
    def validate_idToken(self, value):
        if not value:
            raise serializers.ValidationError("ID Token es requerido")
        return value