#!/usr/bin/env python
"""
Script para importação de convocações de exames através do Django.
Pode ser executado diretamente ou através do shell do Django.
"""
import os
import sys
import subprocess

# Definir o caminho do projeto e configurar o ambiente
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

# Verificar se estamos no shell do Django
def is_django_shell():
    return 'django' in sys.modules and hasattr(sys, 'ps1')

# Se não estiver no shell do Django, configurar o ambiente Django manualmente
if not is_django_shell():
    try:
        print("Configurando ambiente Django diretamente...")
        
        # Configurar o módulo de configurações
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_grs.settings')
        
        # Se não é o shell interativo, importar django e configurar
        import django
        django.setup()
        print("Ambiente Django configurado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao configurar o ambiente Django: {e}")
        
        # Tentar via django-admin como último recurso
        try:
            print("Tentando via django-admin...")
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_grs.settings')
            comando = f"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_grs.settings'); exec(open('{__file__}').read())"
            subprocess.run([sys.executable, '-m', 'django', 'shell', '-c', comando], check=True)
            sys.exit(0)
        except Exception as e2:
            print(f"Erro ao tentar via django-admin: {e2}")
            sys.exit(1)

print("Executando importação de convocações de exames...")

import requests
import json
from datetime import datetime
from django.db import transaction

# Importar modelos - já estamos no ambiente Django
from dashboard.models import Empresa, Funcionario, Convocacao

# Credenciais e parâmetros - URL atualizada para GRS Manager
GRS_CONNECT_URL = "https://www.grsconnect.com.br"  # URL correta conforme documentação
GRS_CONNECT_USER = 1  # Número do usuário (int)
GRS_CONNECT_PASS = "ConnectBI@20482022"  # Chave de integração
WEBSOC_URL = 'https://ws1.soc.com.br/WebSoc/exportadados?parametro='
WEBSOC_EMPRESA = "423"
WEBSOC_CODIGO = "151346"
WEBSOC_CHAVE = "b5aa04943cd28ff155ed"

def get_grs_connect_token():
    """Obtém token de autenticação da API GRS Manager"""
    try:
        # Usar o endpoint get_token conforme documentação
        response = requests.get(
            f"{GRS_CONNECT_URL}/get_token",
            params={
                "username": str(GRS_CONNECT_USER),
                "password": GRS_CONNECT_PASS
            }
        )
        
        if response.status_code != 200:
            # Tratar mensagens de erro específicas
            error_message = "Erro desconhecido"
            try:
                error_data = response.json()
                if 'message' in error_data:
                    error_message = error_data['message']
            except:
                pass
                
            if "Username ou password invalido" in error_message:
                print("Credenciais inválidas. Verifique seu username e password.")
            elif "Providencie username e password" in error_message:
                print("Parâmetros incompletos. Username e password são obrigatórios.")
            else:
                print(f"Erro na autenticação: {error_message}")
                print(f"Resposta completa: {response.text}")
            
            return None
            
        data = response.json()
        if 'token' not in data:
            print(f"Token não encontrado na resposta: {data}")
            return None
            
        print("Token obtido com sucesso!")
        return data.get('token')
        
    except Exception as e:
        print(f"Erro ao obter token da API GRS Manager: {e}")
        return None

def get_solicitacoes(token):
    """Obtém todas as solicitações da API GRS Manager"""
    try:
        # Usar o endpoint get_ped_proc com o token
        response = requests.get(
            f"{GRS_CONNECT_URL}/get_ped_proc",
            params={"token": token}
        )
        
        if response.status_code != 200:
            # Tratar mensagens de erro específicas para tokens
            error_message = "Erro desconhecido"
            try:
                error_data = response.json()
                if 'message' in error_data:
                    error_message = error_data['message']
            except:
                pass
                
            if "Token expirado" in error_message:
                print("O token expirou. Solicite um novo token.")
            elif "Token invalido" in error_message:
                print("O token fornecido é inválido.")
            elif "Providencie um token" in error_message:
                print("Token não fornecido na requisição.")
            else:
                print(f"Erro ao obter solicitações: {error_message}")
                print(f"Resposta completa: {response.text}")
                
            return []
        
        # Verificar se a resposta é válida
        data = response.json()
        if not isinstance(data, list) and not (isinstance(data, dict) and 'registros' in data):
            print(f"Formato de resposta inesperado: {data}")
            return []
            
        # Extrair registros se estiverem em um objeto
        if isinstance(data, dict) and 'registros' in data:
            return data['registros']
            
        return data
        
    except Exception as e:
        print(f"Erro ao listar solicitações: {e}")
        return []

def get_exames_convocacao(cod_empresa, cod_solicitacao):
    """Obtém dados detalhados de exames da API WebSoc usando código de solicitação"""
    try:
        parametros = {
            "empresa": WEBSOC_EMPRESA,
            "codigo": WEBSOC_CODIGO, 
            "chave": WEBSOC_CHAVE,
            "tipoSaida": "json",
            "empresaTrabalho": str(cod_empresa),
            "codigoSolicitacao": str(cod_solicitacao)
        }
        
        # Converter para JSON string
        parametros_str = json.dumps(parametros)
        
        # Fazer requisição
        print(f"Consultando WebSoc para empresa {cod_empresa}, solicitação {cod_solicitacao}")
        print(f"URL completa: {WEBSOC_URL + parametros_str}")
        
        response = requests.get(WEBSOC_URL + parametros_str, timeout=60)
        
        if response.status_code != 200:
            print(f"Erro ao consultar WebSoc: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            return []
        
        # Decodificar resposta
        data = response.content.decode('latin-1')
        
        try:
            exames_data = json.loads(data)
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON para empresa {cod_empresa}. Resposta: {data[:200]}...")
            return []
        
        # Verificar formato dos dados
        registros = []
        if isinstance(exames_data, dict):
            if 'registros' in exames_data:
                registros = exames_data['registros']
            elif 'exames' in exames_data:
                registros = exames_data['exames']
            elif len(exames_data) > 0:
                # Talvez os registros estejam diretamente no dicionário raiz
                registros = [exames_data]
        elif isinstance(exames_data, list):
            registros = exames_data
        
        if not registros:
            print(f"Nenhum exame encontrado para empresa {cod_empresa}, solicitação {cod_solicitacao}")
            
        return registros
        
    except Exception as e:
        print(f"Erro ao consultar WebSoc para empresa {cod_empresa}: {e}")
        import traceback
        print(traceback.format_exc())  # Imprimir traceback completo para diagnóstico
        return []

def processar_data(data_str):
    """Converte uma string de data para objeto date"""
    if not data_str:
        return None
        
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(data_str, fmt).date()
        except ValueError:
            continue
    return None

def criar_ou_atualizar_funcionario(empresa_db, codigo_funcionario, cpf, nome, matricula, data_admissao, **kwargs):
    """Cria ou atualiza um funcionário no banco de dados"""
    funcionario = None
    
    # Verificar se o funcionário já existe
    if cpf:
        funcionario = Funcionario.objects.filter(cpf=cpf).first()
    
    if not funcionario and codigo_funcionario:
        funcionario = Funcionario.objects.filter(codigo=codigo_funcionario).first()
    
    if not funcionario and matricula:
        funcionario = Funcionario.objects.filter(
            empresa=empresa_db,
            matricula_funcionario=matricula
        ).first()
    
    # Se não existir, criar um novo
    if not funcionario:
        funcionario = Funcionario(
            empresa=empresa_db,
            codigo=codigo_funcionario,
            codigo_empresa=empresa_db.codigo,
            nome_empresa=empresa_db.nome_abreviado,
            nome=nome,
            cpf=cpf,
            matricula_funcionario=matricula,
            data_admissao=data_admissao,
            **kwargs
        )
        funcionario.save()
        print(f"Criado funcionário: {nome} (CPF: {cpf})")
    else:
        # Atualizar dados do funcionário existente
        funcionario.empresa = empresa_db
        if codigo_funcionario and not funcionario.codigo:
            funcionario.codigo = codigo_funcionario
        if cpf and not funcionario.cpf:
            funcionario.cpf = cpf
        if nome and not funcionario.nome:
            funcionario.nome = nome
        if matricula and not funcionario.matricula_funcionario:
            funcionario.matricula_funcionario = matricula
        if data_admissao and not funcionario.data_admissao:
            funcionario.data_admissao = data_admissao
        
        # Atualizar campos adicionais
        for key, value in kwargs.items():
            if value and not getattr(funcionario, key, None):
                setattr(funcionario, key, value)
        
        funcionario.save()
        print(f"Atualizado funcionário: {funcionario.nome} (CPF: {funcionario.cpf})")
    
    return funcionario

def main():
    # Obter token de autenticação
    print("Obtendo token de autenticação...")
    token = get_grs_connect_token()
    
    if not token:
        print("Não foi possível obter token de autenticação. Abortando.")
        return
    
    # Obter lista de solicitações
    print("Obtendo lista de solicitações...")
    solicitacoes = get_solicitacoes(token)
    
    if not solicitacoes:
        print("Não foi possível obter solicitações. Abortando.")
        return
        
    print(f"Obtidas {len(solicitacoes)} solicitações no total.")
    
    # Mostrar alguns exemplos para verificar formato
    for i, solicitacao in enumerate(solicitacoes[:3]):
        print(f"Solicitação {i+1}: cod_empresa={solicitacao.get('cod_empresa')}, cod_solicitacao={solicitacao.get('cod_solicitacao')}")
    
    # Obter empresas ativas do banco de dados
    empresas_db = {str(empresa.codigo): empresa for empresa in Empresa.objects.filter(ativo=True)}
    
    if not empresas_db:
        print("Não há empresas ativas no banco de dados. Abortando.")
        return
        
    print(f"Encontradas {len(empresas_db)} empresas ativas no banco de dados.")
    
    # Filtrar solicitações para empresas que existem no banco
    solicitacoes_validas = []
    for solicitacao in solicitacoes:
        cod_empresa = str(solicitacao.get('cod_empresa'))
        if cod_empresa in empresas_db:
            solicitacoes_validas.append(solicitacao)
    
    print(f"Encontradas {len(solicitacoes_validas)} solicitações para empresas existentes no banco.")
    
    # Processar cada solicitação válida
    total_convocacoes = 0
    total_empresas_processadas = 0
    
    for solicitacao in solicitacoes_validas:
        try:
            cod_empresa = str(solicitacao.get('cod_empresa'))
            cod_solicitacao = str(solicitacao.get('cod_solicitacao'))
            empresa_db = empresas_db[cod_empresa]
            
            print(f"\nProcessando empresa: {empresa_db.codigo} - {empresa_db.nome_abreviado}, Solicitação: {cod_solicitacao}")
            
            # Obter dados de exames para esta empresa/solicitação
            exames = get_exames_convocacao(cod_empresa, cod_solicitacao)
            
            if not exames:
                print(f"Nenhum exame encontrado para empresa {cod_empresa}, solicitação {cod_solicitacao}")
                continue
                
            print(f"Obtidos {len(exames)} exames para empresa {cod_empresa}")
            
            # Usar transação para garantir consistência
            with transaction.atomic():
                for exame in exames:
                    try:
                        # Extrair dados do exame
                        codigo_empresa = exame.get('CODIGOEMPRESA')
                        nome_abreviado = exame.get('NOMEABREVIADO')
                        unidade = exame.get('UNIDADE')
                        cidade = exame.get('CIDADE')
                        estado = exame.get('ESTADO')
                        bairro = exame.get('BAIRRO')
                        endereco = exame.get('ENDERECO')
                        cep = exame.get('CEP')
                        cnpj_unidade = exame.get('CNPJUNIDADE')
                        setor = exame.get('SETOR')
                        cargo = exame.get('CARGO')
                        codigo_funcionario = exame.get('CODIGOFUNCIONARIO')
                        cpf = exame.get('CPFFUNCIONARIO')
                        matricula = exame.get('MATRICULA')
                        data_admissao_str = exame.get('DATAADMISSAO')
                        nome_funcionario = exame.get('NOME')
                        email_funcionario = exame.get('EMAILFUNCIONARIO')
                        telefone_funcionario = exame.get('TELEFONEFUNCIONARIO')
                        codigo_exame = exame.get('CODIGOEXAME')
                        nome_exame = exame.get('EXAME')
                        ultimo_pedido_str = exame.get('ULTIMOPEDIDO')
                        data_resultado_str = exame.get('DATARESULTADO')
                        periodicidade_str = exame.get('PERIODICIDADE', '12')
                        refazer_str = exame.get('REFAZER', '')
                        
                        # Converter datas
                        data_admissao = processar_data(data_admissao_str)
                        ultimo_pedido = processar_data(ultimo_pedido_str)
                        data_resultado = processar_data(data_resultado_str)
                        refazer_date = processar_data(refazer_str)  # Agora tratamos como data
                        
                        # Converter periodicidade para inteiro
                        try:
                            periodicidade = int(periodicidade_str)
                            if periodicidade <= 0:
                                periodicidade = 12
                        except (ValueError, TypeError):
                            periodicidade = 12
                        
                        # Criar ou atualizar funcionário
                        funcionario_info = {
                            'nome_unidade': unidade,
                            'nome_setor': setor,
                            'nome_cargo': cargo,
                            'email': email_funcionario,
                            'telefone_celular': telefone_funcionario
                        }
                        
                        funcionario = criar_ou_atualizar_funcionario(
                            empresa_db=empresa_db,
                            codigo_funcionario=codigo_funcionario,
                            cpf=cpf,
                            nome=nome_funcionario,
                            matricula=matricula,
                            data_admissao=data_admissao,
                            **funcionario_info
                        )
                        
                        # Preparar dados para criar/atualizar a convocação
                        convocacao_data = {
                            'empresa': empresa_db,
                            'funcionario': funcionario,  # Agora garantimos que temos um funcionário
                            'codigo_empresa': codigo_empresa or empresa_db.codigo,
                            'nome_abreviado': nome_abreviado or empresa_db.nome_abreviado,
                            'unidade': unidade or '',
                            'cidade': cidade or empresa_db.cidade,
                            'estado': estado or empresa_db.uf,
                            'bairro': bairro or empresa_db.bairro,
                            'endereco': endereco or empresa_db.endereco,
                            'cep': cep or empresa_db.cep,
                            'cnpj_unidade': cnpj_unidade or empresa_db.cnpj,
                            'setor': setor or '',
                            'cargo': cargo or '',
                            'codigo_funcionario': codigo_funcionario,
                            'cpf_funcionario': cpf or '',
                            'matricula': matricula or '',
                            'data_admissao': data_admissao,
                            'nome': nome_funcionario or '',
                            'email_funcionario': email_funcionario or '',
                            'telefone_funcionario': telefone_funcionario or '',
                            'codigo_exame': codigo_exame or '',
                            'exame': nome_exame or '',
                            'ultimo_pedido': ultimo_pedido,
                            'data_resultado': data_resultado,
                            'periodicidade': periodicidade,
                            'refazer': refazer_date  # Agora é um campo de data
                        }
                        
                        # Verificar se já existe uma convocação com os mesmos dados
                        convocacao_existente = Convocacao.objects.filter(
                            empresa=empresa_db,
                            funcionario=funcionario,
                            codigo_exame=convocacao_data['codigo_exame']
                        ).first()
                        
                        if convocacao_existente:
                            # Atualizar convocação existente
                            for key, value in convocacao_data.items():
                                if value is not None:  # Só atualizar valores não nulos
                                    setattr(convocacao_existente, key, value)
                            convocacao_existente.save()
                            print(f"Atualizada convocação para {nome_funcionario} - {convocacao_data['exame']}")
                        else:
                            # Criar nova convocação
                            convocacao = Convocacao(**convocacao_data)
                            convocacao.save()
                            print(f"Criada convocação para {nome_funcionario} - {convocacao_data['exame']}")
                        
                        total_convocacoes += 1
                        
                    except Exception as e:
                        print(f"Erro ao processar exame: {str(e)}")
                        # Imprimir dados do exame para depuração
                        print(f"Dados do exame: {json.dumps(exame, default=str)}")
                        import traceback
                        print(traceback.format_exc())  # Imprimir traceback para melhor diagnóstico
            
            total_empresas_processadas += 1
            
        except Exception as e:
            print(f"Erro ao processar solicitação para empresa {cod_empresa}: {str(e)}")
            import traceback
            print(traceback.format_exc())  # Imprimir traceback para melhor diagnóstico
    
    print(f"\nImportação concluída. Total de empresas processadas: {total_empresas_processadas}")
    print(f"Total de convocações criadas/atualizadas: {total_convocacoes}")

# Executar a função principal
if __name__ == "__main__":
    main()