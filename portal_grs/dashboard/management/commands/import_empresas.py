import os
import sys
import django
import requests
import json

# Adiciona o diretório do projeto ao path para encontrar o módulo settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_grs.settings')
django.setup()

# Importar o modelo Empresa
from dashboard.models import Empresa

# Fazer a requisição para API
url = 'https://ws1.soc.com.br/WebSoc/exportadados?parametro='
parametros = {"empresa":"423","codigo":"26625","chave":"7e9da216f3bfda8c024b","tipoSaida":"json"}
print("Conectando à API...")
response = requests.get(url=url + str(parametros))
data = response.content.decode('latin-1')
empresas = json.loads(data)

# Verificar formato dos dados
if isinstance(empresas, dict) and 'registros' in empresas:
    empresas = empresas['registros']
elif isinstance(empresas, dict) and 'empresas' in empresas:
    empresas = empresas['empresas']

# Contador para acompanhamento
total = 0

print(f"Processando {len(empresas)} empresas...")

# Processar cada empresa
for empresa in empresas:
    try:
        codigo = int(empresa.get('CODIGO', 0))
        if codigo <= 0:
            continue
            
        # Criar ou atualizar empresa
        obj, created = Empresa.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nome_abreviado': empresa.get('NOMEABREVIADO', '')[:60],
                'razao_social_inicial': empresa.get('RAZAOSOCIALINICIAL', '')[:200],
                'razao_social': empresa.get('RAZAOSOCIAL', '')[:200],
                'endereco': empresa.get('ENDERECO', '')[:110],
                'numero_endereco': empresa.get('NUMEROENDERECO', '')[:20],
                'complemento_endereco': empresa.get('COMPLEMENTOENDERECO', '')[:300],
                'bairro': empresa.get('BAIRRO', '')[:80],
                'cidade': empresa.get('CIDADE', '')[:50],
                'cep': empresa.get('CEP', '')[:11],
                'uf': empresa.get('UF', '')[:2],
                'cnpj': empresa.get('CNPJ', '')[:20],
                'inscricao_estadual': empresa.get('INSCRICAOESTADUAL', '')[:20],
                'inscricao_municipal': empresa.get('INSCRICAOMUNICIPAL', '')[:20],
                'ativo': int(empresa.get('ATIVO', 1)) == 1,
                'codigo_cliente_integracao': empresa.get('CODIGOCLIENTEINTEGRACAO', '')[:20],
                'codigo_cliente_int': empresa.get('CÓD. CLIENTE (INT.)', '')[:30],
            }
        )
        
        status = "Criada" if created else "Atualizada"
        print(f"{status} empresa: {codigo} - {empresa.get('NOMEABREVIADO', '')}")
        total += 1
        
    except Exception as e:
        print(f"Erro ao processar empresa {empresa.get('CODIGO', 'N/A')}: {e}")

print(f"Importação concluída. Total de empresas processadas: {total}")