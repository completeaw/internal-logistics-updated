from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Assigns a user to a specified group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('group_name', type=str)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        group_name = kwargs['group_name']

        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name=group_name)
            
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f'Successfully added {username} to {group_name} group'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Group {group_name} does not exist')) 