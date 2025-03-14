#!/usr/bin/env python
"""
Script para importação de dados de absenteísmo através do Django.
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

print("Executando importação de absenteísmo...")

import requests
import json
from datetime import datetime, timedelta
from django.db import transaction

# Importar modelos - já estamos no ambiente Django
from dashboard.models import Empresa, Funcionario, Absenteismo

def processar_data(data_str):
    """Tenta converter uma string de data em um objeto date"""
    if not data_str:
        return None
        
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(data_str, fmt).date()
        except ValueError:
            continue
    return None

def format_date_for_api(date_obj):
    """Formata a data para o formato esperado pela API (DD/MM/YYYY)"""
    return date_obj.strftime('%d/%m/%Y')

def main():
    # Definir parâmetros fixos
    EMPRESA_PARAM = "423"
    CODIGO_PARAM = "183868"
    CHAVE_PARAM = "6dff7b9a8a635edaddf5"
    
    # Calcular datas (hoje e 30 dias atrás)
    hoje = datetime.now().date()
    data_inicio = hoje - timedelta(days=30)
    
    data_inicio_str = format_date_for_api(data_inicio)
    data_fim_str = format_date_for_api(hoje)
    
    # Contador para geração de matrículas genéricas
    contador_matricula = 1
    
    # Obter empresas ativas
    print("Buscando empresas ativas...")
    empresas_ativas = Empresa.objects.filter(ativo=True)

    if not empresas_ativas.exists():
        print("Não há empresas ativas no banco de dados.")
        return

    total_processados = 0
    print(f"Encontradas {empresas_ativas.count()} empresas ativas.")

    # Processar cada empresa
    for empresa in empresas_ativas:
        print(f"\nProcessando empresa: {empresa.codigo} - {empresa.nome_abreviado}")
        
        # Montar parâmetros da API
        url = 'https://ws1.soc.com.br/WebSoc/exportadados?parametro='
        parametros = {
            "empresa": EMPRESA_PARAM,
            "codigo": CODIGO_PARAM,
            "chave": CHAVE_PARAM,
            "tipoSaida": "json",
            "empresaTrabalho": str(empresa.codigo),
            "dataInicio": data_inicio_str,
            "dataFim": data_fim_str
        }
        
        # Converter o dicionário para string
        parametros_str = json.dumps(parametros)
        
        try:
            # Fazer a requisição
            print(f"Conectando à API para empresa {empresa.codigo}...")
            print(f"URL completa: {url + parametros_str}")
            response = requests.get(url=url + parametros_str, timeout=60)
            
            if response.status_code != 200:
                print(f"Erro ao conectar com a API. Status: {response.status_code}")
                continue
            
            # Decodificar resposta
            data = response.content.decode('latin-1')
            
            try:
                absenteismo_data = json.loads(data)
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON para empresa {empresa.codigo}. Resposta: {data[:200]}...")
                continue
            
            # Verificar formato dos dados
            registros = []
            if isinstance(absenteismo_data, dict):
                if 'registros' in absenteismo_data:
                    registros = absenteismo_data['registros']
                elif 'absenteismo' in absenteismo_data:
                    registros = absenteismo_data['absenteismo']
                elif len(absenteismo_data) > 0:
                    # Talvez os registros estejam diretamente no dicionário raiz
                    registros = [absenteismo_data]
            elif isinstance(absenteismo_data, list):
                registros = absenteismo_data
            
            if not registros:
                print(f"Nenhum registro de absenteísmo encontrado para a empresa {empresa.codigo}")
                continue
                
            print(f"Obtidos {len(registros)} registros de absenteísmo para a empresa {empresa.codigo}")
            
            # Usar transação para garantir consistência
            with transaction.atomic():
                for dados in registros:
                    try:
                        # Verificar se há matrícula, caso contrário, gerar uma genérica
                        matricula = dados.get('MATRICULA_FUNC', '')
                        if not matricula:
                            matricula = f"SEM_MATRICULA_{contador_matricula:04d}"
                            contador_matricula += 1
                            print(f"Matrícula gerada: {matricula}")
                        
                        # Processar datas
                        dt_inicio = processar_data(dados.get('DT_INICIO_ATESTADO'))
                        dt_fim = processar_data(dados.get('DT_FIM_ATESTADO'))
                        dt_nascimento = processar_data(dados.get('DT_NASCIMENTO'))
                        
                        # Se não tiver datas de início ou fim, criar com base nos parâmetros
                        if not dt_inicio:
                            dt_inicio = data_inicio
                            print(f"Data de início não encontrada para matrícula {matricula}. Usando {dt_inicio}.")
                            
                        if not dt_fim:
                            dt_fim = hoje
                            print(f"Data de fim não encontrada para matrícula {matricula}. Usando {dt_fim}.")
                            
                        # Converter dias afastados para inteiro
                        dias_afastados = dados.get('DIAS_AFASTADOS')
                        try:
                            dias_afastados = int(dias_afastados) if dias_afastados else None
                        except (ValueError, TypeError):
                            # Calcular dias se não informado
                            if dt_inicio and dt_fim:
                                dias_afastados = (dt_fim - dt_inicio).days + 1
                            else:
                                dias_afastados = 1  # Valor padrão
                            
                        # Processar tipo de atestado
                        tipo_atestado = dados.get('TIPO_ATESTADO')
                        try:
                            tipo_atestado = int(tipo_atestado) if tipo_atestado else 1
                            # Limitar aos valores possíveis
                            if tipo_atestado not in [1, 2, 3, 4]:
                                tipo_atestado = 4  # Outros afastamentos
                        except (ValueError, TypeError):
                            tipo_atestado = 1  # Padrão

                        # Processar sexo
                        sexo = dados.get('SEXO')
                        try:
                            sexo = int(sexo) if sexo else None
                            # Limitar aos valores possíveis
                            if sexo not in [1, 2]:
                                sexo = None
                        except (ValueError, TypeError):
                            sexo = None
                            
                        # Verificar se já existe este registro
                        registro_existente = Absenteismo.objects.filter(
                            empresa=empresa,
                            matricula_func=matricula,
                            dt_inicio_atestado=dt_inicio,
                            dt_fim_atestado=dt_fim
                        ).first()
                        
                        if registro_existente:
                            # Atualizar registro existente
                            for key, value in {
                                'unidade': dados.get('UNIDADE', ''),
                                'setor': dados.get('SETOR', ''),
                                'dt_nascimento': dt_nascimento,
                                'sexo': sexo,
                                'tipo_atestado': tipo_atestado,
                                'hora_inicio_atestado': dados.get('HORA_INICIO_ATESTADO', ''),
                                'hora_fim_atestado': dados.get('HORA_FIM_ATESTADO', ''),
                                'dias_afastados': dias_afastados,
                                'horas_afastado': dados.get('HORAS_AFASTADO', ''),
                                'cid_principal': dados.get('CID_PRINCIPAL', ''),
                                'descricao_cid': dados.get('DESCRICAO_CID', ''),
                                'grupo_patologico': dados.get('GRUPO_PATOLOGICO', ''),
                                'tipo_licenca': dados.get('TIPO_LICENCA', '')
                            }.items():
                                setattr(registro_existente, key, value)
                                
                            registro_existente.save()
                            print(f"Atualizado registro para matrícula {matricula} - {dt_inicio} a {dt_fim}")
                            
                        else:
                            # Criar novo registro
                            absenteismo = Absenteismo(
                                empresa=empresa,
                                matricula_func=matricula,
                                unidade=dados.get('UNIDADE', ''),
                                setor=dados.get('SETOR', ''),
                                dt_nascimento=dt_nascimento,
                                sexo=sexo,
                                tipo_atestado=tipo_atestado,
                                dt_inicio_atestado=dt_inicio,
                                dt_fim_atestado=dt_fim,
                                hora_inicio_atestado=dados.get('HORA_INICIO_ATESTADO', ''),
                                hora_fim_atestado=dados.get('HORA_FIM_ATESTADO', ''),
                                dias_afastados=dias_afastados,
                                horas_afastado=dados.get('HORAS_AFASTADO', ''),
                                cid_principal=dados.get('CID_PRINCIPAL', ''),
                                descricao_cid=dados.get('DESCRICAO_CID', ''),
                                grupo_patologico=dados.get('GRUPO_PATOLOGICO', ''),
                                tipo_licenca=dados.get('TIPO_LICENCA', '')
                            )
                            absenteismo.save()
                            print(f"Criado registro para matrícula {matricula} - {dt_inicio} a {dt_fim}")
                        
                        total_processados += 1
                        
                    except Exception as e:
                        print(f"Erro ao processar registro: {str(e)}")
                        # Imprimir o registro que causou o erro para debug
                        print(f"Dados do registro: {json.dumps(dados, indent=2)}")
            
        except Exception as e:
            print(f"Erro ao processar a empresa {empresa.codigo}: {str(e)}")

    print(f"\nImportação concluída. Total de registros de absenteísmo processados: {total_processados}")

# Executar a função principal
if __name__ == "__main__":
    main()