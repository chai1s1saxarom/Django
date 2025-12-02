from django import forms
from .models import Feedback

class ContactForm(forms.Form):
    name = forms.CharField(
        label='Ваше имя',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите ваше сообщение', 'rows': 5})
    )

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'subject', 'message']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите ваш email'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема сообщения'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше сообщение...',
                'rows': 5
            }),
        }
        
        labels = {
            'name': 'Ваше имя',
            'email': 'Email адрес',
            'subject': 'Тема сообщения', 
            'message': 'Сообщение'
        }

from .models import Subscriber

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш email',
                'style': 'width: 250px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
            })
        }
        labels = {
            'email': ''
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Subscriber.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError("Вы уже подписаны на рассылку.")
        return email

class UnsubscribeForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email для отписки',
            'style': 'width: 300px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
        }),
        label=''
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Subscriber.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError("Этот email не найден в списке подписчиков.")
        return email