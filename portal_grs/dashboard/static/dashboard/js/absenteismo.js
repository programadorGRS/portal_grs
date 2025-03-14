// dashboard/static/dashboard/js/absenteismo.js

/**
 * Script para a página de Absenteísmo
 * Gerencia filtros, eventos, gráficos e funcionalidades adicionais
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicialização
    setupPeriodControls();
    setupAdvancedFilters();
    setupExportOptions();
    highlightFuncionariosProblemas();
    
    // Inicializar gráficos (função definida no bloco script do template)
    if (typeof initCharts === 'function') {
        initCharts();
    }
});

/**
 * Configuração do controle de períodos
 */
function setupPeriodControls() {
    const periodoTabs = document.querySelectorAll('.periodo-tab');
    const periodoInput = document.getElementById('periodoInput');
    const dateRangeFields = document.querySelectorAll('.date-range');
    
    if (!periodoTabs.length || !periodoInput) return;
    
    periodoTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const periodo = this.getAttribute('data-periodo');
            
            // Atualizar estado visual
            periodoTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Atualizar input
            periodoInput.value = periodo;
            
            // Mostrar/esconder campos de data personalizada
            if (periodo === 'custom') {
                dateRangeFields.forEach(field => field.style.display = 'block');
            } else {
                dateRangeFields.forEach(field => field.style.display = 'none');
                
                // Submeter o formulário automaticamente exceto para o modo personalizado
                document.getElementById('filtroForm').submit();
            }
        });
    });
}

/**
 * Configuração dos filtros avançados
 */
function setupAdvancedFilters() {
    // Adicionar botão de filtros avançados
    const filterForm = document.querySelector('.funcionarios-filters');
    
    if (filterForm) {
        // Criar botão de opções avançadas
        const advancedBtn = document.createElement('button');
        advancedBtn.type = 'button';
        advancedBtn.className = 'btn-secondary';
        advancedBtn.style.marginLeft = 'auto';
        advancedBtn.style.marginBottom = 'var(--spacing-4)';
        advancedBtn.innerHTML = 'Opções Avançadas <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';
        
        // Adicionar container para opções avançadas
        const advancedOptions = document.createElement('div');
        advancedOptions.className = 'advanced-options';
        advancedOptions.style.display = 'none';
        
        // Adicionar conteúdo de opções avançadas
        advancedOptions.innerHTML = `
            <div style="display: flex; flex-wrap: wrap; gap: var(--spacing-4);">
                <div style="flex: 1; min-width: 200px;">
                    <h3>Visualização de Gráficos</h3>
                    <div class="filter-group">
                        <label>Agrupar por</label>
                        <select id="groupBySelect" class="filter-input">
                            <option value="month">Mês</option>
                            <option value="week">Semana</option>
                            <option value="day">Dia</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Métrica principal</label>
                        <select id="metricSelect" class="filter-input">
                            <option value="count">Quantidade de Atestados</option>
                            <option value="days">Dias de Afastamento</option>
                            <option value="both" selected>Ambos</option>
                        </select>
                    </div>
                </div>
                
                <div style="flex: 1; min-width: 200px;">
                    <h3>Exportação de Dados</h3>
                    <div class="export-buttons">
                        <button type="button" id="exportCSV" class="btn-secondary">
                            Exportar CSV
                        </button>
                        <button type="button" id="exportPDF" class="btn-secondary">
                            Gerar Relatório PDF
                        </button>
                    </div>
                </div>
                
                <div style="flex: 1; min-width: 200px;">
                    <h3>Alertas e Notificações</h3>
                    <div class="filter-group">
                        <label>Limite de alerta (dias)</label>
                        <input type="number" id="alertThreshold" class="filter-input" value="3" min="1" max="30">
                    </div>
                    <div style="margin-top: var(--spacing-2);">
                        <label style="display: flex; align-items: center;">
                            <input type="checkbox" id="enableAlerts" checked>
                            <span style="margin-left: var(--spacing-2);">Ativar alertas</span>
                        </label>
                    </div>
                </div>
            </div>
        `;
        
        // Inserir elementos no DOM
        const firstFilter = filterForm.querySelector('.filter-group');
        if (firstFilter) {
            filterForm.insertBefore(advancedBtn, firstFilter);
            filterForm.insertBefore(advancedOptions, firstFilter);
        }
        
        // Adicionar comportamento do botão
        advancedBtn.addEventListener('click', function() {
            const isHidden = advancedOptions.style.display === 'none';
            advancedOptions.style.display = isHidden ? 'block' : 'none';
            advancedBtn.innerHTML = isHidden 
                ? 'Opções Avançadas <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 15l-6-6-6 6"/></svg>'
                : 'Opções Avançadas <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';
        });
        
        // Configurar eventos de visualização dos gráficos
        setupGraphVisualizationOptions();
    }
}

/**
 * Configura opções de visualização para os gráficos
 */
function setupGraphVisualizationOptions() {
    const groupBySelect = document.getElementById('groupBySelect');
    const metricSelect = document.getElementById('metricSelect');
    
    if (groupBySelect) {
        groupBySelect.addEventListener('change', function() {
            // Aqui adicionaríamos a lógica para reagrupar os dados
            // Na implementação real, isso exigiria uma chamada AJAX para 
            // obter dados reagrupados ou fazer o reagrupamento no cliente
            
            if (window.showToast) {
                window.showToast('Informação', 'Reagrupando dados por ' + this.value, 'info');
            }
            
            // Se os gráficos forem atualizados, recriar com novos dados
            if (typeof initCharts === 'function') {
                initCharts();
            }
        });
    }
    
    if (metricSelect) {
        metricSelect.addEventListener('change', function() {
            const value = this.value;
            
            // Lógica para atualizar a visualização dos gráficos
            const charts = getChartInstances();
            
            if (!charts.length) return;
            
            // Nos gráficos que têm diferentes métricas, mostrar/esconder datasets
            charts.forEach(chart => {
                if (chart.config && chart.config.type === 'line' && chart.data.datasets.length > 1) {
                    if (value === 'count') {
                        // Mostrar apenas contagem
                        chart.data.datasets[0].hidden = false;
                        chart.data.datasets[1].hidden = true;
                    } else if (value === 'days') {
                        // Mostrar apenas dias
                        chart.data.datasets[0].hidden = true;
                        chart.data.datasets[1].hidden = false;
                    } else {
                        // Mostrar ambos
                        chart.data.datasets[0].hidden = false;
                        chart.data.datasets[1].hidden = false;
                    }
                    
                    chart.update();
                }
            });
        });
    }
}

/**
 * Obtém instâncias de gráficos da página
 * Na prática, isso exigiria integração com a biblioteca Chart.js
 */
function getChartInstances() {
    // Na versão real, isso seria implementado conforme a biblioteca de gráficos
    return [];
}

/**
 * Configuração das opções de exportação
 */
function setupExportOptions() {
    // Adicionar funções aos botões de exportação
    const exportCSVBtn = document.getElementById('exportCSV');
    const exportPDFBtn = document.getElementById('exportPDF');
    
    if (exportCSVBtn) {
        exportCSVBtn.addEventListener('click', function() {
            downloadCSV();
        });
    }
    
    if (exportPDFBtn) {
        exportPDFBtn.addEventListener('click', function() {
            generatePDFReport();
        });
    }
}

/**
 * Gera dados de exemplo para exportação CSV
 */
function generateRandomData() {
    // Esta função é apenas para exemplo, na implementação real,
    // você usaria os dados reais da aplicação
    return [
        ['Funcionário', 'Matrícula', 'Setor', 'Dias Afastados', 'Início', 'Fim', 'Tipo', 'CID'],
        ['João Silva', '123456', 'Produção', '3', '01/02/2023', '03/02/2023', 'Atestado médico', 'J11'],
        ['Maria Santos', '789012', 'Administração', '2', '05/02/2023', '06/02/2023', 'Atestado médico', 'R10'],
        ['Carlos Oliveira', '345678', 'Logística', '5', '10/02/2023', '14/02/2023', 'Acidente de trabalho', 'S61'],
        ['Ana Pereira', '901234', 'RH', '10', '15/02/2023', '24/02/2023', 'Licença maternidade', 'O80']
    ];
}

/**
 * Gera e inicia o download de um arquivo CSV
 */
function downloadCSV() {
    // Na implementação real, você obteria esses dados do backend
    const data = generateRandomData();
    
    // Criar o conteúdo CSV
    let csvContent = "data:text/csv;charset=utf-8,";
    
    data.forEach(row => {
        csvContent += row.join(',') + '\r\n';
    });
    
    // Criar o link de download
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `absenteismo_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    
    // Simular clique para iniciar o download
    link.click();
    
    // Remover o link
    document.body.removeChild(link);
    
    // Mostrar confirmação
    if (window.showToast) {
        window.showToast('Sucesso', 'Arquivo CSV exportado com sucesso!', 'success');
    } else {
        alert('Arquivo CSV exportado com sucesso!');
    }
}

/**
 * Gera um relatório PDF
 */
function generatePDFReport() {
    // Na implementação real, seria necessário uma biblioteca como jsPDF
    // ou enviar uma requisição para o backend gerar o PDF
    
    // Simular processamento
    if (window.showLoading) {
        window.showLoading('Gerando relatório PDF...');
    }
    
    setTimeout(() => {
        if (window.hideLoading) {
            window.hideLoading();
        }
        
        if (window.showToast) {
            window.showToast('Sucesso', 'Relatório PDF gerado com sucesso! O download começará em instantes.', 'success');
        } else {
            alert('Relatório PDF gerado com sucesso!');
        }
    }, 2000);
}

/**
 * Destaca visualmente funcionários com problemas de absenteísmo
 */
function highlightFuncionariosProblemas() {
    const alertThreshold = document.getElementById('alertThreshold')?.value || 3;
    const enableAlerts = document.getElementById('enableAlerts')?.checked || false;
    
    if (!enableAlerts) return;
    
    const funcionariosTable = document.querySelector('.funcionarios-table');
    if (!funcionariosTable) return;
    
    const rows = funcionariosTable.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 7) {
            const totalAtestados = parseInt(cells[5].textContent);
            const totalDias = parseInt(cells[6].textContent);
            
            // Realçar funcionários com muitos atestados ou muitos dias
            if (totalAtestados >= 3 || totalDias >= parseInt(alertThreshold)) {
                row.classList.add('alert-row');
                row.classList.add('highlight-critical');
                
                // Adicionar ícone de alerta
                const nomeCell = cells[0];
                const currentText = nomeCell.textContent;
                nomeCell.innerHTML = `
                    <div class="alert-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                            <line x1="12" y1="9" x2="12" y2="13"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                        </svg>
                        ${currentText}
                    </div>
                `;
            }
        }
    });
}

/**
 * Event listeners para a configuração de alertas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar listener para o checkbox de alertas
    const enableAlertsCheckbox = document.getElementById('enableAlerts');
    if (enableAlertsCheckbox) {
        enableAlertsCheckbox.addEventListener('change', highlightFuncionariosProblemas);
    }
    
    // Adicionar listener para o input de limite
    const alertThresholdInput = document.getElementById('alertThreshold');
    if (alertThresholdInput) {
        alertThresholdInput.addEventListener('change', highlightFuncionariosProblemas);
    }
    
    // Inicializar destacamento após 1 segundo
    setTimeout(highlightFuncionariosProblemas, 1000);
});

/**
 * Adiciona uma comparação com período anterior (dummy)
 */
function addComparisonView() {
    const dashboardContent = document.querySelector('.dashboard-content');
    if (!dashboardContent) return;
    
    const comparisonSection = document.createElement('div');
    comparisonSection.className = 'comparison-view';
    comparisonSection.innerHTML = `
        <h2 class="comparison-title">Comparação com Período Anterior</h2>
        <div class="comparison-row">
            <div class="comparison-item">
                <div class="comparison-header">Total de Atestados</div>
                <div class="comparison-value">
                    <span class="number">87</span>
                    <span class="change negative">+12.4%</span>
                </div>
            </div>
            <div class="comparison-item">
                <div class="comparison-header">Dias Perdidos</div>
                <div class="comparison-value">
                    <span class="number">342</span>
                    <span class="change negative">+8.2%</span>
                </div>
            </div>
        </div>
        <div class="comparison-row">
            <div class="comparison-item">
                <div class="comparison-header">Média por Atestado</div>
                <div class="comparison-value">
                    <span class="number">3.9</span>
                    <span class="change negative">+0.3</span>
                </div>
            </div>
            <div class="comparison-item">
                <div class="comparison-header">Funcionários Afastados</div>
                <div class="comparison-value">
                    <span class="number">52</span>
                    <span class="change positive">-5.4%</span>
                </div>
            </div>
        </div>
    `;
    
    dashboardContent.appendChild(comparisonSection);
}

// Adaptar a interface com base no tamanho da janela
window.addEventListener('resize', function() {
    if (window.innerWidth < 768) {
        // Adaptar para dispositivos móveis
        // Por exemplo, ajustar a visualização de gráficos
    } else {
        // Restaurar para desktop
    }
});