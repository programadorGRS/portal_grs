# importar_funcionarios.py - versão otimizada
import os
import django
import sys
import requests
import json
from datetime import datetime
from django.db import transaction

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_grs.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

# Importar modelos
from dashboard.models import Empresa, Funcionario

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

def main():
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
            "empresa": str(empresa.codigo),
            "codigo": "25722",
            "chave": "b4c740208036d64c467b",
            "tipoSaida": "json",
            "ativo": "Sim",
            "inativo": "",
            "afastado": "Sim",
            "pendente": "",
            "ferias": "Sim"
        }
        
        try:
            # Fazer a requisição
            print(f"Conectando à API para empresa {empresa.codigo}...")
            response = requests.get(url=url + str(parametros), timeout=60)
            
            if response.status_code != 200:
                print(f"Erro ao conectar com a API. Status: {response.status_code}")
                continue
            
            # Decodificar resposta
            data = response.content.decode('latin-1')
            funcionarios_data = json.loads(data)
            
            # Verificar formato dos dados
            if isinstance(funcionarios_data, dict) and 'registros' in funcionarios_data:
                funcionarios_data = funcionarios_data['registros']
            elif isinstance(funcionarios_data, dict) and 'funcionarios' in funcionarios_data:
                funcionarios_data = funcionarios_data['funcionarios']
            
            print(f"Obtidos {len(funcionarios_data)} funcionários para a empresa {empresa.codigo}")
            
            # Preparar objetos para inserção em massa
            funcionarios_para_criar = []
            codigos_para_atualizar = []
            
            # Preparar dados para atualização/criação
            for func_data in funcionarios_data:
                try:
                    codigo = int(func_data.get('CODIGO', 0))
                    if codigo <= 0:
                        continue
                        
                    # Verificar se o funcionário já existe
                    codigos_para_atualizar.append(codigo)
                    
                    # Mapear dados
                    funcionario_dict = {
                        'empresa_id': empresa.id,
                        'codigo': codigo,
                        'codigo_empresa': empresa.codigo,
                        'nome_empresa': empresa.nome_abreviado,
                        'nome': func_data.get('NOME', '')[:120],
                        'codigo_unidade': func_data.get('CODIGOUNIDADE', '')[:20],
                        'nome_unidade': func_data.get('NOMEUNIDADE', '')[:130],
                        'codigo_setor': func_data.get('CODIGOSETOR', '')[:12],
                        'nome_setor': func_data.get('NOMESETOR', '')[:130],
                        'codigo_cargo': func_data.get('CODIGOCARGO', '')[:10],
                        'nome_cargo': func_data.get('NOMECARGO', '')[:130],
                        'cbo_cargo': func_data.get('CBOCARGO', '')[:10],
                        'ccusto': func_data.get('CCUSTO', '')[:50],
                        'nome_centro_custo': func_data.get('NOMECENTROCUSTO', '')[:130],
                        'matricula_funcionario': func_data.get('MATRICULAFUNCIONARIO', '')[:30],
                        'cpf': func_data.get('CPF', '')[:19],
                        'rg': func_data.get('RG', '')[:19],
                        'uf_rg': func_data.get('UFRG', '')[:10],
                        'orgao_emissor_rg': func_data.get('ORGAOEMISSORRG', '')[:20],
                        'situacao': func_data.get('SITUACAO', '')[:12],
                        'sexo': int(func_data.get('SEXO', 0) or 0) or None,
                        'pis': func_data.get('PIS', '')[:20],
                        'ctps': func_data.get('CTPS', '')[:30],
                        'serie_ctps': func_data.get('SERIECTPS', '')[:25],
                        'estado_civil': int(func_data.get('ESTADOCIVIL', 0) or 0) or None,
                        'tipo_contratacao': int(func_data.get('TIPOCONTATACAO', 0) or 0) or None,
                        'data_nascimento': processar_data(func_data.get('DATA_NASCIMENTO')),
                        'data_admissao': processar_data(func_data.get('DATA_ADMISSAO')),
                        'data_demissao': processar_data(func_data.get('DATA_DEMISSAO')),
                        'endereco': func_data.get('ENDERECO', '')[:110],
                        'numero_endereco': func_data.get('NUMERO_ENDERECO', '')[:20],
                        'bairro': func_data.get('BAIRRO', '')[:80],
                        'cidade': func_data.get('CIDADE', '')[:50],
                        'uf': func_data.get('UF', '')[:20],
                        'cep': func_data.get('CEP', '')[:10],
                        'telefone_residencial': func_data.get('TELEFONERESIDENCIAL', '')[:20],
                        'telefone_celular': func_data.get('TELEFONECELULAR', '')[:20],
                        'email': func_data.get('EMAIL', '')[:400],
                        'deficiente': bool(int(func_data.get('DEFICIENTE', 0) or 0)),
                        'deficiencia': func_data.get('DEFICIENCIA', '')[:861],
                        'nm_mae_funcionario': func_data.get('NM_MAE_FUNCIONARIO', '')[:120],
                        'data_ultima_alteracao': processar_data(func_data.get('DATAULTALTERACAO')),
                        'matricula_rh': func_data.get('MATRICULARH', '')[:30],
                        'cor': int(func_data.get('COR', 0) or 0) or None,
                        'escolaridade': int(func_data.get('ESCOLARIDADE', 0) or 0) or None,
                        'naturalidade': func_data.get('NATURALIDADE', '')[:50],
                        'ramal': func_data.get('RAMAL', '')[:10],
                        'regime_revezamento': int(func_data.get('REGIMEREVEZAMENTO', 0) or 0) or None,
                        'regime_trabalho': func_data.get('REGIMETRABALHO', '')[:500],
                        'tel_comercial': func_data.get('TELCOMERCIAL', '')[:20],
                        'turno_trabalho': int(func_data.get('TURNOTRABALHO', 0) or 0) or None,
                        'rh_unidade': func_data.get('RHUNIDADE', '')[:80],
                        'rh_setor': func_data.get('RHSETOR', '')[:80],
                        'rh_cargo': func_data.get('RHCARGO', '')[:80],
                        'rh_centro_custo_unidade': func_data.get('RHCENTROCUSTOUNIDADE', '')[:80],
                    }
                    
                    funcionarios_para_criar.append(funcionario_dict)
                    
                except Exception as e:
                    print(f"Erro ao processar funcionário {func_data.get('CODIGO', 'N/A')}: {str(e)}")
            
            # Usar transação para garantir consistência
            with transaction.atomic():
                # 1. Buscar funcionários existentes para atualizar
                funcionarios_existentes = {
                    f.codigo: f for f in Funcionario.objects.filter(codigo__in=codigos_para_atualizar)
                }
                
                # 2. Separar em listas para criar e atualizar
                para_criar = []
                para_atualizar = []
                
                for func_dict in funcionarios_para_criar:
                    codigo = func_dict['codigo']
                    if codigo in funcionarios_existentes:
                        # Atualizar existente
                        funcionario = funcionarios_existentes[codigo]
                        for key, value in func_dict.items():
                            setattr(funcionario, key, value)
                        para_atualizar.append(funcionario)
                    else:
                        # Criar novo
                        para_criar.append(Funcionario(**func_dict))
                
                # 3. Salvar em lote (bulk operations)
                if para_criar:
                    print(f"Inserindo {len(para_criar)} novos funcionários em lote...")
                    Funcionario.objects.bulk_create(para_criar, batch_size=100)
                
                if para_atualizar:
                    print(f"Atualizando {len(para_atualizar)} funcionários existentes em lote...")
                    Funcionario.objects.bulk_update(
                        para_atualizar, 
                        fields=[f.name for f in Funcionario._meta.fields if f.name != 'codigo'],
                        batch_size=100
                    )
                
                total_processados += len(para_criar) + len(para_atualizar)
                print(f"Processados {len(para_criar) + len(para_atualizar)} funcionários para a empresa {empresa.codigo}")
            
        except Exception as e:
            print(f"Erro ao processar a empresa {empresa.codigo}: {str(e)}")

    print(f"\nImportação concluída. Total de funcionários processados: {total_processados}")

if __name__ == "__main__":
    main()