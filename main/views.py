from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import SubscribeForm, UnsubscribeForm, FeedbackForm,ContactForm
from .models import Subscriber, Product, Manufacturer, Category, Feedback, Project, Lecture


def home(request):
    context = {'title': 'Главная страница'}
    return render(request, 'main/home.html', context)

def about(request):
    context = {'title': 'Обо мне'}
    return render(request, 'main/about.html', context)

def portfolio(request):
    projects = Project.objects.all().order_by('-created_at')
    context = {
        'title': 'Портфолио', 
        'projects': projects
    }
    return render(request, 'main/portfolio.html', context)

def lectures(request):  
    lectures_list = Lecture.objects.all()
    context = {
        'title': 'Лекции', 
        'lectures': lectures_list
    }
    return render(request, 'main/lectures.html', context)

def contacts(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Ваше сообщение успешно отправлено! Мы ответим вам в ближайшее время.')
                return redirect('contacts')
            except Exception as e:
                messages.error(request, f'Произошла ошибка при отправке: {str(e)}')
        else:
            #отладочная информация
            messages.error(request, f'Форма не валидна. Ошибки: {form.errors}')
    else:
        form = FeedbackForm()
    
    context = {
        'title': 'Контакты',
        'form': form
    }
    return render(request, 'main/contacts.html', context)

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    context = {
        'title': project.title,
        'project': project
    }
    return render(request, 'main/project_detail.html', context)

def lecture_detail(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    context = {
        'title': lecture.title,
        'lecture': lecture
    }
    return render(request, 'main/lecture_detail.html', context)


def feedback_list(request):
    if not request.user.is_staff:
        return redirect('home')
    
    feedbacks = Feedback.objects.all()
    context = {
        'title': 'Сообщения обратной связи',
        'feedbacks': feedbacks
    }
    return render(request, 'main/feedback_list.html', context)



def subscribe(request):
    """
    Страница подписки на новости
    """
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            # Проверяем, есть ли уже неактивная подписка с этим email
            email = form.cleaned_data['email']
            existing_subscriber = Subscriber.objects.filter(email=email).first()
            
            if existing_subscriber:
                # Активируем существующую подписку
                existing_subscriber.is_active = True
                existing_subscriber.save()
            else:
                # Создаем новую подписку
                form.save()
            
            return redirect('subscribe_success')
    else:
        form = SubscribeForm()
    
    context = {
        'title': 'Подписка на новости',
        'form': form
    }
    return render(request, 'main/subscribe.html', context)

def subscribe_success(request):
    """
    Страница успешной подписки
    """
    context = {
        'title': 'Подписка оформлена'
    }
    return render(request, 'main/subscribe_success.html', context)

def unsubscribe(request):
    """
    Страница отписки от рассылки
    """
    if request.method == 'POST':
        form = UnsubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                subscriber = Subscriber.objects.get(email=email, is_active=True)
                subscriber.is_active = False
                subscriber.save()
                messages.success(request, 'Вы успешно отписались от рассылки.')
                return redirect('unsubscribe')
            except Subscriber.DoesNotExist:
                messages.error(request, 'Подписка с таким email не найдена.')
    else:
        form = UnsubscribeForm()
    
    context = {
        'title': 'Отписка от рассылки',
        'form': form
    }
    return render(request, 'main/unsubscribe.html', context)

def quick_subscribe(request):
    """
    Быстрая подписка из футера (обработка AJAX или обычного POST)
    """
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            existing_subscriber = Subscriber.objects.filter(email=email).first()
            
            if existing_subscriber:
                existing_subscriber.is_active = True
                existing_subscriber.save()
            else:
                form.save()
            
            messages.success(request, 'Вы успешно подписались на рассылку!')
        else:
            # Передаем ошибки в messages
            for error in form.errors['email']:
                messages.error(request, error)
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

