/**
 * base.js - Arquivo base otimizado
 * Portal GRS - Versão 2.0
 */

// Execução imediata para evitar poluição do escopo global
(function() {
    'use strict';
    
    // Objeto central para gerenciar funções do sistema
    const GRS = {
        // Estado da aplicação
        state: {
            isLoading: false,
            currentPage: window.location.pathname,
            activeModals: []
        },
        
        // Inicialização da aplicação
        init: function() {
            this.setupEventListeners();
            this.setupNavigation();
            this.setupUserControls();
            this.initCurrentPageSpecifics();
            
            // Remover a classe loading caso esteja presente no carregamento inicial
            document.body.classList.remove('loading');
        },
        
        // Configuração de listeners de eventos globais
        setupEventListeners: function() {
            // Delegação de eventos para o documento
            document.addEventListener('click', this.handleGlobalClicks.bind(this));
            
            // Adicionar listeners para todos os links que devem mostrar a tela de loading
            document.querySelectorAll('a:not([target="_blank"])').forEach(link => {
                if (!link.getAttribute('data-no-loading')) {
                    link.addEventListener('click', this.showLoadingOnNavigation.bind(this));
                }
            });
        },
        
        // Evento para manipular cliques globais usando delegação de eventos
        handleGlobalClicks: function(event) {
            // Fechar dropdowns quando clicar fora deles
            const userDropdown = document.getElementById('user-dropdown');
            const userProfile = document.getElementById('user-profile');
            
            if (userDropdown && userDropdown.classList.contains('show')) {
                if (!userDropdown.contains(event.target) && event.target !== userProfile) {
                    userDropdown.classList.remove('show');
                }
            }
            
            // Fechar modais quando clicar no background
            if (event.target.classList.contains('settings-modal') || 
                event.target.classList.contains('funcionario-modal')) {
                this.closeModal(event.target.id);
            }
        },
        
        // Configuração da navegação
        setupNavigation: function() {
            // Destacar o item de menu atual
            const menuItems = document.querySelectorAll('.sidebar-menu-item');
            const currentPath = this.state.currentPath || window.location.pathname;
            
            menuItems.forEach(item => {
                item.classList.remove('active');
                const href = item.getAttribute('href');
                
                if (href === currentPath || 
                    (href === '/dashboard/' && currentPath === '/') || 
                    (currentPath.startsWith(href) && href !== '/')) {
                    item.classList.add('active');
                }
            });
        },
        
        // Configuração de controles do usuário
        setupUserControls: function() {
            const userProfile = document.getElementById('user-profile');
            const settingsBtn = document.getElementById('settings-btn');
            const logoutBtn = document.getElementById('logout-btn');
            
            if (userProfile) {
                userProfile.addEventListener('click', (event) => {
                    event.stopPropagation();
                    document.getElementById('user-dropdown').classList.toggle('show');
                });
            }
            
            if (settingsBtn) {
                settingsBtn.addEventListener('click', (event) => {
                    event.stopPropagation();
                    this.openModal('settingsModal');
                    document.getElementById('user-dropdown').classList.remove('show');
                });
            }
            
            if (logoutBtn) {
                logoutBtn.addEventListener('click', () => {
                    this.showLoading('Encerrando sua sessão...');
                    window.location.href = '/logout/';
                });
            }
        },
        
        // Inicializar funcionalidades específicas da página atual
        initCurrentPageSpecifics: function() {
            const path = window.location.pathname;
            
            if (path.includes('/funcionarios')) {
                this.initFuncionariosPage();
            } else if (path.includes('/dashboard')) {
                this.initDashboardPage();
            } else if (path.includes('/login')) {
                this.initLoginPage();
            }
        },
        
        // Inicialização da página de funcionários
        initFuncionariosPage: function() {
            // Configurar funcionamento do modal de funcionários
            const funcionarioModalClose = document.getElementById('funcionarioModalClose');
            
            if (funcionarioModalClose) {
                funcionarioModalClose.addEventListener('click', () => {
                    this.closeModal('funcionarioModal');
                });
            }
            
            // Configurar filtros com debounce para melhorar performance
            const filterInputs = document.querySelectorAll('.filter-input');
            filterInputs.forEach(input => {
                if (input.tagName === 'INPUT') {
                    input.addEventListener('input', this.debounce(() => {
                        document.querySelector('.funcionarios-filters').submit();
                    }, 500));
                }
            });
            
            // Definir função global para mostrar detalhes do funcionário
            window.showFuncionarioDetails = this.showFuncionarioDetails.bind(this);
        },
        
        // Inicialização da página de dashboard
        initDashboardPage: function() {
            // Carregar dados para os cards do dashboard via AJAX para melhorar velocidade inicial
            this.loadDashboardData();
        },
        
        // Inicialização da página de login
        initLoginPage: function() {
            const loginForm = document.getElementById('loginForm');
            
            if (loginForm) {
                loginForm.addEventListener('submit', (e) => {
                    const username = document.getElementById('id_username').value;
                    const password = document.getElementById('id_password').value;
                    
                    if (!username || !password) {
                        e.preventDefault();
                        window.showToast('Atenção', 'Por favor, preencha todos os campos', 'warning');
                        return;
                    }
                    
                    this.showLoading('Autenticando sua sessão com segurança...');
                });
            }
            
            // Verificar token JWT armazenado no localStorage
            if (localStorage.getItem('access_token')) {
                this.verifyToken(localStorage.getItem('access_token'));
            }
        },
        
        // Verificar token JWT (para página de login)
        verifyToken: function(token) {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            fetch('/api/token/verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ token: token })
            })
            .then(response => {
                if (response.ok) {
                    this.showLoading('Redirecionando para o dashboard...');
                    window.location.href = '/dashboard/';
                } else {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            })
            .catch(error => {
                console.error('Erro ao verificar token:', error);
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            });
        },
        
        // Carregar dados do dashboard via AJAX
        loadDashboardData: function() {
            // Implementação simplificada - supondo que você teria uma API para isto
            // Aqui seria o código para carregar dados dos cards via fetch() e atualizar os números
        },
        
        // Exibir detalhes do funcionário (modal)
        showFuncionarioDetails: function(codigo) {
            const modal = document.getElementById('funcionarioModal');
            const modalTitle = document.getElementById('funcionarioModalTitle');
            const detailsContainer = document.getElementById('funcionarioDetails');
            
            // Mostrar loading
            this.showLoading('Carregando dados do colaborador...');
            
            // Fazer requisição AJAX usando o campo codigo (primary key correto)
            fetch(`/api/funcionarios/${codigo}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao obter dados do colaborador');
                    }
                    return response.json();
                })
                .then(data => {
                    // Preencher o título
                    modalTitle.textContent = `Detalhes de ${data.nome}`;
                    
                    // Preencher os detalhes (mantive sua implementação original)
                    detailsContainer.innerHTML = `
                        <div class="detail-section">
                            <h3 class="detail-section-title">Informações Pessoais</h3>
                            <div class="funcionario-details">
                                <div class="detail-group">
                                    <div class="detail-label">Nome</div>
                                    <div class="detail-value">${data.nome || '-'}</div>
                                </div>
                                <div class="detail-group">
                                    <div class="detail-label">CPF</div>
                                    <div class="detail-value">${data.cpf || '-'}</div>
                                </div>
                                <div class="detail-group">
                                    <div class="detail-label">RG</div>
                                    <div class="detail-value">${data.rg || '-'} ${data.orgao_emissor_rg ? '- ' + data.orgao_emissor_rg : ''} ${data.uf_rg ? '- ' + data.uf_rg : ''}</div>
                                </div>
                                <!-- Outros campos como no original -->
                            </div>
                        </div>
                        
                        <!-- Outras seções... -->
                    `;
                    
                    // Esconder loading
                    this.hideLoading();
                    
                    // Mostrar o modal com uma transição suave
                    this.openModal('funcionarioModal');
                })
                .catch(error => {
                    this.hideLoading();
                    window.showToast('Erro', 'Não foi possível carregar os dados do colaborador.', 'error');
                    console.error('Erro:', error);
                });
        },
        
        // Abrir um modal
        openModal: function(modalId) {
            const modal = document.getElementById(modalId);
            if (!modal) return;
            
            // Impedir rolagem do body
            document.body.style.overflow = 'hidden';
            
            // Mostrar o modal com uma transição suave
            modal.style.display = 'flex';
            this.state.activeModals.push(modalId);
            
            // Pequeno delay para garantir que a transição funcione
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
        },
        
        // Fechar um modal
        closeModal: function(modalId) {
            const modal = document.getElementById(modalId);
            if (!modal) return;
            
            modal.classList.remove('show');
            
            // Remover do array de modais ativos
            const index = this.state.activeModals.indexOf(modalId);
            if (index > -1) {
                this.state.activeModals.splice(index, 1);
            }
            
            // Restaurar rolagem do body apenas se não houver mais modais ativos
            if (this.state.activeModals.length === 0) {
                document.body.style.overflow = '';
            }
            
            // Esperar a transição terminar antes de ocultar
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        },
        
        // Mostrar tela de loading
        showLoading: function(message) {
            this.state.isLoading = true;
            
            // Verificar se o elemento de loading já existe
            let loadingOverlay = document.querySelector('.loading-overlay');
            
            if (!loadingOverlay) {
                // Criar o overlay de loading
                loadingOverlay = document.createElement('div');
                loadingOverlay.className = 'loading-overlay';
                
                // Criar a estrutura interna
                loadingOverlay.innerHTML = `
                    <div class="background-elements">
                        <div class="background-circle"></div>
                        <div class="background-circle"></div>
                    </div>
                    
                    <div class="loading-container">
                        <div class="loading-dots">
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                        </div>
                        <div class="loading-text">Carregando</div>
                        <div class="loading-subtext">Preparando seus dados com segurança e precisão...</div>
                    </div>
                `;
                
                // Adicionar ao body
                document.body.appendChild(loadingOverlay);
            }
            
            // Atualizar a mensagem se fornecida
            if (message) {
                const loadingSubtext = loadingOverlay.querySelector('.loading-subtext');
                if (loadingSubtext) {
                    loadingSubtext.textContent = message;
                }
            }
            
            // Adicionar classe active para mostrar o overlay
            loadingOverlay.classList.add('active');
        },
        
        // Ocultar tela de loading
        hideLoading: function() {
            this.state.isLoading = false;
            const loadingOverlay = document.querySelector('.loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.classList.remove('active');
            }
        },
        
        // Mostrar loading durante navegação
        showLoadingOnNavigation: function(e) {
            // Não mostrar loading se for clique em nova aba ou com modificadores
            if (e.ctrlKey || e.metaKey || e.shiftKey || e.which === 2) {
                return;
            }
            
            this.showLoading('Navegando para a próxima página...');
        },
        
        // Função de debounce para limitar chamadas frequentes
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };
    
    // Inicializar a aplicação quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', () => {
        GRS.init();
        
        // Tornar o objeto GRS acessível globalmente
        window.GRS = GRS;
    });
    
    // Implementar funções toast específicas
    window.showToast = function(title, message, type = 'info', duration = 5000) {
        // Remove qualquer toast existente
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => {
            toast.remove();
        });
        
        // Ícones SVG para diferentes tipos de toast
        const toastIcons = {
            error: '<svg class="error-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
            success: '<svg class="success-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>',
            warning: '<svg class="warning-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>',
            info: '<svg class="info-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
        };
        
        // Títulos padrão para diferentes tipos de toast
        const defaultTitles = {
            error: 'Erro',
            success: 'Sucesso',
            warning: 'Aviso',
            info: 'Informação'
        };
        
        // Se o título não for fornecido, use o padrão para o tipo
        if (!title) {
            title = defaultTitles[type] || 'Notificação';
        }
        
        // Criar container do toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Criar conteúdo do toast
        toast.innerHTML = `
            <div class="toast-icon">
                ${toastIcons[type] || toastIcons.info}
            </div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Fechar">&times;</button>
        `;
        
        // Adicionar toast ao documento
        document.body.appendChild(toast);
        
        // Obter botão de fechar
        const closeButton = toast.querySelector('.toast-close');
        
        // Manipular clique no botão de fechar
        closeButton.addEventListener('click', () => {
            toast.classList.add('hide');
            setTimeout(() => {
                toast.remove();
            }, 300);
        });
        
        // Remoção automática após a duração
        if (duration > 0) {
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    toast.classList.add('hide');
                    setTimeout(() => {
                        toast.remove();
                    }, 300);
                }
            }, duration);
        }
        
        return toast;
    };
})();