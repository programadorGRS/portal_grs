// dashboard/static/dashboard/js/convocacao.js

/**
 * Portal GRS - Gerenciamento de Convocações de Exames
 * Script para manipulação da tela de convocações, gráficos e modal de detalhes
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar os gráficos se existirem dados
    if (typeof statusData !== 'undefined' && typeof evolucaoData !== 'undefined') {
        initCharts();
    }
    
    // Modal de detalhes
    const convocacaoModal = document.getElementById('convocacaoModal');
    const convocacaoModalClose = document.getElementById('convocacaoModalClose');
    
    // Fechar o modal ao clicar no botão de fechar
    if (convocacaoModalClose) {
        convocacaoModalClose.addEventListener('click', closeConvocacaoModal);
    }
    
    // Fechar o modal ao clicar fora dele
    window.addEventListener('click', function(event) {
        if (event.target === convocacaoModal) {
            closeConvocacaoModal();
        }
    });
    
    // Configurar botões de exportação
    setupExportButtons();
});

/**
 * Inicializa os gráficos da página
 */
function initCharts() {
    // Definir paleta de cores
    const colors = {
        vencido: '#ef4444',
        pendente: '#f59e0b',
        aVencer: '#3b82f6',
        emDia: '#10b981',
        semHistorico: '#9ca3af',
    };
    
    // 1. Gráfico de distribuição por status (rosca)
    const statusCtx = document.getElementById('statusChart');
    if (!statusCtx) return;
    
    const statusCtxContext = statusCtx.getContext('2d');
    
    // Criar os dados para o gráfico de status
    const statusLabels = statusData.map(item => item.label);
    const statusValues = statusData.map(item => item.count);
    const statusColors = statusData.map(item => {
        switch(item.status) {
            case 'Vencido': return colors.vencido;
            case 'Pendente': return colors.pendente;
            case 'A Vencer': return colors.aVencer;
            case 'Em dia': return colors.emDia;
            case 'Sem histórico': return colors.semHistorico;
            default: return '#9ca3af';
        }
    });
    
    // Criar o gráfico de rosca
    const statusChart = new Chart(statusCtxContext, {
        type: 'doughnut',
        data: {
            labels: statusLabels,
            datasets: [{
                data: statusValues,
                backgroundColor: statusColors,
                borderColor: '#ffffff',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 15,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const value = context.raw;
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // 2. Gráfico de evolução por período (linha)
    const evolucaoCtx = document.getElementById('evolucaoChart');
    if (!evolucaoCtx) return;
    
    const evolucaoCtxContext = evolucaoCtx.getContext('2d');
    
    // Extrair dados de evolução
    const evolucaoLabels = evolucaoData.labels;
    const evolucaoVencidos = evolucaoData.series.find(s => s.name === 'Vencidos')?.data || [];
    const evolucaoPendentes = evolucaoData.series.find(s => s.name === 'Pendentes')?.data || [];
    const evolucaoAVencer = evolucaoData.series.find(s => s.name === 'A Vencer')?.data || [];
    const evolucaoEmDia = evolucaoData.series.find(s => s.name === 'Em Dia')?.data || [];
    
    // Criar o gráfico de linha
    const evolucaoChart = new Chart(evolucaoCtxContext, {
        type: 'line',
        data: {
            labels: evolucaoLabels,
            datasets: [
                {
                    label: 'Vencidos',
                    data: evolucaoVencidos,
                    borderColor: colors.vencido,
                    backgroundColor: hexToRgba(colors.vencido, 0.1),
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Pendentes',
                    data: evolucaoPendentes,
                    borderColor: colors.pendente,
                    backgroundColor: hexToRgba(colors.pendente, 0.1),
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'A Vencer',
                    data: evolucaoAVencer,
                    borderColor: colors.aVencer,
                    backgroundColor: hexToRgba(colors.aVencer, 0.1),
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Em Dia',
                    data: evolucaoEmDia,
                    borderColor: colors.emDia,
                    backgroundColor: hexToRgba(colors.emDia, 0.1),
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: {
                        drawOnChartArea: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * Configura os botões de exportação CSV
 */
function setupExportButtons() {
    const exportarTodosBtn = document.getElementById('exportarTodosCSV');
    const exportarColaboradorBtn = document.getElementById('exportarColaboradorCSV');
    
    if (exportarTodosBtn) {
        exportarTodosBtn.addEventListener('click', function() {
            exportarTodosCSV();
        });
    }
    
    if (exportarColaboradorBtn) {
        exportarColaboradorBtn.addEventListener('click', function() {
            exportarColaboradorCSV();
        });
    }
}

/**
 * Função para mostrar o modal com detalhes da convocação
 * @param {number} funcionarioId - ID do funcionário
 */
function showConvocacaoDetails(funcionarioId) {
    const modal = document.getElementById('convocacaoModal');
    const modalTitle = document.getElementById('convocacaoModalTitle');
    const colaboradorInfo = document.getElementById('colaboradorInfo');
    const examesTableBody = document.getElementById('examesTableBody');
    
    // Verifica se os elementos existem
    if (!modal || !modalTitle || !colaboradorInfo || !examesTableBody) {
        console.error('Elementos do modal não encontrados');
        return;
    }
    
    // Limpar conteúdo anterior e mostrar loading
    colaboradorInfo.innerHTML = '<div class="loading-spinner"></div>';
    examesTableBody.innerHTML = `
        <tr>
            <td colspan="6" class="loading-data">
                <div class="loading-spinner"></div>
                <p>Carregando exames...</p>
            </td>
        </tr>
    `;
    
    // Mostrar o modal
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // Fazer uma requisição para obter os detalhes do funcionário
    fetch(`/api/convocacoes/funcionario/${funcionarioId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao obter dados do funcionário');
            }
            return response.json();
        })
        .then(data => {
            // Atualizar título do modal
            modalTitle.textContent = `Exames de ${data.funcionario.nome}`;
            
            // Atualizar informações do colaborador
            colaboradorInfo.innerHTML = `
                <h3>Informações do Colaborador</h3>
                <div class="info-grid">
                    <div class="info-group">
                        <div class="info-label">Nome</div>
                        <div class="info-value">${data.funcionario.nome || '-'}</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">CPF</div>
                        <div class="info-value">${data.funcionario.cpf || '-'}</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Matrícula</div>
                        <div class="info-value">${data.funcionario.matricula || '-'}</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Cargo</div>
                        <div class="info-value">${data.funcionario.cargo || '-'}</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Setor</div>
                        <div class="info-value">${data.funcionario.setor || '-'}</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Unidade</div>
                        <div class="info-value">${data.funcionario.unidade || '-'}</div>
                    </div>
                    <div class="info-group">
                        <div class="info-label">Data de Admissão</div>
                        <div class="info-value">${formatarData(data.funcionario.data_admissao) || '-'}</div>
                    </div>
                </div>
            `;
            
            // Preencher a tabela de exames
            if (data.exames && data.exames.length > 0) {
                examesTableBody.innerHTML = '';
                
                data.exames.forEach(exame => {
                    const tr = document.createElement('tr');
                    
                    // Define a classe com base no status
                    let statusClass = '';
                    if (exame.status === 'Vencido') statusClass = 'status-vencido';
                    else if (exame.status === 'Pendente') statusClass = 'status-pendente';
                    else if (exame.status === 'A Vencer') statusClass = 'status-a-vencer';
                    else if (exame.status === 'Em dia') statusClass = 'status-em-dia';
                    
                    tr.innerHTML = `
                        <td>${exame.exame || '-'}</td>
                        <td>${formatarData(exame.ultimo_pedido) || '-'}</td>
                        <td>${formatarData(exame.data_resultado) || '-'}</td>
                        <td>${exame.periodicidade ? exame.periodicidade + ' meses' : '-'}</td>
                        <td>${formatarData(exame.refazer) || '-'}</td>
                        <td><span class="status-badge ${statusClass}">${exame.status || '-'}</span></td>
                    `;
                    
                    examesTableBody.appendChild(tr);
                });
            } else {
                examesTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center;">Nenhum exame encontrado para este colaborador.</td>
                    </tr>
                `;
            }
            
            // Armazenar dados para exportação
            window.colaboradorAtual = data;
        })
        .catch(error => {
            console.error('Erro:', error);
            
            colaboradorInfo.innerHTML = `
                <div style="text-align: center; padding: var(--spacing-4); color: var(--color-error);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <h3>Erro ao carregar dados</h3>
                    <p>Não foi possível obter os dados do colaborador. Por favor, tente novamente.</p>
                </div>
            `;
            
            examesTableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center;">Erro ao carregar os exames.</td>
                </tr>
            `;
            
            // Mostrar um toast de erro se disponível
            if (window.showToast) {
                window.showToast('Erro', 'Não foi possível carregar os dados do colaborador', 'error');
            }
        });
}

/**
 * Fecha o modal de detalhes
 */
function closeConvocacaoModal() {
    const modal = document.getElementById('convocacaoModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

/**
 * Exporta todos os dados de convocações para CSV
 */
function exportarTodosCSV() {
    // Mostrar loading
    if (window.showLoading) {
        window.showLoading('Gerando arquivo CSV...');
    }
    
    // Fazer requisição para obter todos os dados
    fetch('/api/convocacoes/export-all/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao obter dados para exportação');
            }
            return response.json();
        })
        .then(data => {
            // Gerar CSV e fazer download
            generateCSV(data, 'convocacoes_todos');
            
            // Esconder loading
            if (window.hideLoading) {
                window.hideLoading();
            }
            
            // Mostrar mensagem de sucesso
            if (window.showToast) {
                window.showToast('Sucesso', 'Arquivo CSV gerado com sucesso!', 'success');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            
            // Esconder loading
            if (window.hideLoading) {
                window.hideLoading();
            }
            
            // Mostrar mensagem de erro
            if (window.showToast) {
                window.showToast('Erro', 'Não foi possível gerar o arquivo CSV. Tente novamente.', 'error');
            }
        });
}

/**
 * Exporta os dados do colaborador atual para CSV
 */
function exportarColaboradorCSV() {
    // Verificar se há dados do colaborador
    if (!window.colaboradorAtual) {
        if (window.showToast) {
            window.showToast('Erro', 'Não há dados para exportar', 'error');
        }
        return;
    }
    
    // Gerar CSV e fazer download
    generateCSV(window.colaboradorAtual, 'convocacoes_' + window.colaboradorAtual.funcionario.nome.replace(/\s+/g, '_').toLowerCase());
    
    // Mostrar mensagem de sucesso
    if (window.showToast) {
        window.showToast('Sucesso', 'Arquivo CSV gerado com sucesso!', 'success');
    }
}

/**
 * Gera um arquivo CSV a partir dos dados e inicia o download
 * @param {Object} data - Dados para o CSV
 * @param {string} filename - Nome do arquivo sem extensão
 */
function generateCSV(data, filename) {
    // Formatar os dados para CSV
    const csvRows = [];
    
    // Cabeçalho para dados de funcionário com exames
    if (data.funcionario && data.exames) {
        // Informações do funcionário
        csvRows.push(['Informações do Colaborador']);
        csvRows.push(['Nome', 'CPF', 'Matrícula', 'Cargo', 'Setor', 'Unidade', 'Data de Admissão']);
        csvRows.push([
            data.funcionario.nome || '',
            data.funcionario.cpf || '',
            data.funcionario.matricula || '',
            data.funcionario.cargo || '',
            data.funcionario.setor || '',
            data.funcionario.unidade || '',
            formatarData(data.funcionario.data_admissao) || ''
        ]);
        
        // Linha em branco
        csvRows.push([]);
        
        // Cabeçalho de exames
        csvRows.push(['Exames']);
        csvRows.push(['Exame', 'Último Pedido', 'Data Resultado', 'Periodicidade', 'Data Refazer', 'Status']);
        
        // Dados dos exames
        data.exames.forEach(exame => {
            csvRows.push([
                exame.exame || '',
                formatarData(exame.ultimo_pedido) || '',
                formatarData(exame.data_resultado) || '',
                exame.periodicidade ? exame.periodicidade + ' meses' : '',
                formatarData(exame.refazer) || '',
                exame.status || ''
            ]);
        });
    }
    // Cabeçalho para lista geral de convocações
    else if (Array.isArray(data)) {
        csvRows.push(['Nome', 'CPF', 'Matrícula', 'Cargo', 'Setor', 'Unidade', 'Exame', 'Último Pedido', 'Data Resultado', 'Periodicidade', 'Data Refazer', 'Status']);
        
        // Dados de todas as convocações
        data.forEach(item => {
            csvRows.push([
                item.nome || '',
                item.cpf || '',
                item.matricula || '',
                item.cargo || '',
                item.setor || '',
                item.unidade || '',
                item.exame || '',
                formatarData(item.ultimo_pedido) || '',
                formatarData(item.data_resultado) || '',
                item.periodicidade ? item.periodicidade + ' meses' : '',
                formatarData(item.refazer) || '',
                item.status || ''
            ]);
        });
    }
    
    // Converter para CSV
    let csvContent = csvRows.map(row => 
        row.map(value => 
            `"${String(value).replace(/"/g, '""')}"`
        ).join(',')
    ).join('\n');
    
    // Adicionar BOM para compatibilidade com Excel (UTF-8)
    const BOM = '\uFEFF';
    csvContent = BOM + csvContent;
    
    // Criar Blob e link para download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    // Configurar link para download
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}_${formatDateForFilename(new Date())}.csv`);
    link.style.visibility = 'hidden';
    
    // Adicionar ao documento, clicar e remover
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Formata uma data para exibição no formato DD/MM/YYYY
 * @param {string} dateString - Data em formato string
 * @returns {string} Data formatada ou string vazia se inválida
 */
function formatarData(dateString) {
    if (!dateString) return '';
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';
        
        const dia = String(date.getDate()).padStart(2, '0');
        const mes = String(date.getMonth() + 1).padStart(2, '0');
        const ano = date.getFullYear();
        
        return `${dia}/${mes}/${ano}`;
    } catch (e) {
        return '';
    }
}

/**
 * Formata uma data para uso em nome de arquivo (YYYY-MM-DD)
 * @param {Date} date - Objeto Date
 * @returns {string} Data formatada para nome de arquivo
 */
function formatDateForFilename(date) {
    const dia = String(date.getDate()).padStart(2, '0');
    const mes = String(date.getMonth() + 1).padStart(2, '0');
    const ano = date.getFullYear();
    
    return `${ano}-${mes}-${dia}`;
}

/**
 * Converte cor hex para rgba
 * @param {string} hex - Cor em formato hexadecimal
 * @param {number} alpha - Valor de transparência (0-1)
 * @returns {string} Cor em formato rgba
 */
function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Make functions globally available
window.showConvocacaoDetails = showConvocacaoDetails;
window.closeConvocacaoModal = closeConvocacaoModal;