from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import SignUpForm
from .models import WatchItem

class SignInView(LoginView):
    template_name = 'registration/login.html'

class SignOutView(LogoutView):
    template_name = 'registration/logged_out.html'

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "회원가입이 완료되었습니다.")
            return redirect('crawlings:index')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def watchlist(request):
    items = WatchItem.objects.filter(user=request.user).order_by('-id')
    return render(request, 'accounts/watchlist.html', {'items': items})

@login_required
def add_watch(request):
    name = (request.POST.get('company_name') or '').strip()
    code = (request.POST.get('stock_code') or '').strip()
    if not name:
        messages.warning(request, "회사명이 비었습니다.")
        return redirect('accounts:watchlist')
    WatchItem.objects.get_or_create(
        user=request.user, company_name=name,
        defaults={'stock_code': code}
    )
    messages.success(request, f"'{name}'을(를) 관심종목에 추가했습니다.")
    return redirect(request.META.get('HTTP_REFERER', reverse('accounts:watchlist')))

@login_required
def remove_watch(request, pk):
    item = get_object_or_404(WatchItem, pk=pk, user=request.user)
    name = item.company_name
    item.delete()
    messages.info(request, f"'{name}' 관심종목을 해제했습니다.")
    return redirect(request.META.get('HTTP_REFERER', reverse('accounts:watchlist')))
