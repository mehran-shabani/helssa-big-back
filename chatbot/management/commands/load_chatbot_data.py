"""
دستور مدیریت برای بارگذاری داده‌های اولیه چت‌بات
Management command to load initial chatbot data
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from chatbot.models import ChatbotResponse


class Command(BaseCommand):
    """
    دستور بارگذاری داده‌های اولیه چت‌بات
    """
    help = 'بارگذاری داده‌های اولیه چت‌بات شامل پاسخ‌های از پیش تعریف شده'
    
    def add_arguments(self, parser):
        """
        اضافه کردن آرگومان‌های دستور
        """
        parser.add_argument(
            '--reset',
            action='store_true',
            help='حذف داده‌های موجود قبل از بارگذاری',
        )
        
        parser.add_argument(
            '--fixture',
            type=str,
            default='initial_responses.json',
            help='نام فایل fixture برای بارگذاری',
        )
    
    def handle(self, *args, **options):
        """
        اجرای دستور
        """
        self.stdout.write(
            self.style.SUCCESS('شروع بارگذاری داده‌های اولیه چت‌بات...')
        )
        
        # حذف داده‌های موجود در صورت درخواست
        if options['reset']:
            self.stdout.write('حذف پاسخ‌های موجود...')
            ChatbotResponse.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('✓ پاسخ‌های موجود حذف شدند')
            )
        
        # بارگذاری fixture
        try:
            fixture_path = f'chatbot/fixtures/{options["fixture"]}'
            call_command('loaddata', fixture_path)
            
            # آمارگیری
            total_responses = ChatbotResponse.objects.count()
            active_responses = ChatbotResponse.objects.filter(is_active=True).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ داده‌های اولیه با موفقیت بارگذاری شد\n'
                    f'  - تعداد کل پاسخ‌ها: {total_responses}\n'
                    f'  - پاسخ‌های فعال: {active_responses}'
                )
            )
            
            # نمایش آمار بر اساس دسته‌بندی
            self._show_category_stats()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطا در بارگذاری داده‌ها: {str(e)}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 فرآیند بارگذاری با موفقیت تکمیل شد!')
        )
    
    def _show_category_stats(self):
        """
        نمایش آمار بر اساس دسته‌بندی
        """
        self.stdout.write('\nآمار بر اساس دسته‌بندی:')
        
        categories = ChatbotResponse.objects.values_list('category', flat=True).distinct()
        
        for category in categories:
            count = ChatbotResponse.objects.filter(
                category=category, 
                is_active=True
            ).count()
            
            category_display = {
                'greeting': 'خوشامدگویی',
                'symptom_inquiry': 'پرسش علائم',
                'medication_info': 'اطلاعات دارو',
                'appointment': 'نوبت‌گیری',
                'emergency': 'اورژانس',
                'general_health': 'سلامت عمومی',
                'farewell': 'خداحافظی',
                'error': 'خطا',
                'unknown': 'نامشخص'
            }.get(category, category)
            
            self.stdout.write(f'  - {category_display}: {count} پاسخ')