from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if (not request.user.is_authenticated) or (not request.user.profile.is_admin) or (not request.user.is_staff):
            messages.error(request, 'Доступ запрещён. Требуются права администратора.')
            return redirect('puzzlestore:catalog')
        return view_func(request, *args, **kwargs)
    return wrapper