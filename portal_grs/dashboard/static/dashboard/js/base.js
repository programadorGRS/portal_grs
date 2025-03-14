// Base JavaScript para o Portal GRS
document.addEventListener('DOMContentLoaded', function() {
    // Dropdown do perfil de usuário
    const userProfile = document.getElementById('user-profile');
    const userDropdown = document.getElementById('user-dropdown');
    
    if (userProfile && userDropdown) {
        userProfile.addEventListener('click', function(event) {
            event.stopPropagation();
            userDropdown.classList.toggle('show');
        });
    }
    
    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function(event) {
        if (userDropdown && userDropdown.classList.contains('show')) {
            if (!userDropdown.contains(event.target) && event.target !== userProfile) {
                userDropdown.classList.remove('show');
            }
        }
    });
    
    // Configurações e Logout
    const settingsBtn = document.getElementById('settings-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const settingsModal = document.getElementById('settingsModal');
    
    if (settingsBtn && settingsModal) {
        settingsBtn.addEventListener('click', function() {
            settingsModal.style.display = 'flex';
            setTimeout(() => {
                settingsModal.classList.add('show');
            }, 10);
            
            if (userDropdown) {
                userDropdown.classList.remove('show');
            }
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            window.location.href = '/logout/';
        });
    }
    
    // Configuração do modal
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function() {
            closeModal('settingsModal');
        });
    }
    
    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', function() {
            closeModal('settingsModal');
        });
    }
    
    // Fechar modais ao clicar fora deles
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('settings-modal') || 
            event.target.classList.contains('funcionario-modal')) {
            closeModal(event.target.id);
        }
    });
    
    // Garantir que os links do sidebar funcionem em tela cheia
    const sidebarLinks = document.querySelectorAll('.sidebar-menu-item');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Apenas para links normais, não para botões ou outras interações
            if (e.currentTarget.tagName === 'A' && !e.ctrlKey && !e.shiftKey && !e.metaKey && e.button !== 1) {
                // Adicionar classe de loading antes de navegar
                document.body.classList.add('loading');
            }
        });
    });
    
    // Garantir que o menu lateral seja corretamente marcado como ativo
    function setActiveMenuItem() {
        const currentPath = window.location.pathname;
        const menuItems = document.querySelectorAll('.sidebar-menu-item');
        
        menuItems.forEach(item => {
            // Remove active de todos os itens
            item.classList.remove('active');
            
            // Verifica se o href do item corresponde ao path atual
            const href = item.getAttribute('href');
            if (href === currentPath || 
                (href === '/dashboard/' && currentPath === '/') || 
                (currentPath.startsWith(href) && href !== '/')) {
                item.classList.add('active');
            }
        });
    }
    
    setActiveMenuItem();
    
    // Função para fechar modais
    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    };
    
    // Função para mostrar o modal de detalhes do funcionário
    window.showFuncionarioDetails = function(id) {
        const modal = document.getElementById('funcionarioModal');
        const modalTitle = document.getElementById('funcionarioModalTitle');
        const detailsContainer = document.getElementById('funcionarioDetails');
        
        if (!modal || !modalTitle || !detailsContainer) {
            console.error('Elementos do modal não encontrados');
            return;
        }
        
        // Mostrar loading
        detailsContainer.innerHTML = `
            <div class="loading-indicator" style="text-align: center; padding: 2rem;">
                <div class="loading-spinner" style="display: inline-block; width: 40px; height: 40px; border: 3px solid #f3f3f3; border-top: 3px solid #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem;"></div>
                <p>Carregando dados do colaborador...</p>
            </div>
        `;
        
        // Mostrar o modal imediatamente com o indicador de carregamento
        modal.style.display = 'flex';
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // Fazer requisição AJAX para obter os dados do funcionário
        fetch(`/api/funcionarios/${id}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao obter dados: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Preencher o título
                modalTitle.textContent = `Detalhes de ${data.nome}`;
                
                // Preencher os detalhes
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
                            <div class="detail-group">
                                <div class="detail-label">Data de Nascimento</div>
                                <div class="detail-value">${data.data_nascimento || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Sexo</div>
                                <div class="detail-value">${data.sexo === 1 ? 'Masculino' : data.sexo === 2 ? 'Feminino' : '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Estado Civil</div>
                                <div class="detail-value">${getEstadoCivil(data.estado_civil)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3 class="detail-section-title">Informações de Contato</h3>
                        <div class="funcionario-details">
                            <div class="detail-group">
                                <div class="detail-label">Endereço</div>
                                <div class="detail-value">${data.endereco || '-'} ${data.numero_endereco ? ', ' + data.numero_endereco : ''}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Bairro</div>
                                <div class="detail-value">${data.bairro || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Cidade/UF</div>
                                <div class="detail-value">${data.cidade || '-'} ${data.uf ? '- ' + data.uf : ''}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">CEP</div>
                                <div class="detail-value">${data.cep || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Telefone</div>
                                <div class="detail-value">${data.telefone_residencial || data.telefone_celular || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Email</div>
                                <div class="detail-value">${data.email || '-'}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3 class="detail-section-title">Informações Profissionais</h3>
                        <div class="funcionario-details">
                            <div class="detail-group">
                                <div class="detail-label">Matrícula</div>
                                <div class="detail-value">${data.matricula_funcionario || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Cargo</div>
                                <div class="detail-value">${data.nome_cargo || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Setor</div>
                                <div class="detail-value">${data.nome_setor || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Unidade</div>
                                <div class="detail-value">${data.nome_unidade || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Centro de Custo</div>
                                <div class="detail-value">${data.nome_centro_custo || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Data de Admissão</div>
                                <div class="detail-value">${data.data_admissao || '-'}</div>
                            </div>
                            <div class="detail-group">
                                <div class="detail-label">Situação</div>
                                <div class="detail-value">${data.situacao || '-'}</div>
                            </div>
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Erro:', error);
                detailsContainer.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: #ef4444;">
                        <h3>Erro ao carregar dados</h3>
                        <p>Não foi possível obter os detalhes do funcionário. Por favor, tente novamente mais tarde.</p>
                    </div>
                `;
                
                // Mostrar um toast de erro
                if (window.showToast) {
                    window.showToast('Erro', 'Não foi possível carregar os dados do colaborador.', 'error');
                }
            });
    };
    
    // Função para obter o estado civil por código
    function getEstadoCivil(codigo) {
        switch(codigo) {
            case 1: return 'Solteiro(a)';
            case 2: return 'Casado(a)';
            case 3: return 'Separado(a)';
            case 4: return 'Desquitado(a)';
            case 5: return 'Viúvo(a)';
            case 6: return 'Outros';
            case 7: return 'Divorciado(a)';
            default: return '-';
        }
    }
    
    // Função de toast
    window.showToast = function(title, message, type = 'info', duration = 5000) {
        // Remover toasts existentes
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
        // Ícones SVG para diferentes tipos de toast
        const toastIcons = {
            error: '<svg class="error-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
            success: '<svg class="success-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>',
            warning: '<svg class="warning-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>',
            info: '<svg class="info-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
        };
        
        // Criar o toast
        const toast = document.createElement('div');
        toast.className = `toast ${type || 'info'}`;
        
        // HTML do toast
        toast.innerHTML = `
            <div class="toast-icon">
                ${toastIcons[type] || toastIcons.info}
            </div>
            <div class="toast-content">
                <div class="toast-title">${title || (type === 'error' ? 'Erro' : type === 'success' ? 'Sucesso' : type === 'warning' ? 'Aviso' : 'Informação')}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Fechar">&times;</button>
        `;
        
        // Adicionar ao body
        document.body.appendChild(toast);
        
        // Configurar evento para fechar o toast
        const closeButton = toast.querySelector('.toast-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                toast.classList.add('hide');
                setTimeout(() => {
                    if (document.body.contains(toast)) {
                        document.body.removeChild(toast);
                    }
                }, 300);
            });
        }
        
        // Auto-remover depois do tempo definido
        if (duration > 0) {
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    toast.classList.add('hide');
                    setTimeout(() => {
                        if (document.body.contains(toast)) {
                            document.body.removeChild(toast);
                        }
                    }, 300);
                }
            }, duration);
        }
        
        return toast;
    };
});

// Animação keyframe para o spinner (define se não existir)
if (!document.querySelector('style#loading-animations')) {
    const style = document.createElement('style');
    style.id = 'loading-animations';
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}