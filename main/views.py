from django.shortcuts import render, get_object_or_404
from .models import Product, Manufacturer

def home(request):
    """
    Домашняя страница - список всех производителей
    """
    manufacturers = Manufacturer.objects.all()
    return render(request, 'main/home.html', {
        'manufacturers': manufacturers
    })

def product_list(request):
    """
    Список всех товаров
    """
    products = Product.objects.select_related('manufacturer').all()
    return render(request, 'main/product_list.html', {
        'products': products
    })

def product_detail(request, product_id):
    """
    Детальная страница товара
    """
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'main/product_detail.html', {
        'product': product
    })

def manufacturer_products(request, manufacturer_id):
    """
    Товары конкретного производителя
    """
    manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)
    products = Product.objects.filter(manufacturer=manufacturer)
    return render(request, 'main/manufacturer_products.html', {
        'manufacturer': manufacturer,
        'products': products
    })

def search_products(request):
    """
    Поиск товаров по названию 
    """
    # Получаем поисковый запрос из GET-параметра
    query = request.GET.get('q', '')
    
    # Ищем товары, если есть поисковый запрос
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = []
    
    # Передаем результаты в шаблон
    return render(request, 'main/search_results.html', {
        'products': products,
        'query': query
    })
from django.views.generic import ListView, DetailView, TemplateView

# Классы для CBV (добавьте после существующих функций)
class HomeView(TemplateView):
    """Главная страница на основе класса"""
    template_name = 'main/home_cbv.html'
    
    def get_context_data(self, **kwargs):
        # Получаем контекст от родительского класса
        context = super().get_context_data(**kwargs)
        # Добавляем производителей в контекст шаблона
        context['manufacturers'] = Manufacturer.objects.all()
        return context


class ProductListView(ListView):
    """Список товаров на основе класса"""
    model = Product  # Указываем, с какой моделью работаем
    template_name = 'main/product_list_cbv.html'
    context_object_name = 'products'  # Как называть список в шаблоне
    
    def get_queryset(self):
        # Оптимизируем запрос к базе данных
        return Product.objects.select_related('manufacturer').all()


class ProductDetailView(DetailView):
    """Детальная страница товара на основе класса"""
    model = Product
    template_name = 'main/product_detail_cbv.html'
    context_object_name = 'product'
    # Автоматически ищет товар по ID (pk = primary key)


class ManufacturerProductsView(ListView):
    """Товары производителя на основе класса"""
    template_name = 'main/manufacturer_products_cbv.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # Получаем ID производителя из URL
        manufacturer_id = self.kwargs['manufacturer_id']
        # Фильтруем товары по производителю
        return Product.objects.filter(manufacturer_id=manufacturer_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о производителе
        manufacturer_id = self.kwargs['manufacturer_id']
        context['manufacturer'] = get_object_or_404(Manufacturer, id=manufacturer_id)
        return context
