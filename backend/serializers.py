from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class PasswordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Passwords
        fields = ('website', 'username', 'password')
        
class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ('title', 'url', 'visited')
        

class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ('created_at', 'data')
        
        

class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = '__all__'
        
class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = ('hardware_id','OS_VERSION')
        
        
class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.CharField(write_only=True)  

    class Meta:
        model = CustomUser  
        fields = ['username', 'password', 'password2', 'email', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'email': {'required': False, 'allow_blank': True}, 
        }

    def save(self):
        if self.validated_data['password'] != self.validated_data['password2']:
            raise serializers.ValidationError({'password': 'Password1 and password2 must match'})

        email = self.validated_data.get('email', None)
        if email and CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})

        role = self.validated_data.get('role') 
        account = CustomUser(
            username=self.validated_data['username'],
            email=email
        )
        account.set_password(self.validated_data['password'])
        account.save()

        account.role = role
        account.save()

        return account

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['role'] = user.role  

        return token
