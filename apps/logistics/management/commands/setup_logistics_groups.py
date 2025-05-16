from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates default user groups for logistics system'

    def handle(self, *args, **kwargs):
        # Create Viewer group
        viewer_group, viewer_created = Group.objects.get_or_create(name='Viewer')
        if viewer_created:
            self.stdout.write(self.style.SUCCESS('Successfully created Viewer group'))
        else:
            self.stdout.write(self.style.WARNING('Viewer group already exists'))

        # Create Uploader group
        uploader_group, uploader_created = Group.objects.get_or_create(name='Uploader')
        if uploader_created:
            self.stdout.write(self.style.SUCCESS('Successfully created Uploader group'))
        else:
            self.stdout.write(self.style.WARNING('Uploader group already exists')) 