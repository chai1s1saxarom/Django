from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from main.models import Subscriber

class Command(BaseCommand):
    help = 'Send newsletter to all active subscribers'

    def handle(self, *args, **options):
        active_subscribers = Subscriber.objects.filter(is_active=True)
        emails = [subscriber.email for subscriber in active_subscribers]
        
        if emails:
            subject = 'Новости нашего сайта'
            message = 'Здравствуйте! Вот последние новости нашего сайта...'
            from_email = 'noreply@example.com'
            
            datatuple = [
                (subject, message, from_email, [email])
                for email in emails
            ]
            
            send_mass_mail(datatuple)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent newsletter to {len(emails)} subscribers')
            )
        else:
            self.stdout.write('No active subscribers found')