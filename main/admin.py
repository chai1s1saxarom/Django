from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from decimal import Decimal
from .models import Project, Lecture, Feedback, Subscriber, Manufacturer, Product, Category, ProductImage, ProductReview, Discount


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_processed',)
    readonly_fields = ('created_at',)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    """
    Настройка админки для подписчиков
    """
    list_display = ('email', 'date_subscribed', 'is_active', 'days_subscribed')
    list_filter = ('is_active', 'date_subscribed')
    search_fields = ('email',)
    readonly_fields = ('date_subscribed',)
    list_editable = ('is_active',)
    
    def days_subscribed(self, obj):
        """
        Количество дней с момента подписки
        """
        from django.utils import timezone
        if obj.date_subscribed:
            delta = timezone.now() - obj.date_subscribed
            return delta.days
        return 0
    days_subscribed.short_description = 'Дней с подписки'
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """
        Массовая активация подписок
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} подписок активировано')
    activate_subscriptions.short_description = "Активировать выбранные подписки"
    
    def deactivate_subscriptions(self, request, queryset):
        """
        Массовая деактивация подписок
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} подписок деактивировано')
    deactivate_subscriptions.short_description = "Деактивировать выбранные подписки"

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'founded_year', 'is_active', 'product_count')
    list_filter = ('country', 'is_active')
    search_fields = ('name', 'country')
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Количество товаров'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name', 'description')
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Количество товаров'

# Inline-редактирование для изображений товаров
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'caption', 'is_main', 'uploaded_at')
    readonly_fields = ('uploaded_at', 'preview')
    
    def preview(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "Нет изображения"
    preview.short_description = 'Превью'
    model = ProductImage
    extra = 1
    fields = ('image', 'caption', 'is_main', 'uploaded_at')
    readonly_fields = ('uploaded_at', 'preview')
    
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "Нет изображения"
    preview.short_description = 'Превью'

# Inline-редактирование для отзывов о товарах
class ProductReviewInline(admin.StackedInline):
    model = ProductReview
    extra = 0
    fields = ('author', 'email', 'rating', 'comment', 'is_published', 'created_at')
    readonly_fields = ('created_at',)

class DiscountInline(admin.TabularInline):
    model = Discount
    extra = 1
    fields = ('discount_percent', 'start_date', 'end_date', 'is_active', 'is_valid_display')
    readonly_fields = ('is_valid_display',)
    
    def is_valid_display(self, obj):
        """
        Отображает статус скидки
        """
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Активна</span>')
        else:
            return format_html('<span style="color: red;">✗ Неактивна</span>')
    is_valid_display.short_description = 'Статус'
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'manufacturer', 
        'category',
        'formatted_price',
        'discount_display',
        'discounted_price_display',
        'stock_quantity', 
        'is_available',
        'image_count',
        'review_count',
        'average_rating_display'
    )
    
    list_filter = ('manufacturer', 'category', 'is_available', 'created_at', 'discounts__is_active')
    
    search_fields = ('name', 'description', 'manufacturer__name')
    list_editable = ('stock_quantity', 'is_available')
    readonly_fields = ('created_at', 'image_preview', 'current_discount_info')
    list_per_page = 20
    
    # Добавляем inline-формы
    inlines = [ProductImageInline, ProductReviewInline, DiscountInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'manufacturer', 'category')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Скидки', {
            'fields': ('current_discount_info',),
            'classes': ('collapse',)
        }),
        ('Дополнительная информация', {
            'fields': ('warranty_months', 'created_at')
        }),
    )
    
    # Кастомные методы для отображения в списке
    def formatted_price(self, obj):
        price_value = float(obj.price)
        price_str = f"{price_value:.2f}"
        
        if obj.has_active_discount:
            return format_html(
                '<s style="color: gray;">{} ₽</s>',
                price_str
            )
        return f"{price_str} ₽"
    formatted_price.short_description = 'Цена'
    formatted_price.admin_order_field = 'price'
    
    def discount_display(self, obj):
        """
        Отображает скидку в списке товаров
        """
        if obj.has_active_discount:
            return format_html(
                '<span style="color: green; font-weight: bold;">-{}%</span>',
                obj.get_discount_percent()
            )
        return "-"
    discount_display.short_description = 'Скидка'
    
    def discounted_price_display(self, obj):
        """
        Отображает цену со скидкой в списке товаров
        """
        if obj.has_active_discount:
            discounted_price_value = float(obj.discounted_price)
            price_str = f"{discounted_price_value:.2f}"
            
            return format_html(
                '<span style="color: red; font-weight: bold;">{} ₽</span>',
                price_str
            )
        return "-"
    discounted_price_display.short_description = 'Цена со скидкой'
    
    # Новый метод для отображения информации о скидке в форме редактирования
    def current_discount_info(self, obj):
        """
        Отображает информацию о текущей скидке в форме редактирования
        """
        if obj.has_active_discount:
            discount = obj.current_discount
            end_date = discount.end_date.strftime('%d.%m.%Y') if discount.end_date else "бессрочно"
            
            # Форматируем все числа в строки перед передачей в format_html
            discount_percent_str = str(discount.discount_percent)
            old_price_str = f"{float(obj.price):.2f}"
            new_price_str = f"{float(obj.discounted_price):.2f}"
            savings_str = f"{float(obj.price - obj.discounted_price):.2f}"
            
            return format_html(
                '''
                <div style="padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                    <h3 style="margin-top: 0;">Текущая скидка</h3>
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 24px; color: green; margin-right: 15px;">
                            <strong>-{}%</strong>
                        </div>
                        <div>
                            <div><strong>Старая цена:</strong> <s>{} ₽</s></div>
                            <div><strong>Новая цена:</strong> <span style="color: red; font-size: 18px;"><strong>{} ₽</strong></span></div>
                        </div>
                    </div>
                    <div style="font-size: 12px; color: #666;">
                        <div><strong>Начало:</strong> {}</div>
                        <div><strong>Окончание:</strong> {}</div>
                        <div><strong>Экономия:</strong> {} ₽</div>
                    </div>
                </div>
                ''',
                discount_percent_str,
                old_price_str,
                new_price_str,
                discount.start_date.strftime('%d.%m.%Y %H:%M'),
                end_date,
                savings_str
            )
        
        # Нет активных скидок
        price_str = f"{float(obj.price):.2f}"
        return format_html(
            '''
            <div style="padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; text-align: center;">
                <p style="color: #666; margin: 0;">Нет активных скидок</p>
                <p style="font-size: 12px; color: #999; margin: 5px 0 0 0;">Текущая цена: <strong>{} ₽</strong></p>
            </div>
            ''',
            price_str
        )
    current_discount_info.short_description = 'Информация о скидках'
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Изображений'
    
    def review_count(self, obj):
        return obj.reviews.filter(is_published=True).count()
    review_count.short_description = 'Отзывов'
    
    def average_rating_display(self, obj):
        reviews = obj.reviews.filter(is_published=True)
        if reviews.exists():
            average = sum(review.rating for review in reviews) / reviews.count()
            stars = '★' * round(average)
            return f"{stars} ({average:.1f})"
        return "Нет оценок"
    average_rating_display.short_description = 'Рейтинг'
    
    # Метод для превью изображения в форме редактирования
    def image_preview(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image and main_image.image.url:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                main_image.image.url
            )
        return "Нет главного изображения"
    image_preview.short_description = 'Главное изображение'
    
    # Массовые операции
    actions = [
        'make_available', 
        'make_unavailable', 
        'increase_price_10_percent',
        'decrease_price_10_percent',
        'add_15_percent_discount',
        'remove_all_discounts'
    ]
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} товаров стало доступно')
    make_available.short_description = "Сделать доступными"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} товаров стало недоступно')
    make_unavailable.short_description = "Сделать недоступными"
    
    def increase_price_10_percent(self, request, queryset):
        count = 0
        for product in queryset:
            product.price *= Decimal('1.1')
            product.save()
            count += 1
        self.message_user(request, f'Цены увеличены на 10 процентов для {count} товаров')
    increase_price_10_percent.short_description = "Увеличить цену на 10 процентов"
    
    def decrease_price_10_percent(self, request, queryset):
        count = 0
        for product in queryset:
            product.price *= Decimal('0.9')
            product.save()
            count += 1
        self.message_user(request, f'Цены уменьшены на 10 процентов для {count} товаров')
    decrease_price_10_percent.short_description = "Уменьшить цену на 10 процентов"
    
    # НОВАЯ массовая операция: Добавить скидку 15%
    def add_15_percent_discount(self, request, queryset):
        count = 0
        for product in queryset:
            # Проверяем, нет ли уже активной скидки
            if not product.has_active_discount:
                Discount.objects.create(
                    product=product,
                    discount_percent=15,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=30),
                    is_active=True
                )
                count += 1
            else:
                # Если скидка уже есть, обновляем существующую
                discount = product.current_discount
                discount.discount_percent = 15
                discount.start_date = timezone.now()
                discount.end_date = timezone.now() + timezone.timedelta(days=30)
                discount.save()
                count += 1
        
        self.message_user(
            request, 
            f'Скидка 15%% добавлена на {count} товаров на срок 30 дней'
        )
    add_15_percent_discount.short_description = "Добавить скидку 15%% на 30 дней"
    
    # НОВАЯ массовая операция: Удалить все скидки
    def remove_all_discounts(self, request, queryset):
        total_deleted = 0
        for product in queryset:
            deleted_count, _ = product.discounts.all().delete()
            total_deleted += deleted_count
        
        self.message_user(
            request, 
            f'Удалено {total_deleted} скидок с выбранных товаров'
        )
    remove_all_discounts.short_description = "Удалить все скидки"
    
    # Настройка формы создания/редактирования
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['manufacturer'].queryset = Manufacturer.objects.filter(is_active=True)
        return form

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """
    Админка для управления скидками
    """
    list_display = (
        'product',
        'discount_percent_display',
        'start_date',
        'end_date',
        'is_active',
        'is_valid_display',
        'created_at'
    )
    
    list_filter = (
        'is_active',
        'start_date',
        'end_date',
        'product__manufacturer',
        'product__category'
    )
    
    search_fields = (
        'product__name',
        'product__manufacturer__name'
    )
    
    list_editable = ('is_active',)
    
    readonly_fields = ('created_at', 'is_valid_display')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('product', 'discount_percent')
        }),
        ('Срок действия', {
            'fields': ('start_date', 'end_date')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_valid_display', 'created_at')
        }),
    )
    
    actions = ['activate_discounts', 'deactivate_discounts']
    
    def discount_percent_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: green;">-{}%</span>',
            obj.discount_percent
        )
    discount_percent_display.short_description = 'Скидка'
    
    def is_valid_display(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Действует</span>')
        else:
            return format_html('<span style="color: red;">✗ Не действует</span>')
    is_valid_display.short_description = 'Статус действия'
    
    def activate_discounts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} скидок активировано')
    activate_discounts.short_description = "Активировать скидки"
    
    def deactivate_discounts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} скидок деактивировано')
    deactivate_discounts.short_description = "Деактивировать скидки"
