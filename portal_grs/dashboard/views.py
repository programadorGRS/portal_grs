# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import *
import json
from django.db.models import Count, Sum, Avg, Max, F, Q, Case, When, Value, IntegerField, CharField
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

@login_required
def convocacao_view(request):
    """View para a página de convocação de exames"""
    # Obter a empresa atual
    empresa_atual = get_current_empresa(request)
    
    # Obter empresas acessíveis para o usuário
    empresas_acessiveis = get_user_empresas(request.user)
    
    # Obter filtros da requisição
    status_filtro = request.GET.get('status', '')
    vencimento = request.GET.get('vencimento', '')  # Alterado de setor
    unidade = request.GET.get('unidade', '')
    busca = request.GET.get('busca', '')
    
    # Base query para convocações da empresa atual
    base_query = Convocacao.objects.filter(empresa=empresa_atual)
    
    # Aplicar outros filtros
    if unidade:
        base_query = base_query.filter(unidade__icontains=unidade)
    if busca:
        base_query = base_query.filter(
            Q(nome__icontains=busca) | 
            Q(cpf_funcionario__icontains=busca) | 
            Q(matricula__icontains=busca)
        )
    
    # Data atual para comparações
    hoje = timezone.now().date()
    fim_do_ano = datetime(hoje.year, 12, 31).date()
    
    # Criar campos calculados com Case/When para status
    convocacoes_com_status = base_query.annotate(
        status_calc=Case(
            When(Q(ultimo_pedido__isnull=True) & Q(data_resultado__isnull=True) & Q(refazer__isnull=True), 
                 then=Value('Sem histórico')),
            When(Q(ultimo_pedido__isnull=False) & Q(data_resultado__isnull=True) & Q(refazer__isnull=True), 
                 then=Value('Pendente')),
            When(Q(refazer__isnull=False) & Q(refazer__lte=hoje) & Q(ultimo_pedido__isnull=False) & Q(data_resultado__isnull=False), 
                 then=Value('Vencido')),
            When(Q(refazer__isnull=False) & Q(refazer__lte=fim_do_ano), 
                 then=Value('A Vencer')),
            When(Q(refazer__isnull=False) & Q(refazer__year__gt=hoje.year), 
                 then=Value('Em dia')),
            default=Value('Desconhecido'),
            output_field=models.CharField(),
        )
    )
    
    # Filtro de vencimento (novo)
    if vencimento:
        # Calcular a data limite com base nos dias especificados
        data_limite = hoje + timedelta(days=int(vencimento))
        
        # Filtrar por datas de refazer entre hoje e a data limite
        convocacoes_com_status = convocacoes_com_status.filter(
            Q(refazer__isnull=False) & 
            Q(refazer__gte=hoje) & 
            Q(refazer__lte=data_limite)
        )
    
    # Contagem de totais por status para KPIs (uma única consulta)
    status_counts = convocacoes_com_status.values('status_calc').annotate(
        count=Count('id')
    ).order_by('status_calc')
    
    # Transformar em dicionário para facilitar acesso
    status_counts_dict = {item['status_calc']: item['count'] for item in status_counts}
    
    # Definir totais
    total_exames = sum(status_counts_dict.values())
    total_vencidos = status_counts_dict.get('Vencido', 0)
    total_pendentes = status_counts_dict.get('Pendente', 0)
    total_a_vencer = status_counts_dict.get('A Vencer', 0)
    total_em_dia = status_counts_dict.get('Em dia', 0)
    total_sem_historico = status_counts_dict.get('Sem histórico', 0)
    
    # Filtrar por status se solicitado
    if status_filtro:
        convocacoes_com_status = convocacoes_com_status.filter(status_calc=status_filtro)
    
    # Agregação por funcionário (uma única consulta SQL)
    funcionarios = convocacoes_com_status.values(
        'codigo_funcionario', 'nome', 'cpf_funcionario', 'matricula', 'cargo', 'setor', 'unidade'
    ).annotate(
        total_exames=Count('codigo_funcionario'),
        exames_vencidos=Count(Case(
            When(status_calc='Vencido', then=1),
            output_field=models.IntegerField()
        )),
        exames_pendentes=Count(Case(
            When(status_calc='Pendente', then=1),
            output_field=models.IntegerField()
        ))
    ).order_by('nome')
    
    # Paginação
    paginator = Paginator(list(funcionarios), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcular percentuais
    percentual_vencidos = round((total_vencidos / total_exames) * 100) if total_exames else 0
    percentual_pendentes = round((total_pendentes / total_exames) * 100) if total_exames else 0
    percentual_a_vencer = round((total_a_vencer / total_exames) * 100) if total_exames else 0
    percentual_em_dia = round((total_em_dia / total_exames) * 100) if total_exames else 0
    
    # Dados para o gráfico de status
    status_data = [
        {'label': 'Vencidos', 'count': total_vencidos, 'status': 'Vencido'},
        {'label': 'Pendentes', 'count': total_pendentes, 'status': 'Pendente'},
        {'label': 'A Vencer', 'count': total_a_vencer, 'status': 'A Vencer'},
        {'label': 'Em Dia', 'count': total_em_dia, 'status': 'Em dia'},
        {'label': 'Sem Histórico', 'count': total_sem_historico, 'status': 'Sem histórico'}
    ]
    
    # Obter os últimos 6 meses
    meses = []
    datas_meses = []
    for i in range(5, -1, -1):
        data = hoje - timedelta(days=i*30)
        meses.append(data.strftime('%m/%Y'))
        # Primeiro dia do mês para filtro
        primeiro_dia = data.replace(day=1)
        datas_meses.append(primeiro_dia)
    
    # Consulta para dados de evolução agrupados por mês e status
    from django.db.models.functions import TruncMonth
    
    evolucao_data_query = (
        base_query
        .filter(data_convocacao__gte=datas_meses[0])  # Filtrar pelos últimos 6 meses
        .annotate(
            mes=TruncMonth('data_convocacao'),
            status_calc=Case(
                When(Q(ultimo_pedido__isnull=True) & Q(data_resultado__isnull=True) & Q(refazer__isnull=True), 
                     then=Value('Sem histórico')),
                When(Q(ultimo_pedido__isnull=False) & Q(data_resultado__isnull=True) & Q(refazer__isnull=True), 
                     then=Value('Pendente')),
                When(Q(refazer__isnull=False) & Q(refazer__lte=hoje) & Q(ultimo_pedido__isnull=False) & Q(data_resultado__isnull=False), 
                     then=Value('Vencido')),
                When(Q(refazer__isnull=False) & Q(refazer__lte=fim_do_ano), 
                     then=Value('A Vencer')),
                When(Q(refazer__isnull=False) & Q(refazer__year__gt=hoje.year), 
                     then=Value('Em dia')),
                default=Value('Desconhecido'),
                output_field=models.CharField(),
            )
        )
        .values('mes', 'status_calc')
        .annotate(total=Count('id'))
        .order_by('mes', 'status_calc')
    )
    
    # Inicializar séries com zeros
    evolucao_vencidos = [0] * 6
    evolucao_pendentes = [0] * 6
    evolucao_a_vencer = [0] * 6
    evolucao_em_dia = [0] * 6
    
    # Criar mapeamento de meses para índices
    mes_para_indice = {mes.replace(day=1): i for i, mes in enumerate(datas_meses)}
    
    # Preenchimento otimizado dos dados de evolução
    for item in evolucao_data_query:
        mes = item['mes']
        status = item['status_calc']
        total = item['total']
        
        if mes in mes_para_indice:
            idx = mes_para_indice[mes]
            if status == 'Vencido':
                evolucao_vencidos[idx] = total
            elif status == 'Pendente':
                evolucao_pendentes[idx] = total
            elif status == 'A Vencer':
                evolucao_a_vencer[idx] = total
            elif status == 'Em dia':
                evolucao_em_dia[idx] = total
    
    # Dados para o gráfico de evolução temporal
    evolucao_data = {
        'labels': meses,
        'series': [
            {'name': 'Vencidos', 'data': evolucao_vencidos},
            {'name': 'Pendentes', 'data': evolucao_pendentes},
            {'name': 'A Vencer', 'data': evolucao_a_vencer},
            {'name': 'Em Dia', 'data': evolucao_em_dia}
        ]
    }
    
    # Opções para filtros (consultas otimizadas)
    setores = base_query.values_list('setor', flat=True).distinct()
    unidades = base_query.values_list('unidade', flat=True).distinct()
    
    return render(request, 'dashboard/convocacao.html', {
        'user': request.user,
        'empresa_atual': empresa_atual,
        'empresas_acessiveis': empresas_acessiveis,
        'page_obj': page_obj,
        'total_vencidos': total_vencidos,
        'total_pendentes': total_pendentes,
        'total_a_vencer': total_a_vencer,
        'total_em_dia': total_em_dia,
        'percentual_vencidos': percentual_vencidos,
        'percentual_pendentes': percentual_pendentes,
        'percentual_a_vencer': percentual_a_vencer,
        'percentual_em_dia': percentual_em_dia,
        'status_data': json.dumps(status_data),
        'evolucao_data': json.dumps(evolucao_data),
        'setores': setores,
        'unidades': unidades,
        'filtros': {
            'status': status_filtro,
            'vencimento': vencimento,  
            'unidade': unidade,
            'busca': busca
        }
    })

@login_required
def get_funcionario_convocacoes_api(request, funcionario_id):
    """API para obter convocações de um funcionário específico"""
    try:
        # Obter a empresa atual
        empresa_atual = get_current_empresa(request)
        
        # Obter dados do funcionário
        funcionario = Funcionario.objects.filter(
            codigo=funcionario_id, 
            empresa=empresa_atual
        ).values('codigo', 'nome', 'cpf', 'matricula_funcionario', 'nome_cargo', 'nome_setor', 'nome_unidade', 'data_admissao').first()
        
        if not funcionario:
            return JsonResponse({'error': 'Funcionário não encontrado'}, status=404)
        
        # Obter exames do funcionário
        convocacoes = Convocacao.objects.filter(
            empresa=empresa_atual,
            codigo_funcionario=funcionario_id
        ).values(
            'exame', 'ultimo_pedido', 'data_resultado', 'periodicidade', 'refazer'
        )
        
        # Data atual para comparações
        hoje = timezone.now().date()
        fim_do_ano = datetime(hoje.year, 12, 31).date()
        
        # Adicionar status a cada convocação
        exames_list = []
        for convocacao in convocacoes:
            # Calcular status baseado na mesma lógica do PowerQuery
            if (not convocacao['ultimo_pedido']) and (not convocacao['data_resultado']) and (not convocacao['refazer']):
                status = "Sem histórico"
            elif convocacao['ultimo_pedido'] and (not convocacao['data_resultado']) and (not convocacao['refazer']):
                status = "Pendente"
            elif convocacao['refazer'] and convocacao['refazer'] <= hoje and convocacao['ultimo_pedido'] and convocacao['data_resultado']:
                status = "Vencido"
            elif convocacao['refazer'] and convocacao['refazer'] <= fim_do_ano:
                status = "A Vencer"
            elif convocacao['refazer'] and convocacao['refazer'].year > hoje.year:
                status = "Em dia"
            else:
                status = "Desconhecido"
            
            # Adicionar status ao dicionário de convocação
            convocacao_dict = dict(convocacao)
            convocacao_dict['status'] = status
            exames_list.append(convocacao_dict)
        
        # Formatar dados para o response
        response_data = {
            'funcionario': {
                'id': funcionario['codigo'],
                'nome': funcionario['nome'],
                'cpf': funcionario['cpf'],
                'matricula': funcionario['matricula_funcionario'],
                'cargo': funcionario['nome_cargo'],
                'setor': funcionario['nome_setor'],
                'unidade': funcionario['nome_unidade'],
                'data_admissao': funcionario['data_admissao'].isoformat() if funcionario['data_admissao'] else None
            },
            'exames': exames_list
        }
        
        # Converter datas para ISO format para serialização JSON
        for exame in response_data['exames']:
            if exame['ultimo_pedido']:
                exame['ultimo_pedido'] = exame['ultimo_pedido'].isoformat()
            if exame['data_resultado']:
                exame['data_resultado'] = exame['data_resultado'].isoformat()
            if exame['refazer']:
                exame['refazer'] = exame['refazer'].isoformat()
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def export_convocacoes_all_api(request):
    """API para exportar todas as convocações"""
    try:
        # Obter a empresa atual
        empresa_atual = get_current_empresa(request)
        
        # Obter todas as convocações
        convocacoes = Convocacao.objects.filter(empresa=empresa_atual).values(
            'nome', 'cpf_funcionario', 'matricula', 'cargo', 'setor', 'unidade',
            'exame', 'ultimo_pedido', 'data_resultado', 'periodicidade', 'refazer'
        )
        
        # Data atual para comparações
        hoje = timezone.now().date()
        fim_do_ano = datetime(hoje.year, 12, 31).date()
        
        # Adicionar status a cada convocação
        convocacoes_list = []
        for convocacao in convocacoes:
            # Calcular status baseado na mesma lógica do PowerQuery
            if (not convocacao['ultimo_pedido']) and (not convocacao['data_resultado']) and (not convocacao['refazer']):
                status = "Sem histórico"
            elif convocacao['ultimo_pedido'] and (not convocacao['data_resultado']) and (not convocacao['refazer']):
                status = "Pendente"
            elif convocacao['refazer'] and convocacao['refazer'] <= hoje and convocacao['ultimo_pedido'] and convocacao['data_resultado']:
                status = "Vencido"
            elif convocacao['refazer'] and convocacao['refazer'] <= fim_do_ano:
                status = "A Vencer"
            elif convocacao['refazer'] and convocacao['refazer'].year > hoje.year:
                status = "Em dia"
            else:
                status = "Desconhecido"
            
            # Adicionar status ao dicionário de convocação
            convocacao_dict = dict(convocacao)
            convocacao_dict['status'] = status
            convocacoes_list.append(convocacao_dict)
        
        # Converter datas para ISO format para serialização JSON
        for conv in convocacoes_list:
            if conv['ultimo_pedido']:
                conv['ultimo_pedido'] = conv['ultimo_pedido'].isoformat()
            if conv['data_resultado']:
                conv['data_resultado'] = conv['data_resultado'].isoformat()
            if conv['refazer']:
                conv['refazer'] = conv['refazer'].isoformat()
        
        return JsonResponse(convocacoes_list, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def absenteismo_view(request):
    """View da página de absenteísmo"""
    # Obter a empresa atual
    empresa_atual = get_current_empresa(request)
    
    # Obter todas as empresas acessíveis ao usuário
    empresas_acessiveis = get_user_empresas(request.user)
    
    # Parâmetros de filtro
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    tipo_atestado = request.GET.get('tipo_atestado', '')
    setor = request.GET.get('setor', '')
    unidade = request.GET.get('unidade', '')
    busca = request.GET.get('busca', '')
    periodo = request.GET.get('periodo', '30')  # padrão: últimos 30 dias
    
    # Período de análise
    hoje = timezone.now().date()
    
    if data_inicio and data_fim:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except ValueError:
            # Em caso de erro, usar período padrão
            data_inicio_obj = hoje - timedelta(days=int(periodo))
            data_fim_obj = hoje
    else:
        # Definir período baseado no parâmetro 'periodo'
        data_inicio_obj = hoje - timedelta(days=int(periodo))
        data_fim_obj = hoje
    
    # Consulta base de absenteísmo
    queryset = Absenteismo.objects.filter(
        empresa=empresa_atual,
        dt_inicio_atestado__gte=data_inicio_obj,
        dt_inicio_atestado__lte=data_fim_obj
    )
    
    # Aplicar filtros adicionais
    if tipo_atestado:
        queryset = queryset.filter(tipo_atestado=tipo_atestado)
    if setor:
        queryset = queryset.filter(setor__icontains=setor)
    if unidade:
        queryset = queryset.filter(unidade__icontains=unidade)
    if busca:
        queryset = queryset.filter(
            Q(funcionario__nome__icontains=busca) | 
            Q(matricula_func__icontains=busca) |
            Q(cid_principal__icontains=busca)
        )
    
    # KPIs
    total_registros = queryset.count()
    total_dias_afastamento = queryset.aggregate(Sum('dias_afastados'))['dias_afastados__sum'] or 0
    media_dias = queryset.aggregate(Avg('dias_afastados'))['dias_afastados__avg'] or 0
    funcionarios_afastados = queryset.values('matricula_func').distinct().count()
    
    # Calcular índice de absenteísmo (% dias perdidos)
    total_funcionarios = Funcionario.objects.filter(empresa=empresa_atual).count()
    dias_periodo = (data_fim_obj - data_inicio_obj).days + 1
    dias_trabalho_potencial = total_funcionarios * dias_periodo
    indice_absenteismo = (total_dias_afastamento / dias_trabalho_potencial * 100) if dias_trabalho_potencial > 0 else 0
    
    # Dados para gráficos
    # 1. Tendência mensal de absenteísmo
    tendencia_mensal = queryset.annotate(
        mes=TruncMonth('dt_inicio_atestado')
    ).values('mes').annotate(
        total=Count('id'),
        dias=Sum('dias_afastados')
    ).order_by('mes')
    
    # 2. Distribuição por tipo de atestado - CORRIGIDO
    distribuicao_tipo = queryset.values('tipo_atestado').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Criar um dicionário para mapear tipo_atestado para o label correspondente
    tipo_atestado_map = dict(Absenteismo.TIPO_ATESTADO_CHOICES)
    
    # 3. Top 5 CIDs (causas de afastamento)
    top_cids = queryset.exclude(cid_principal__isnull=True).exclude(cid_principal='').values(
        'cid_principal', 'descricao_cid'
    ).annotate(
        total=Count('id'),
        dias=Sum('dias_afastados')
    ).order_by('-total')[:5]
    
    # 4. Absenteísmo por setor
    por_setor = queryset.values('setor').annotate(
        total=Count('id'),
        dias=Sum('dias_afastados')
    ).order_by('-dias')[:10]
    
    # 5. Funcionários com mais atestados
    funcionarios_ranking = queryset.values(
        'matricula_func', 'funcionario__nome', 'funcionario__nome_cargo', 
        'funcionario__nome_setor', 'funcionario__nome_unidade'
    ).annotate(
        total_atestados=Count('id'),
        total_dias=Sum('dias_afastados'),
        ultimo_atestado=Max('dt_inicio_atestado')
    ).order_by('-total_atestados')[:15]
    
    # Opções para filtros
    setores = Absenteismo.objects.filter(empresa=empresa_atual).values_list('setor', flat=True).distinct()
    unidades = Absenteismo.objects.filter(empresa=empresa_atual).values_list('unidade', flat=True).distinct()
    
    # Conversão para JSON para uso no JavaScript
    tendencia_data = json.dumps([{
        'mes': item['mes'].strftime('%Y-%m') if item['mes'] else '',
        'total': item['total'],
        'dias': item['dias']
    } for item in tendencia_mensal])
    
    # Usando o mapeamento para obter os labels corretos - CORRIGIDO
    tipos_data = json.dumps([{
        'tipo': item['tipo_atestado'],
        'label': tipo_atestado_map.get(item['tipo_atestado'], 'Não categorizado'),
        'total': item['total']
    } for item in distribuicao_tipo])
    
    cids_data = json.dumps([{
        'cid': item['cid_principal'],
        'descricao': item['descricao_cid'] or f"CID {item['cid_principal']}",
        'total': item['total'],
        'dias': item['dias']
    } for item in top_cids])
    
    setores_data = json.dumps([{
        'setor': item['setor'] or 'Não especificado',
        'total': item['total'],
        'dias': item['dias']
    } for item in por_setor])
    
    return render(request, 'dashboard/absenteismo.html', {
        'user': request.user,
        'empresa_atual': empresa_atual,
        'empresas_acessiveis': empresas_acessiveis,
        
        # Parâmetros de filtro
        'filtros': {
            'data_inicio': data_inicio or data_inicio_obj.strftime('%Y-%m-%d'),
            'data_fim': data_fim or data_fim_obj.strftime('%Y-%m-%d'),
            'tipo_atestado': tipo_atestado,
            'setor': setor,
            'unidade': unidade,
            'busca': busca,
            'periodo': periodo
        },
        
        # KPIs
        'total_registros': total_registros,
        'total_dias_afastamento': total_dias_afastamento,
        'media_dias': round(media_dias, 2),
        'funcionarios_afastados': funcionarios_afastados,
        'indice_absenteismo': round(indice_absenteismo, 2),
        
        # Dados para gráficos
        'tendencia_data': tendencia_data,
        'tipos_data': tipos_data,
        'cids_data': cids_data,
        'setores_data': setores_data,
        
        # Ranking de funcionários
        'funcionarios_ranking': funcionarios_ranking,
        
        # Opções para filtros
        'setores': setores,
        'unidades': unidades,
        'tipos_atestado': Absenteismo.TIPO_ATESTADO_CHOICES,
    })

# Função para obter a empresa atual do usuário
def get_current_empresa(request):
    """Obtém a empresa atual do usuário baseada na sessão ou na empresa principal"""
    cache_key = f"empresa_atual_{request.user.id}"
    cached_empresa = cache.get(cache_key)
    
    if cached_empresa:
        return cached_empresa
        
    if 'empresa_atual' in request.session:
        empresa_codigo = request.session['empresa_atual']
        # Verificar se o usuário tem acesso a esta empresa
        if request.user.tipo_usuario == 'admin' or AcessoEmpresa.objects.filter(usuario=request.user, empresa__codigo=empresa_codigo).exists():
            try:
                empresa = Empresa.objects.get(codigo=empresa_codigo)
                cache.set(cache_key, empresa, 60*30)  # Cache por 30 minutos
                return empresa
            except Empresa.DoesNotExist:
                pass
    
    # Se não houver empresa na sessão ou o usuário não tiver acesso, usar a principal
    empresa_atual = request.user.empresa_principal
    if not empresa_atual:
        # Se não tiver empresa principal, usar a primeira disponível
        empresas = get_user_empresas(request.user)
        if empresas.exists():
            empresa_atual = empresas.first()
    
    # Atualizar a sessão
    if empresa_atual:
        request.session['empresa_atual'] = empresa_atual.codigo
        cache.set(cache_key, empresa_atual, 60*30)  # Cache por 30 minutos
    
    return empresa_atual

# Função para obter empresas do usuário
def get_user_empresas(user):
    """Retorna as empresas que o usuário tem acesso"""
    cache_key = f"empresas_usuario_{user.id}"
    cached_empresas = cache.get(cache_key)
    
    if cached_empresas:
        return cached_empresas
        
    if user.tipo_usuario == 'admin':
        # Admin pode ver todas as empresas
        empresas = Empresa.objects.filter(ativo=True).order_by('nome_abreviado')
    else:
        # Usuário normal só vê empresas que tem acesso
        empresas = Empresa.objects.filter(
            acessoempresa__usuario=user,
            ativo=True
        ).distinct().order_by('nome_abreviado')
    
    cache.set(cache_key, empresas, 60*30)  # Cache por 30 minutos
    return empresas

# Otimizei esta função para buscar estatísticas do dashboard
def get_dashboard_stats(empresa_atual):
    """Obtém estatísticas para o dashboard"""
    cache_key = f"dashboard_stats_{empresa_atual.codigo}"
    cached_stats = cache.get(cache_key)
    
    if cached_stats:
        return cached_stats
        
    # Obter estatísticas reais do banco de dados
    stats = {
        'total_funcionarios': Funcionario.objects.filter(empresa=empresa_atual).count(),
        'funcionarios_ativos': Funcionario.objects.filter(empresa=empresa_atual, situacao='ATIVO').count(),
        'funcionarios_ferias': Funcionario.objects.filter(empresa=empresa_atual, situacao='FÉRIAS').count(),
        'funcionarios_afastados': Funcionario.objects.filter(empresa=empresa_atual, situacao='AFASTADO').count()
    }
    
    # Adicionar outras estatísticas conforme necessário
    
    # Cachear por 15 minutos - ajuste conforme necessidade de atualização
    cache.set(cache_key, stats, 60*15)
    
    return stats

# View do dashboard com dados reais
@login_required
def dashboard_view(request):
    """View do dashboard que requer autenticação"""
    # Obter a empresa atual do usuário
    empresa_atual = get_current_empresa(request)
    
    # Obter empresas acessíveis para o usuário
    empresas_acessiveis = get_user_empresas(request.user)
    
    # Obter dados estatísticos para o dashboard
    stats = get_dashboard_stats(empresa_atual)
    
    return render(request, 'dashboard/dashboard.html', {
        'user': request.user,
        'empresa_atual': empresa_atual,
        'empresas_acessiveis': empresas_acessiveis,
        'stats': stats
    })

# API para obter dados do dashboard via AJAX
@login_required
def dashboard_api(request):
    """API para obter dados do dashboard para carregamento AJAX"""
    empresa_atual = get_current_empresa(request)
    stats = get_dashboard_stats(empresa_atual)
    
    return JsonResponse({
        'success': True,
        'data': stats
    })

# View otimizada de funcionários
@login_required
def funcionarios_view(request):
    """View da página de funcionários otimizada"""
    # Obter a empresa atual
    empresa_atual = get_current_empresa(request)
    
    # Obter todas as empresas acessíveis ao usuário
    empresas_acessiveis = get_user_empresas(request.user)
    
    # Filtros
    cargo = request.GET.get('cargo', '')
    setor = request.GET.get('setor', '')
    unidade = request.GET.get('unidade', '')
    busca = request.GET.get('busca', '')
    
    # Cache de opções para filtros (por empresa)
    cache_key = f"filtros_funcionarios_{empresa_atual.codigo}"
    filtros_cache = cache.get(cache_key)
    
    if not filtros_cache:
        # Query otimizada para obter opções de filtros
        cargos = Funcionario.objects.filter(empresa=empresa_atual).values_list('nome_cargo', flat=True).distinct()
        setores = Funcionario.objects.filter(empresa=empresa_atual).values_list('nome_setor', flat=True).distinct()
        unidades = Funcionario.objects.filter(empresa=empresa_atual).values_list('nome_unidade', flat=True).distinct()
        
        filtros_cache = {
            'cargos': list(cargos),
            'setores': list(setores),
            'unidades': list(unidades)
        }
        
        # Cache por 1 hora, pois essas opções raramente mudam
        cache.set(cache_key, filtros_cache, 60*60)
    
    # Consulta base otimizada com select_related para evitar N+1 queries
    # Funcionarios não tem related objects, então não precisa de select_related aqui
    funcionarios = Funcionario.objects.filter(empresa=empresa_atual)
    
    # Aplicar filtros
    if cargo:
        funcionarios = funcionarios.filter(nome_cargo__icontains=cargo)
    if setor:
        funcionarios = funcionarios.filter(nome_setor__icontains=setor)
    if unidade:
        funcionarios = funcionarios.filter(nome_unidade__icontains=unidade)
    if busca:
        funcionarios = funcionarios.filter(
            Q(nome__icontains=busca) | 
            Q(cpf__icontains=busca) | 
            Q(matricula_funcionario__icontains=busca)
        )
    
    # Otimizar: Selecionar apenas os campos necessários para a listagem
    funcionarios = funcionarios.only(
        'codigo', 'nome', 'cpf', 'nome_cargo', 'nome_setor', 
        'nome_unidade', 'data_admissao', 'situacao'
    )
    
    # Paginação - 15 funcionários por página (aumentei de 10 para 15)
    paginator = Paginator(funcionarios, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/funcionarios.html', {
        'user': request.user,
        'empresa_atual': empresa_atual,
        'empresas_acessiveis': empresas_acessiveis,
        'page_obj': page_obj,  # Objeto da página atual
        'cargos': filtros_cache['cargos'],
        'setores': filtros_cache['setores'],
        'unidades': filtros_cache['unidades'],
        'filtros': {
            'cargo': cargo,
            'setor': setor,
            'unidade': unidade,
            'busca': busca
        }
    })

# Reescrita da função get_funcionario_api para resolver o erro de sintaxe
@login_required
def get_funcionario_api(request, id):
    """API para obter dados de um funcionário específico por código"""
    try:
        # Obter a empresa atual
        empresa_atual = get_current_empresa(request)
        
        # Consulta reescrita usando argumentos nomeados via dicionário
        # para evitar completamente problemas de ordem de argumentos
        query_params = {
            'codigo': id,
            'empresa': empresa_atual
        }
        
        funcionario = Funcionario.objects.get(**query_params)
        
        # Retornar os dados do funcionário em formato JSON
        return JsonResponse({
            'codigo': funcionario.codigo,
            'nome': funcionario.nome,
            'cpf': funcionario.cpf,
            'rg': funcionario.rg,
            'orgao_emissor_rg': funcionario.orgao_emissor_rg,
            'uf_rg': funcionario.uf_rg,
            'matricula_funcionario': funcionario.matricula_funcionario,
            'nome_cargo': funcionario.nome_cargo,
            'nome_setor': funcionario.nome_setor,
            'nome_unidade': funcionario.nome_unidade,
            'nome_empresa': funcionario.nome_empresa,
            'nome_centro_custo': funcionario.nome_centro_custo,
            'data_admissao': funcionario.data_admissao.strftime('%d/%m/%Y') if funcionario.data_admissao else None,
            'data_demissao': funcionario.data_demissao.strftime('%d/%m/%Y') if funcionario.data_demissao else None,
            'data_nascimento': funcionario.data_nascimento.strftime('%d/%m/%Y') if funcionario.data_nascimento else None,
            'sexo': funcionario.sexo,
            'estado_civil': funcionario.estado_civil,
            'pis': funcionario.pis,
            'ctps': funcionario.ctps,
            'serie_ctps': funcionario.serie_ctps,
            'situacao': funcionario.situacao,
            'endereco': funcionario.endereco,
            'numero_endereco': funcionario.numero_endereco,
            'bairro': funcionario.bairro,
            'cidade': funcionario.cidade,
            'uf': funcionario.uf,
            'cep': funcionario.cep,
            'telefone_residencial': funcionario.telefone_residencial,
            'telefone_celular': funcionario.telefone_celular,
            'tel_comercial': funcionario.tel_comercial,
            'email': funcionario.email,
            'nm_mae_funcionario': funcionario.nm_mae_funcionario,
            'naturalidade': funcionario.naturalidade,
        })
    except Funcionario.DoesNotExist:
        return JsonResponse({'error': 'Funcionário não encontrado'}, status=404)

# Reescrita da função search_funcionarios_api para resolver o erro de sintaxe
@login_required
def search_funcionarios_api(request):
    """API para busca dinâmica de funcionários"""
    empresa_atual = get_current_empresa(request)
    query = request.GET.get('query', '')
    
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    # Construir condições de consulta usando objeto Q
    search_conditions = Q()
    # Adicionar condições de pesquisa
    search_conditions |= Q(nome__icontains=query)
    search_conditions |= Q(cpf__icontains=query)
    search_conditions |= Q(matricula_funcionario__icontains=query)
    
    # Aplicar a empresa atual como um filtro direto
    funcionarios = Funcionario.objects.filter(
        empresa=empresa_atual
    ).filter(
        search_conditions
    ).only('codigo', 'nome', 'cpf', 'nome_cargo')[:10]  # Limite para performance
    
    results = [
        {
            'codigo': f.codigo,
            'nome': f.nome,
            'cpf': f.cpf,
            'cargo': f.nome_cargo
        } 
        for f in funcionarios
    ]
    
    return JsonResponse({'results': results})

# Mantive as outras funções conforme o original, apenas otimizando quando necessário
@ensure_csrf_cookie
def login_view(request):
    """View para página de login (página principal)"""
    # Se o usuário já estiver autenticado, redireciona para o dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Usamos o formulário de autenticação padrão para este exemplo
    form = AuthenticationForm()
    
    return render(request, 'dashboard/login.html', {
        'form': form,
        'next': request.GET.get('next', '/dashboard/')
    })

def logout_view(request):
    """Realiza o logout do usuário e redireciona para a página de login"""
    # Limpar caches específicos do usuário ao fazer logout
    if request.user.is_authenticated:
        cache.delete(f"empresa_atual_{request.user.id}")
        cache.delete(f"empresas_usuario_{request.user.id}")
        
    logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect('login')

@login_required
def update_settings(request):
    """View para atualizar configurações de usuário"""
    if request.method == 'POST':
        # Verificar se é uma troca de empresa
        empresa_codigo = request.POST.get('empresa')
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        # Verificar se estamos trocando de empresa
        if empresa_codigo:
            try:
                # Verificar se o usuário tem acesso a esta empresa
                if request.user.tipo_usuario == 'admin' or AcessoEmpresa.objects.filter(usuario=request.user, empresa__codigo=empresa_codigo).exists():
                    # Limpar cache da empresa atual
                    cache.delete(f"empresa_atual_{request.user.id}")
                    
                    # Atualizar a empresa na sessão
                    request.session['empresa_atual'] = int(empresa_codigo)
                    messages.success(request, "Empresa alterada com sucesso.")
                else:
                    messages.error(request, "Você não tem acesso a esta empresa.")
            except Exception as e:
                messages.error(request, f"Erro ao trocar de empresa: {str(e)}")
        
        # Verificar se estamos alterando a senha
        if senha_atual and nova_senha and confirmar_senha:
            if nova_senha != confirmar_senha:
                messages.error(request, "As senhas não coincidem.")
            elif len(nova_senha) < 8:
                messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
            else:
                # Verificar se a senha atual está correta
                if request.user.check_password(senha_atual):
                    # Alterar a senha
                    request.user.set_password(nova_senha)
                    request.user.save()
                    
                    # Atualizar a sessão de autenticação para evitar logout
                    update_session_auth_hash(request, request.user)
                    
                    messages.success(request, "Senha alterada com sucesso.")
                else:
                    messages.error(request, "Senha atual incorreta.")
        
        # Retorno para a mesma página
        return redirect('dashboard')
    
    # Se não for POST, redirecionar para o dashboard
    return redirect('dashboard')

# Página de erro 404 personalizada
def custom_404(request, exception=None):
    """Redirecionar para login ao invés de mostrar erro 404"""
    messages.error(request, "A página solicitada não existe. Você foi redirecionado para a página de login.")
    return redirect('login')

# Página de erro 500 personalizada
def custom_500(request, exception=None):
    """Redirecionar para login ao invés de mostrar erro 500"""
    messages.error(request, "Ocorreu um erro interno no servidor. Por favor, tente novamente mais tarde.")
    return redirect('login')

# Exemplo de view protegida por JWT para API
class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "Esta é uma view protegida", "user": request.user.email})