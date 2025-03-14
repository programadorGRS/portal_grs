# portal_grs/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # URL para admin
    path('adminGRS/', admin.site.urls),
    
    # Favicon - usando uma abordagem mais simples
    path('favicon.ico', RedirectView.as_view(
        url=settings.STATIC_URL + 'dashboard/images/favicon.ico', 
        permanent=True
    )),
    
    # Incluir todas as URLs do app dashboard
    path('', include('dashboard.urls')),
]

# Arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
# Handlers para erros em produção
handler404 = 'dashboard.views.custom_404'
handler500 = 'dashboard.views.custom_500'