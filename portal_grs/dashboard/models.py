# dashboard/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Gerenciador de modelo personalizado para o modelo de Usuário customizado."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('tipo_usuario', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Tela(models.Model):
    """Modelo para armazenar as telas do sistema."""
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True, db_index=True)
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tela'
        verbose_name_plural = 'Telas'
        ordering = ['nome']
        db_table = 'telas'
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['codigo']),
        ]
    
    def __str__(self):
        return self.nome


class Empresa(models.Model):
    """Modelo para armazenar informações das empresas."""
    UF_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]
    
    cnpj_validator = RegexValidator(
        regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
        message='CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX'
    )
    
    cep_validator = RegexValidator(
        regex=r'^\d{5}-\d{3}$',
        message='CEP deve estar no formato XXXXX-XXX'
    )
    
    codigo = models.BigIntegerField(primary_key=True, verbose_name='Código')
    nome_abreviado = models.CharField(max_length=60, verbose_name='Nome Abreviado')
    razao_social_inicial = models.CharField(max_length=200, verbose_name='Razão Social Inicial')
    razao_social = models.CharField(max_length=200, verbose_name='Razão Social')
    endereco = models.CharField(max_length=110, verbose_name='Endereço')
    numero_endereco = models.CharField(max_length=20, verbose_name='Número')
    complemento_endereco = models.CharField(max_length=300, blank=True, null=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=80, verbose_name='Bairro')
    cidade = models.CharField(max_length=50, verbose_name='Cidade')
    cep = models.CharField(max_length=11, validators=[cep_validator], verbose_name='CEP')
    uf = models.CharField(max_length=2, choices=UF_CHOICES, verbose_name='UF')
    cnpj = models.CharField(max_length=20, validators=[cnpj_validator], unique=True, db_index=True, verbose_name='CNPJ')
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name='Inscrição Estadual')
    inscricao_municipal = models.CharField(max_length=20, blank=True, null=True, verbose_name='Inscrição Municipal')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    codigo_cliente_integracao = models.CharField(max_length=20, blank=True, null=True, verbose_name='Código Cliente Integração')
    codigo_cliente_int = models.CharField(max_length=30, blank=True, null=True, verbose_name='Cód. Cliente (INT.)')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome_abreviado']
        db_table = 'empresas'
        indexes = [
            models.Index(fields=['nome_abreviado']),
            models.Index(fields=['cnpj']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return self.nome_abreviado


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo de Usuário personalizado usando email como campo de login."""
    TIPO_USUARIO_CHOICES = [
        ('admin', 'Administrador'),
        ('normal', 'Usuário Normal'),
    ]
    
    email = models.EmailField(unique=True, db_index=True)
    nome = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_staff = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultima_sessao = models.DateTimeField(null=True, blank=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='normal')
    empresa_principal = models.ForeignKey(
        Empresa, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='usuarios_principal'
    )
    acesso_telas = models.ManyToManyField(Tela, through='AcessoTela')
    acesso_empresas = models.ManyToManyField(Empresa, through='AcessoEmpresa', related_name='usuarios_com_acesso')
    
    # Define o gerenciador de objetos personalizado
    objects = UserManager()
    
    # Define qual campo será usado como username para login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome']
        db_table = 'usuarios'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tipo_usuario']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.nome
    
    def get_short_name(self):
        return self.nome.split(' ')[0]
    
    def registrar_sessao(self):
        """Registra a data/hora da última sessão do usuário."""
        self.ultima_sessao = timezone.now()
        self.save(update_fields=['ultima_sessao'])


class AcessoTela(models.Model):
    """Modelo para relacionamento Many-to-Many entre Usuário e Tela com permissões específicas."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tela = models.ForeignKey(Tela, on_delete=models.CASCADE)
    permissao_leitura = models.BooleanField(default=True)
    permissao_escrita = models.BooleanField(default=False)
    permissao_exclusao = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Acesso à Tela'
        verbose_name_plural = 'Acessos às Telas'
        db_table = 'acesso_telas'
        unique_together = ('usuario', 'tela')
        indexes = [
            models.Index(fields=['usuario', 'tela']),
        ]
    
    def __str__(self):
        return f'{self.usuario.email} - {self.tela.nome}'


class AcessoEmpresa(models.Model):
    """Modelo para relacionamento Many-to-Many entre Usuário e Empresa com permissões específicas."""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    permissao_leitura = models.BooleanField(default=True)
    permissao_escrita = models.BooleanField(default=False)
    permissao_exclusao = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Acesso à Empresa'
        verbose_name_plural = 'Acessos às Empresas'
        db_table = 'acesso_empresas'
        unique_together = ('usuario', 'empresa')
        indexes = [
            models.Index(fields=['usuario', 'empresa']),
        ]
    
    def __str__(self):
        return f'{self.usuario.email} - {self.empresa.nome_abreviado}'
    

# Adicione esta classe ao seu arquivo dashboard/models.py

class Funcionario(models.Model):
    """Modelo para armazenar informações de funcionários"""
    
    # Choices para campos com opções específicas
    SEXO_CHOICES = [
        (1, 'Masculino'),
        (2, 'Feminino'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        (1, 'Solteiro(a)'),
        (2, 'Casado(a)'),
        (3, 'Separado(a)'),
        (4, 'Desquitado(a)'),
        (5, 'Viuvo(a)'),
        (6, 'Outros'),
        (7, 'Divorciado(a)'),
    ]
    
    # Relacionamento com Empresa
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE,
        related_name='funcionarios'
    )
    
    # Campos do modelo
    codigo = models.BigIntegerField(primary_key=True, verbose_name='Código')
    codigo_empresa = models.BigIntegerField(verbose_name='Código Empresa')
    nome_empresa = models.CharField(max_length=200, verbose_name='Nome Empresa')
    nome = models.CharField(max_length=120, verbose_name='Nome')
    codigo_unidade = models.CharField(max_length=20, blank=True, null=True, verbose_name='Código Unidade')
    nome_unidade = models.CharField(max_length=130, blank=True, null=True, verbose_name='Nome Unidade')
    codigo_setor = models.CharField(max_length=12, blank=True, null=True, verbose_name='Código Setor')
    nome_setor = models.CharField(max_length=130, blank=True, null=True, verbose_name='Nome Setor')
    codigo_cargo = models.CharField(max_length=10, blank=True, null=True, verbose_name='Código Cargo')
    nome_cargo = models.CharField(max_length=130, blank=True, null=True, verbose_name='Nome Cargo')
    cbo_cargo = models.CharField(max_length=10, blank=True, null=True, verbose_name='CBO Cargo')
    ccusto = models.CharField(max_length=50, blank=True, null=True, verbose_name='Centro de Custo')
    nome_centro_custo = models.CharField(max_length=130, blank=True, null=True, verbose_name='Nome Centro Custo')
    matricula_funcionario = models.CharField(max_length=30, blank=True, null=True, verbose_name='Matrícula Funcionário')
    cpf = models.CharField(max_length=19, blank=True, null=True, verbose_name='CPF')
    rg = models.CharField(max_length=19, blank=True, null=True, verbose_name='RG')
    uf_rg = models.CharField(max_length=10, blank=True, null=True, verbose_name='UF RG')
    orgao_emissor_rg = models.CharField(max_length=20, blank=True, null=True, verbose_name='Órgão Emissor RG')
    situacao = models.CharField(max_length=12, blank=True, null=True, verbose_name='Situação')
    sexo = models.IntegerField(choices=SEXO_CHOICES, blank=True, null=True, verbose_name='Sexo')
    pis = models.CharField(max_length=20, blank=True, null=True, verbose_name='PIS')
    ctps = models.CharField(max_length=30, blank=True, null=True, verbose_name='CTPS')
    serie_ctps = models.CharField(max_length=25, blank=True, null=True, verbose_name='Série CTPS')
    estado_civil = models.IntegerField(choices=ESTADO_CIVIL_CHOICES, blank=True, null=True, verbose_name='Estado Civil')
    tipo_contratacao = models.IntegerField(blank=True, null=True, verbose_name='Tipo Contratação')
    data_nascimento = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    data_admissao = models.DateField(blank=True, null=True, verbose_name='Data de Admissão')
    data_demissao = models.DateField(blank=True, null=True, verbose_name='Data de Demissão')
    endereco = models.CharField(max_length=110, blank=True, null=True, verbose_name='Endereço')
    numero_endereco = models.CharField(max_length=20, blank=True, null=True, verbose_name='Número')
    bairro = models.CharField(max_length=80, blank=True, null=True, verbose_name='Bairro')
    cidade = models.CharField(max_length=50, blank=True, null=True, verbose_name='Cidade')
    uf = models.CharField(max_length=20, blank=True, null=True, verbose_name='UF')
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name='CEP')
    telefone_residencial = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone Residencial')
    telefone_celular = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone Celular')
    email = models.CharField(max_length=400, blank=True, null=True, verbose_name='Email')
    deficiente = models.BooleanField(default=False, verbose_name='Deficiente')
    deficiencia = models.CharField(max_length=861, blank=True, null=True, verbose_name='Deficiência')
    nm_mae_funcionario = models.CharField(max_length=120, blank=True, null=True, verbose_name='Nome da Mãe')
    data_ultima_alteracao = models.DateField(blank=True, null=True, verbose_name='Data Última Alteração')
    matricula_rh = models.CharField(max_length=30, blank=True, null=True, verbose_name='Matrícula RH')
    cor = models.IntegerField(blank=True, null=True, verbose_name='Cor')
    escolaridade = models.IntegerField(blank=True, null=True, verbose_name='Escolaridade')
    naturalidade = models.CharField(max_length=50, blank=True, null=True, verbose_name='Naturalidade')
    ramal = models.CharField(max_length=10, blank=True, null=True, verbose_name='Ramal')
    regime_revezamento = models.IntegerField(blank=True, null=True, verbose_name='Regime Revezamento')
    regime_trabalho = models.CharField(max_length=500, blank=True, null=True, verbose_name='Regime Trabalho')
    tel_comercial = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone Comercial')
    turno_trabalho = models.IntegerField(blank=True, null=True, verbose_name='Turno Trabalho')
    rh_unidade = models.CharField(max_length=80, blank=True, null=True, verbose_name='RH Unidade')
    rh_setor = models.CharField(max_length=80, blank=True, null=True, verbose_name='RH Setor')
    rh_cargo = models.CharField(max_length=80, blank=True, null=True, verbose_name='RH Cargo')
    rh_centro_custo_unidade = models.CharField(max_length=80, blank=True, null=True, verbose_name='RH Centro Custo Unidade')
    
    # Meta informações
    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome']
        db_table = 'funcionarios'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nome']),
            models.Index(fields=['cpf']),
            models.Index(fields=['codigo_empresa']),
            models.Index(fields=['data_admissao']),
            models.Index(fields=['situacao']),
        ]
    
    def __str__(self):
        return f"{self.nome} (Matrícula: {self.matricula_funcionario or 'N/A'})"

class Absenteismo(models.Model):
    """Modelo para armazenar informações de absenteísmo dos funcionários"""
    
    TIPO_ATESTADO_CHOICES = [
        (1, 'Atestado médico'),
        (2, 'Licença maternidade'),
        (3, 'Acidente de trabalho'),
        (4, 'Outros afastamentos'),
    ]
    
    # Relacionamentos
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE,
        related_name='absenteismos',
        verbose_name='Empresa'
    )
    funcionario = models.ForeignKey(
        Funcionario, 
        on_delete=models.CASCADE,
        related_name='absenteismos',
        verbose_name='Funcionário',
        null=True,
        blank=True,
        # Usaremos o método para buscar o funcionário baseado na matrícula
    )
    
    # Campos conforme especificação
    unidade = models.CharField(max_length=130, verbose_name='Unidade')
    setor = models.CharField(max_length=130, verbose_name='Setor')
    matricula_func = models.CharField(max_length=30, verbose_name='Matrícula Funcionário')
    dt_nascimento = models.DateField(verbose_name='Data de Nascimento', null=True, blank=True)
    sexo = models.IntegerField(choices=[(1, 'Masculino'), (2, 'Feminino')], verbose_name='Sexo', null=True, blank=True)
    tipo_atestado = models.IntegerField(choices=TIPO_ATESTADO_CHOICES, verbose_name='Tipo de Atestado', default=1)
    dt_inicio_atestado = models.DateField(verbose_name='Data Início Atestado')
    dt_fim_atestado = models.DateField(verbose_name='Data Fim Atestado')
    hora_inicio_atestado = models.CharField(max_length=5, verbose_name='Hora Início Atestado', null=True, blank=True)
    hora_fim_atestado = models.CharField(max_length=5, verbose_name='Hora Fim Atestado', null=True, blank=True)
    dias_afastados = models.IntegerField(verbose_name='Dias Afastados')
    horas_afastado = models.CharField(max_length=5, verbose_name='Horas Afastado', null=True, blank=True)
    cid_principal = models.CharField(max_length=10, verbose_name='CID Principal', null=True, blank=True)
    descricao_cid = models.CharField(max_length=264, verbose_name='Descrição CID', null=True, blank=True)
    grupo_patologico = models.CharField(max_length=80, verbose_name='Grupo Patológico', null=True, blank=True)
    tipo_licenca = models.CharField(max_length=100, verbose_name='Tipo de Licença', null=True, blank=True)
    
    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Absenteísmo'
        verbose_name_plural = 'Absenteísmos'
        ordering = ['-dt_inicio_atestado', 'matricula_func']
        db_table = 'absenteismo'
        indexes = [
            models.Index(fields=['empresa']),
            models.Index(fields=['matricula_func']),
            models.Index(fields=['dt_inicio_atestado', 'dt_fim_atestado']),
            models.Index(fields=['tipo_atestado']),
            models.Index(fields=['cid_principal']),
        ]
    
    def __str__(self):
        return f"Absenteísmo de {self.matricula_func} - {self.dt_inicio_atestado} a {self.dt_fim_atestado}"
    
    def save(self, *args, **kwargs):
        # Tentar vincular ao funcionário pela matrícula, se não estiver já definido
        if not self.funcionario_id and self.matricula_func and self.empresa_id:
            try:
                funcionario = Funcionario.objects.get(
                    empresa_id=self.empresa_id,
                    matricula_funcionario=self.matricula_func
                )
                self.funcionario = funcionario
                
                # Atualizar informações do funcionário se estiverem faltando
                if not self.unidade and funcionario.nome_unidade:
                    self.unidade = funcionario.nome_unidade
                    
                if not self.setor and funcionario.nome_setor:
                    self.setor = funcionario.nome_setor
                    
                if not self.dt_nascimento and funcionario.data_nascimento:
                    self.dt_nascimento = funcionario.data_nascimento
                    
                if not self.sexo and funcionario.sexo:
                    self.sexo = funcionario.sexo
                
            except Funcionario.DoesNotExist:
                # Não encontrou o funcionário, mas ainda podemos salvar o absenteísmo
                pass
        
        # Calcular dias afastados se não fornecido
        if not self.dias_afastados and self.dt_inicio_atestado and self.dt_fim_atestado:
            delta = self.dt_fim_atestado - self.dt_inicio_atestado
            self.dias_afastados = delta.days + 1  # +1 porque o dia final também conta
        
        super().save(*args, **kwargs)
    
    @property
    def duracao_formatada(self):
        """Retorna a duração do afastamento em formato legível"""
        if self.dias_afastados == 1:
            return "1 dia"
        elif self.dias_afastados:
            return f"{self.dias_afastados} dias"
        elif self.horas_afastado:
            return f"{self.horas_afastado} horas"
        return "Indefinido"
    
    @property
    def nome_funcionario(self):
        """Retorna o nome do funcionário, se disponível"""
        if self.funcionario:
            return self.funcionario.nome
        return "Não identificado"
    
class Convocacao(models.Model):
    """
    Model for tracking employee health exam summons and appointments.
    Stores information about required exams, their schedule and results.
    """
    
    # Relationship to company and employee
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='convocacoes')
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='convocacoes')
 
    # Company and unit information
    codigo_empresa = models.BigIntegerField(verbose_name='Código Empresa')
    nome_abreviado = models.CharField(max_length=60, verbose_name='Nome Abreviado')
    unidade = models.CharField(max_length=130, verbose_name='Unidade')
    cidade = models.CharField(max_length=50, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado')
    bairro = models.CharField(max_length=80, verbose_name='Bairro')
    endereco = models.CharField(max_length=110, verbose_name='Endereço')
    cep = models.CharField(max_length=10, verbose_name='CEP')
    cnpj_unidade = models.CharField(max_length=20, verbose_name='CNPJ Unidade')
    
    # Employee professional information
    setor = models.CharField(max_length=130, verbose_name='Setor')
    cargo = models.CharField(max_length=130, verbose_name='Cargo')
    codigo_funcionario = models.BigIntegerField(verbose_name='Código Funcionário')
    cpf_funcionario = models.CharField(max_length=14, verbose_name='CPF Funcionário')
    matricula = models.CharField(max_length=30, verbose_name='Matrícula')
    data_admissao = models.DateField(verbose_name='Data de Admissão')
    nome = models.CharField(max_length=120, verbose_name='Nome do Funcionário')
    email_funcionario = models.CharField(max_length=400, verbose_name='Email do Funcionário', null=True, blank=True)
    telefone_funcionario = models.CharField(max_length=20, verbose_name='Telefone do Funcionário', null=True, blank=True)
    
    # Exam information
    codigo_exame = models.CharField(max_length=20, verbose_name='Código do Exame')
    exame = models.CharField(max_length=200, verbose_name='Exame')
    ultimo_pedido = models.DateField(verbose_name='Data do Último Pedido', null=True, blank=True)
    data_resultado = models.DateField(verbose_name='Data do Resultado', null=True, blank=True)
    periodicidade = models.IntegerField(verbose_name='Periodicidade (meses)')
    refazer = models.DateField(verbose_name='Data para Refazer', null=True, blank=True)
    
    # Status fields
    status = models.CharField(max_length=20, default='PENDENTE', verbose_name='Status')
    data_convocacao = models.DateField(verbose_name='Data da Convocação', auto_now_add=True)
    data_agendamento = models.DateField(verbose_name='Data de Agendamento', null=True, blank=True)
    hora_agendamento = models.TimeField(verbose_name='Hora de Agendamento', null=True, blank=True)
    
    # Tracking and auditing fields
    observacoes = models.TextField(verbose_name='Observações', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Convocação de Exame'
        verbose_name_plural = 'Convocações de Exames'
        ordering = ['-data_convocacao', 'nome']
        db_table = 'convocacoes'
        indexes = [
            models.Index(fields=['empresa']),
            models.Index(fields=['funcionario']),
            models.Index(fields=['codigo_funcionario']),
            models.Index(fields=['codigo_exame']),
            models.Index(fields=['data_convocacao']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.nome} - {self.exame} ({self.status})"
    
    def save(self, *args, **kwargs):
        # First, ensure we have a funcionario_id
        if not self.funcionario_id and self.codigo_funcionario and self.cpf_funcionario:
            # Try to find funcionario by codigo
            try:
                funcionario = Funcionario.objects.filter(
                    codigo=self.codigo_funcionario
                ).first()
                
                if not funcionario and self.cpf_funcionario:
                    # Try to find by CPF if codigo didn't work
                    funcionario = Funcionario.objects.filter(
                        cpf=self.cpf_funcionario
                    ).first()
                
                if funcionario:
                    self.funcionario = funcionario
                else:
                    # Create a basic funcionario record if none exists
                    from django.db import transaction
                    with transaction.atomic():
                        funcionario = Funcionario(
                            codigo=self.codigo_funcionario,
                            codigo_empresa=self.codigo_empresa,
                            nome_empresa=self.nome_abreviado,
                            empresa_id=self.empresa_id,
                            nome=self.nome,
                            cpf=self.cpf_funcionario,
                            matricula_funcionario=self.matricula,
                            data_admissao=self.data_admissao,
                            nome_unidade=self.unidade,
                            nome_setor=self.setor,
                            nome_cargo=self.cargo,
                            email=self.email_funcionario,
                            telefone_celular=self.telefone_funcionario
                        )
                        funcionario.save()
                        self.funcionario = funcionario
            except Exception as e:
                import logging
                logging.error(f"Erro ao buscar/criar funcionário: {e}")
                # Don't raise the exception, let the caller handle it
        
        # Pre-populate company and employee information if only IDs are provided
        if self.empresa_id and not self.codigo_empresa:
            self.codigo_empresa = self.empresa.codigo
            self.nome_abreviado = self.empresa.nome_abreviado
            
        if self.funcionario_id and not self.codigo_funcionario:
            # Copy data from the related Funcionario
            funcionario = self.funcionario
            self.codigo_funcionario = funcionario.codigo
            self.cpf_funcionario = funcionario.cpf or ''
            self.matricula = funcionario.matricula_funcionario or ''
            self.data_admissao = funcionario.data_admissao
            self.nome = funcionario.nome
            self.email_funcionario = funcionario.email
            self.telefone_funcionario = funcionario.telefone_celular or funcionario.telefone_residencial
            self.setor = funcionario.nome_setor or ''
            self.cargo = funcionario.nome_cargo or ''
        
        super().save(*args, **kwargs)
    
    @property
    def dias_restantes(self):
        """Returns the number of days until the exam needs to be redone"""
        if not self.data_resultado:
            return 0
        
        import datetime
        from django.utils import timezone
        
        # Calculate next exam date based on periodicidade (in months)
        next_exam_date = self.data_resultado.replace(
            year=self.data_resultado.year + (self.periodicidade // 12),
            month=self.data_resultado.month + (self.periodicidade % 12)
        )
        
        # Adjust if month overflows
        while next_exam_date.month > 12:
            next_exam_date = next_exam_date.replace(
                year=next_exam_date.year + 1,
                month=next_exam_date.month - 12
            )
        
        # Calculate days remaining
        today = timezone.now().date()
        delta = next_exam_date - today
        
        return delta.days
    
    @property
    def situacao(self):
        """Returns the situation of the exam (em dia, próximo do vencimento, vencido)"""
        dias = self.dias_restantes
        
        if dias < 0:
            return "VENCIDO"
        elif dias <= 30:
            return "PRÓXIMO DO VENCIMENTO"
        else:
            return "EM DIA"