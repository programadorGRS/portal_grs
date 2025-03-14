from django.contrib import admin
from .models import *

# Registrar os modelos para aparecerem no admin
admin.site.register(Usuario)
admin.site.register(Tela)
admin.site.register(Empresa)
admin.site.register(AcessoTela)
admin.site.register(AcessoEmpresa)
admin.site.register(Funcionario)
admin.site.register(Absenteismo)
admin.site.register(Convocacao)