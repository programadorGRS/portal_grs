# dashboard/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu email',
                'autocomplete': 'email',
                'required': True,
            }
        )
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Digite sua senha',
                'autocomplete': 'current-password',
                'required': True,
            }
        )
    )
    
    # Campo para armazenar o token JWT quando for gerado
    token = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def confirm_login_allowed(self, user):
        # Verificar se o usuário está ativo
        if not user.is_active:
            raise forms.ValidationError(
                'Esta conta está inativa.',
                code='inactive',
            )
        # Aqui pode verificar outras condições como acesso a telas específicas, etc.
        return super().confirm_login_allowed(user)