document.addEventListener('DOMContentLoaded', function() {
    // Elementos do modal
    const settingsModal = document.getElementById('settingsModal');
    const settingsBtn = document.getElementById('settings-btn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const settingsForm = document.getElementById('settingsForm');
    
    // Garantir que o modal começa escondido
    if (settingsModal) {
        settingsModal.style.display = 'none';
        settingsModal.classList.remove('show');
    }
    
    // Função para abrir o modal
    function openModal() {
        if (settingsModal) {
            document.body.style.overflow = 'hidden'; // Impedir rolagem do fundo
            settingsModal.style.display = 'flex';
            // Pequeno delay para garantir que a transição funcione
            setTimeout(() => {
                settingsModal.classList.add('show');
            }, 10);
        }
    }
    
    // Função para fechar o modal
    function closeModal() {
        if (settingsModal) {
            settingsModal.classList.remove('show');
            // Esperar a transição terminar
            setTimeout(() => {
                settingsModal.style.display = 'none';
                document.body.style.overflow = ''; // Restaurar rolagem
            }, 300);
        }
    }
    
    // Abrir o modal ao clicar no botão de configurações
    if (settingsBtn) {
        settingsBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Fechar o dropdown do usuário
            const userDropdown = document.getElementById('user-dropdown');
            if (userDropdown && userDropdown.classList.contains('show')) {
                userDropdown.classList.remove('show');
            }
            
            openModal();
        });
    }
    
    // Fechar o modal ao clicar no botão de fechar
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    // Fechar o modal ao clicar no botão de cancelar
    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', closeModal);
    }
    
    // Fechar o modal ao clicar fora dele
    window.addEventListener('click', function(event) {
        if (event.target === settingsModal) {
            closeModal();
        }
    });
    
    // Impedir que cliques dentro do modal fechem o modal
    if (settingsModal) {
        const modalContent = settingsModal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    }
    
    // Validação do formulário
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(event) {
            // Validação da alteração de senha
            const senhaAtual = document.getElementById('senhaAtual').value;
            const novaSenha = document.getElementById('novaSenha').value;
            const confirmarSenha = document.getElementById('confirmarSenha').value;
            
            // Se algum campo de senha estiver preenchido, todos devem estar
            if (senhaAtual || novaSenha || confirmarSenha) {
                if (!senhaAtual || !novaSenha || !confirmarSenha) {
                    event.preventDefault();
                    showToast('Erro', 'Para alterar a senha, todos os campos devem ser preenchidos', 'error');
                    return;
                }
                
                // Verificar se as senhas coincidem
                if (novaSenha !== confirmarSenha) {
                    event.preventDefault();
                    showToast('Erro', 'As senhas não coincidem', 'error');
                    return;
                }
                
                // Verificar comprimento mínimo
                if (novaSenha.length < 8) {
                    event.preventDefault();
                    showToast('Erro', 'A senha deve ter pelo menos 8 caracteres', 'error');
                    return;
                }
            }
            
            // Mostrar o loading durante o envio
            showLoading('Salvando configurações...');
        });
    }
});