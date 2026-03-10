from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def admin_only(view_func):
    """Apenas Administradores e Superusuários"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.tipo_profissional == 'ADM':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Acesso restrito à coordenação/administração.")
    return _wrapped_view

def health_team(view_func):
    """Equipe de Saúde (Médicos, Enfermeiros, Farmacêuticos)"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.tipo_profissional in ['MED', 'ENF', 'FAR']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Acesso restrito à equipe assistencial.")
    return _wrapped_view

def medico_only(view_func):
    """Exclusivo para Médicos"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.tipo_profissional == 'MED':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Acesso exclusivo para profissionais médicos.")
    return _wrapped_view