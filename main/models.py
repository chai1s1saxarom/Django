from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q 
from decimal import Decimal 

class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название проекта')
    description = models.TextField(verbose_name='Описание проекта')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

class Lecture(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название лекции')
    description = models.TextField(verbose_name='Краткое описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Лекция'
        verbose_name_plural = 'Лекции'
        ordering = ['-created_at']

class Feedback(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=200, verbose_name='Тема сообщения')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    is_processed = models.BooleanField(default=False, verbose_name='Обработано')
    
    def __str__(self):
        return f"{self.subject} от {self.name}"
    
    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратные связи'
        ordering = ['-created_at']

class Subscriber(models.Model):
    email = models.EmailField(
        unique=True, 
        verbose_name='Email адрес',
        error_messages={
            'unique': 'Этот email уже подписан на рассылку.'
        }
    )
    date_subscribed = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата подписки'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Активна'
    )
    
    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ['-date_subscribed']
    
    def __str__(self):
        return f"{self.email} ({'активна' if self.is_active else 'неактивна'})"

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название производителя')
    country = models.CharField(max_length=50, verbose_name='Страна')
    website = models.URLField(blank=True, verbose_name='Веб-сайт')
    founded_year = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='Год основания'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание')
    
    # Связь с производителем
    manufacturer = models.ForeignKey(
        Manufacturer, 
        on_delete=models.PROTECT, 
        verbose_name='Производитель'
    )
    
    # Связь с категорией (только одно поле!)
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        verbose_name='Категория',
        null=True,  # Разрешаем пустые значения в БД
        blank=True  # Разрешаем пустые значения в формах
    )
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Цена'
    )
    stock_quantity = models.PositiveIntegerField(
        default=0, 
        verbose_name='Количество на складе'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата создания'
    )
    is_available = models.BooleanField(
        default=True, 
        verbose_name='Доступен для продажи'
    )
    warranty_months = models.PositiveSmallIntegerField(
        default=12, 
        verbose_name='Гарантия (мес.)'
    )
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.manufacturer.name})"
        
    @property
    def current_discount(self):
        """
        Возвращает текущую активную скидку на товар
        """
        now = timezone.now()
        discounts = self.discounts.filter(
            is_active=True,
            start_date__lte=now
        )
        
        #Q объекты для сложного запроса
        discounts = discounts.filter(
            Q(end_date__gte=now) | Q(end_date__isnull=True)
        )
        
        return discounts.first()
    
    @property
    def discounted_price(self):
        """
        Возвращает цену со скидкой
        """
        if self.current_discount:
            return self.current_discount.calculate_discounted_price(self.price)
        return self.price
    
    @property
    def has_active_discount(self):
        """
        Проверяет, есть ли у товара активная скидка
        """
        return self.current_discount is not None
    
    def get_discount_percent(self):
        """
        Возвращает процент текущей скидки
        """
        if self.current_discount:
            return self.current_discount.discount_percent
        return 0

class ProductImage(models.Model):
    """
    Модель для хранения изображений товаров
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Товар'
    )
    
    image = models.ImageField(
        upload_to='products/images/%Y/%m/%d/', 
        verbose_name='Изображение'
    )
    
    caption = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Подпись'
    )
    
    is_main = models.BooleanField(
        default=False, 
        verbose_name='Главное изображение'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата загрузки'
    )
    
    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['-is_main', 'uploaded_at']
    
    def __str__(self):
        return f"Изображение для {self.product.name}"

class ProductReview(models.Model):
    """
    Модель для хранения отзывов о товарах
    """
    RATING_CHOICES = [
        (1, '★☆☆☆☆ (1)'),
        (2, '★★☆☆☆ (2)'),
        (3, '★★★☆☆ (3)'),
        (4, '★★★★☆ (4)'),
        (5, '★★★★★ (5)'),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name='Товар'
    )
    
    author = models.CharField(
        max_length=100, 
        verbose_name='Автор'
    )
    
    email = models.EmailField(
        blank=True, 
        verbose_name='Email автора'
    )
    
    rating = models.IntegerField(
        choices=RATING_CHOICES, 
        default=5, 
        verbose_name='Рейтинг'
    )
    
    comment = models.TextField(
        verbose_name='Комментарий'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата создания'
    )
    
    is_published = models.BooleanField(
        default=True, 
        verbose_name='Опубликован'
    )
    
    class Meta:
        verbose_name = 'Отзыв о товаре'
        verbose_name_plural = 'Отзывы о товарах'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Отзыв от {self.author} ({self.rating}/5)"
    
class Discount(models.Model):
    """
    Модель для хранения скидок на товары
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='discounts',
        verbose_name='Товар'
    )
    
    discount_percent = models.PositiveIntegerField(
        verbose_name='Процент скидки',
        help_text='Процент скидки от 1 до 100'
    )
    
    start_date = models.DateTimeField(
        verbose_name='Дата начала действия',
        default=timezone.now  # Используем timezone.now без вызова ()
    )
    
    end_date = models.DateTimeField(
        verbose_name='Дата окончания действия',
        null=True,
        blank=True,
        help_text='Если не указана, скидка бессрочная'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.end_date:
            end_date_str = self.end_date.strftime('%d.%m.%Y')
        else:
            end_date_str = 'бессрочно'
        return f"Скидка {self.discount_percent}% на {self.product.name} (до {end_date_str})"
    
    def clean(self):
        """
        Валидация данных модели
        """
        # Проверяем, что процент скидки в диапазоне 1-100
        if self.discount_percent < 1 or self.discount_percent > 100:
            raise ValidationError({
                'discount_percent': 'Процент скидки должен быть в диапазоне от 1 до 100'
            })
        
        # Проверяем, что дата окончания позже даты начала
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError({
                'end_date': 'Дата окончания должна быть позже даты начала'
            })
    
    @property
    def is_valid(self):
        """
        Проверяем, действует ли скидка в текущий момент
        """
        now = timezone.now()
        
        # Проверяем активность
        if not self.is_active:
            return False
        
        # Проверяем дату начала
        if now < self.start_date:
            return False
        
        # Проверяем дату окончания (если указана)
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def calculate_discounted_price(self, original_price):
        """
        Рассчитывает цену со скидкой
        """
        if not self.is_valid:
            return original_price
        
        discount_amount = original_price * (Decimal(self.discount_percent) / Decimal(100))
        return original_price - discount_amount