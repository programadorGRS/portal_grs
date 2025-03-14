document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('error-message');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            const username = document.getElementById('id_username').value;
            const password = document.getElementById('id_password').value;

            // Validação básica do lado do cliente
            if (!username || !password) {
                e.preventDefault();
                showToast('Atenção', 'Por favor, preencha todos os campos', 'warning');
                return;
            }
            
            // Mostrar tela de carregamento
            showLoading('Autenticando sua sessão com segurança...');
            
            // Não vamos bloquear o envio do formulário, pois o Django
            // lida com o processamento do formulário e redirecionamento.
            // A tela de loading ficará até que a nova página seja carregada.
        });
    }

    // Verificar token JWT armazenado no localStorage
    if (localStorage.getItem('access_token')) {
        // Verificar se o token ainda é válido
        verifyToken(localStorage.getItem('access_token'));
    }
    
    // Função para verificar se o token JWT ainda é válido
    function verifyToken(token) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        fetch('/api/token/verify/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                token: token
            })
        })
        .then(response => {
            if (response.ok) {
                // Token ainda é válido, redirecionar para o dashboard
                showLoading('Redirecionando para o dashboard...');
                window.location.href = '/dashboard/';
            } else {
                // Token expirou ou é inválido, limpar do localStorage
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }
        })
        .catch(error => {
            console.error('Erro ao verificar token:', error);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        });
    }
});