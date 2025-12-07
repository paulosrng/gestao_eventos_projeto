# gestao_app/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Usuario, Evento
import re # Para validação de senha
from datetime import date # <--- ESSA LINHA QUE ESTAVA FALTANDO

class UserCreationForm(forms.ModelForm):
    """Formulário personalizado para criação de usuários."""
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        help_text="Mínimo 8 caracteres, letras, números e caracteres especiais."
    )
    password2 = forms.CharField(
        label="Confirmação da senha",
        widget=forms.PasswordInput,
        help_text="Digite a mesma senha novamente para confirmação."
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefone', 'instituicao_ensino', 'perfil')
        widgets = {
            'telefone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm phone-mask', 
                'placeholder': '(00) 00000-0000'
            }),
        }

    # REGRA 5: Validação de Senha Forte
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError("A senha deve ter no mínimo 8 caracteres.")
            if not re.search(r'[a-zA-Z]', password):
                raise ValidationError("A senha deve conter letras.")
            if not re.search(r'\d', password):
                raise ValidationError("A senha deve conter números.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("A senha deve conter caracteres especiais.")
        return password

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("As senhas não correspondem.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    pass

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        exclude = ['organizador_responsavel']
        widgets = {
            # Agora vai funcionar porque importamos 'date' lá em cima
            'data_inicio': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm',
                'min': date.today().isoformat() 
            }),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm'}),
            'horario': forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm'}),
        }

    def clean_banner(self):
        imagem = self.cleaned_data.get('banner')
        if imagem:
            if not imagem.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise ValidationError("A imagem deve ser JPG ou PNG.")
            if imagem.size > 5 * 1024 * 1024:
                raise ValidationError("O tamanho da imagem não pode exceder 5MB.")
        return imagem