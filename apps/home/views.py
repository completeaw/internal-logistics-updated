from django.shortcuts import render, redirect
from apps.home.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserPasswordChangeForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required

# Index
def index(request):
  return render(request, 'pages/index.html')

# Dashboard
def dashboard(request):
  context = {
    'parent': 'dashboard',
    'segment': 'dashboard'
  }
  return render(request, 'pages/dashboard/dashboard.html', context)

@login_required(login_url='/accounts/login/')
def traffic(request):
  context = {
    'parent': 'dashboard',
    'segment': 'traffic'
  }
  return render(request, 'pages/dashboard/traffic-sources.html', context)

@login_required(login_url='/accounts/login/')
def analysis(request):
  context = {
    'parent': 'dashboard',
    'segment': 'analysis'
  }
  return render(request, 'pages/dashboard/app-analysis.html', context)

# Pages 
@login_required(login_url='/accounts/login/')
def kanban(request):
  context = {
    'segment': 'kanban'
  }
  return render(request, 'pages/kanban.html', context)

@login_required(login_url='/accounts/login/')
def messages(request):
  context = {
    'segment': 'messages'
  }
  return render(request, 'pages/messages.html', context)

@login_required(login_url='/accounts/login/')
def user_list(request):
  context = {
    'segment': 'users'
  }
  return render(request, 'pages/users.html', context)

@login_required(login_url='/accounts/login/')
def transactions(request):
  context = {
    'segment': 'transactions'
  }
  return render(request, 'pages/transactions.html', context)

@login_required(login_url='/accounts/login/')
def task_list(request):
  context = {
    'segment': 'tasks'
  }
  return render(request, 'pages/tasks.html', context)

@login_required(login_url='/accounts/login/')
def settings(request):
  context = {
    'segment': 'settings'
  }
  return render(request, 'pages/settings.html', context)

@login_required(login_url='/accounts/login/')
def calendar(request):
  context = {
    'segment': 'calendar'
  }
  return render(request, 'pages/calendar.html', context)

@login_required(login_url='/accounts/login/')
def map(request):
  context = {
    'segment': 'map'
  }
  return render(request, 'pages/map.html', context)

@login_required(login_url='/accounts/login/')
def widgets(request):
  context = {
    'segment': 'widgets'
  }
  return render(request, 'pages/widgets.html', context)

@login_required(login_url='/accounts/login/')
def single_message(request):
  context = {
    'segment': 'messages'
  }
  return render(request, 'pages/single-message.html', context)

# Pages -> Tables
@login_required(login_url='/accounts/login/')
def datatables(request):
  context = {
    'parent': 'tables',
    'segment': 'data_tables'
  }
  return render(request, 'pages/tables/datatables.html', context)

@login_required(login_url='/accounts/login/')
def bs_tables(request):
  context = {
    'parent': 'tables',
    'segment': 'bs_tables'
  }
  return render(request, 'pages/tables/bootstrap-tables.html', context)

# Pages -> Examples
@login_required(login_url='/accounts/login/')
def pricing(request):
  context = {
    'parent': 'examples',
    'segment': 'pricing'
  }
  return render(request, 'pages/examples/pricing.html', context)

@login_required(login_url='/accounts/login/')
def billing(request):
  context = {
    'parent': 'examples',
    'segment': 'billing'
  }
  return render(request, 'pages/examples/billing.html', context)

@login_required(login_url='/accounts/login/')
def invoice(request):
  context = {
    'parent': 'examples',
    'segment': 'invoice'
  }
  return render(request, 'pages/examples/invoice.html', context)

# Pages -> Components
@login_required(login_url='/accounts/login/')
def buttons(request):
  context = {
    'parent': 'components',
    'segment': 'buttons'
  }
  return render(request, 'pages/components/buttons.html', context)

@login_required(login_url='/accounts/login/')
def notifications(request):
  context = {
    'parent': 'components',
    'segment': 'notifications'
  }
  return render(request, 'pages/components/notifications.html', context)

@login_required(login_url='/accounts/login/')
def forms(request):
  context = {
    'parent': 'components',
    'segment': 'forms'
  }
  return render(request, 'pages/components/forms.html', context)

@login_required(login_url='/accounts/login/')
def modals(request):
  context = {
    'parent': 'components',
    'segment': 'modals'
  }
  return render(request, 'pages/components/modals.html', context)

@login_required(login_url='/accounts/login/')
def typography(request):
  context = {
    'parent': 'components',
    'segment': 'typography'
  }
  return render(request, 'pages/components/typography.html', context)

# Authentication
def register_view(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      print("Account created successfully!")
      form.save()
      return redirect('/accounts/login/')
    else:
      print("Registration failed!")
  else:
    form = RegistrationForm()
  
  context = { 'form': form }
  return render(request, 'accounts/sign-up.html', context)

class UserLoginView(LoginView):
  form_class = LoginForm
  template_name = 'accounts/sign-in.html'

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/password-change.html'
  form_class = UserPasswordChangeForm

class UserPasswordResetView(PasswordResetView):
  template_name = 'accounts/forgot-password.html'
  form_class = UserPasswordResetForm

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/reset-password.html'
  form_class = UserSetPasswordForm

def logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

# Extra
def lock(request):
  return render(request, 'accounts/lock.html')

def error_404(request):
  return render(request, 'accounts/404.html')

def error_500(request):
  return render(request, 'accounts/500.html')

def handler404(request, exception=None):
  return render(request, 'accounts/404.html')

def handler403(request, exception=None):
  return render(request, 'accounts/403.html')

def handler500(request, exception=None):
  return render(request, 'accounts/500.html')


# i18n
def i18n_view(request):
  context = {
    'parent': 'apps',
    'segment': 'i18n'
  }
  return render(request, 'pages/apps/i18n.html', context)