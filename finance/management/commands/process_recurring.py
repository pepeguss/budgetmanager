from django.core.management.base import BaseCommand
from finance.services import process_recurring
class Command(BaseCommand):
    help = 'Create due recurring income transactions.'
    def handle(self, *args, **options): self.stdout.write(f'Создано операций: {process_recurring()}')
