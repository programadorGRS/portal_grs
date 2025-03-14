from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [

    path('', views.login_view, name='login'),

    path('login/', auth_views.LoginView.as_view(
        template_name='dashboard/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True
    ), name='login_auth'),
    
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/protected/', views.ProtectedView.as_view(), name='protected'),
    path('update_settings/', views.update_settings, name='update_settings'),
    path('funcionarios/', views.funcionarios_view, name='funcionarios'),
    path('api/funcionarios/<int:id>/', views.get_funcionario_api, name='get_funcionario_api'),
    path('absenteismo/', views.absenteismo_view, name='absenteismo'),
    path('convocacoes/', views.convocacao_view, name='convocacao'),
    path('api/convocacoes/funcionario/<int:funcionario_id>/', views.get_funcionario_convocacoes_api, name='get_funcionario_convocacoes_api'),
    path('api/convocacoes/export-all/', views.export_convocacoes_all_api, name='export_convocacoes_all'),
]