# dashboard/middleware.py
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.conf import settings
from django.contrib import messages
import time

class SessionControlMiddleware:
    """
    Middleware para controle de sessão e autenticação.
    - Redireciona usuários não autenticados para o login
    - Atualiza o timestamp da última atividade
    - Encerra sessões inativas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Obter a URL atual
        current_url = resolve(request.path_info).url_name
        
        # Lista de URLs que não requerem autenticação
        public_urls = ['login', 'login_auth', 'token_obtain_pair', 
                      'token_refresh', 'token_verify', 'admin:index']
        
        # Lista de URLs que começam com adminGRS
        admin_url = request.path_info.startswith('/adminGRS/')
        
        # Se a URL não é pública e o usuário não está autenticado
        if not (current_url in public_urls or admin_url) and not request.user.is_authenticated:
            # Redirecionar para o login
            return redirect(settings.LOGIN_URL)
        
        # Verificar se a sessão está ativa para usuários autenticados
        if request.user.is_authenticated:
            # Obter o timestamp da última atividade
            last_activity = request.session.get('last_activity', None)
            
            # Verificar se o tempo expirou (30 minutos = 1800 segundos)
            if last_activity and (time.time() - last_activity > settings.SESSION_COOKIE_AGE):
                # Realizar logout e mostrar mensagem
                from django.contrib.auth import logout
                logout(request)
                messages.warning(request, 'Sua sessão expirou devido à inatividade. Por favor, faça login novamente.')
                return redirect(settings.LOGIN_URL)
            
            # Atualizar o timestamp da última atividade
            request.session['last_activity'] = time.time()
            
            # Atualizar a última sessão no banco de dados se for o método Usuario
            if hasattr(request.user, 'registrar_sessao'):
                request.user.registrar_sessao()
            
        # Prosseguir com a requisição
        response = self.get_response(request)
        return response