// dashboard/static/dashboard/js/funcionarios.js

document.addEventListener('DOMContentLoaded', function() {
    // Modal de detalhes
    const funcionarioModal = document.getElementById('funcionarioModal');
    const funcionarioModalClose = document.getElementById('funcionarioModalClose');
    
    // Fechar o modal ao clicar no botão de fechar
    if (funcionarioModalClose) {
        funcionarioModalClose.addEventListener('click', closeFuncionarioModal);
    }
    
    // Fechar o modal ao clicar fora dele
    window.addEventListener('click', function(event) {
        if (event.target === funcionarioModal) {
            closeFuncionarioModal();
        }
    });
});

// Função para mostrar o modal de detalhes do funcionário
function showFuncionarioDetails(id) {
    // Obter o modal e o título
    const modal = document.getElementById('funcionarioModal');
    const modalTitle = document.getElementById('funcionarioModalTitle');
    const detailsContainer = document.getElementById('funcionarioDetails');
    
    // Mostrar loading
    showLoading('Carregando dados do colaborador...');
    
    // Fazer requisição AJAX para obter os dados do funcionário
    fetch(`/api/funcionarios/${id}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao obter dados do colaborador');
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
                        <div class="detail-group">
                            <div class="detail-label">Nome da Mãe</div>
                            <div class="detail-value">${data.nm_mae_funcionario || '-'}</div>
                        </div>
                        <div class="detail-group">
                            <div class="detail-label">Naturalidade</div>
                            <div class="detail-value">${data.naturalidade || '-'}</div>
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
                            <div class="detail-label">Telefone Residencial</div>
                            <div class="detail-value">${data.telefone_residencial || '-'}</div>
                        </div>
                        <div class="detail-group">
                            <div class="detail-label">Telefone Celular</div>
                            <div class="detail-value">${data.telefone_celular || '-'}</div>
                        </div>
                        <div class="detail-group">
                            <div class="detail-label">Telefone Comercial</div>
                            <div class="detail-value">${data.tel_comercial || '-'}</div>
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
                            <div class="detail-label">Empresa</div>
                            <div class="detail-value">${data.nome_empresa || '-'}</div>
                        </div>
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
                            <div class="detail-label">Data de Demissão</div>
                            <div class="detail-value">${data.data_demissao || '-'}</div>
                        </div>
                        <div class="detail-group">
                            <div class="detail-label">Situação</div>
                            <div class="detail-value">${data.situacao || '-'}</div>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3 class="detail-section-title">Documentos</h3>
                    <div class="funcionario-details">
                        <div class="detail-group">
                            <div class="detail-label">PIS</div>
                            <div class="detail-value">${data.pis || '-'}</div>
                        </div>
                        <div class="detail-group">
                            <div class="detail-label">CTPS</div>
                            <div class="detail-value">${data.ctps || '-'} ${data.serie_ctps ? '- Série: ' + data.serie_ctps : ''}</div>
                        </div>
                    </div>
                </div>
            `;
            
            // Esconder loading
            hideLoading();
            
            // Mostrar o modal
            modal.style.display = 'flex';
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
        })
        .catch(error => {
            hideLoading();
            showToast('Erro', 'Não foi possível carregar os dados do colaborador.', 'error');
            console.error('Erro:', error);
        });
}

// Função para fechar o modal
function closeFuncionarioModal() {
    const modal = document.getElementById('funcionarioModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

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