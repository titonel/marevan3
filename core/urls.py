from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('trocar-senha/', views.trocar_senha, name='trocar_senha'),

    # Telas Principais
    path('', views.index, name='index'),
    path('pacientes/', views.gestao_pacientes, name='gestao_pacientes'),
    path('paciente/salvar/', views.salvar_paciente, name='salvar_paciente'),
    path('paciente/alta/<int:id>/', views.dar_alta_paciente, name='dar_alta_paciente'),

    path('atendimento/', views.atendimento, name='atendimento'),
    path('atendimento/registrar/', views.registrar_atendimento, name='registrar_atendimento'),
    path('dashboard/', views.linha_cuidado, name='linha_cuidado'),

    # APIs para o JavaScript (Substituindo o comportamento do Flask)
    path('api/paciente/<int:id>/', views.api_paciente, name='api_paciente'),
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),

    # Administração do site
    path('admin-painel/', views.painel_admin, name='painel_admin'),
    path('admin-painel/usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('admin-painel/usuario/toggle/<int:user_id>/', views.toggle_usuario_status, name='toggle_usuario_status'),
    path('admin-painel/usuario/criar/', views.criar_usuario, name='criar_usuario'),
    path('admin-painel/usuario/salvar/', views.salvar_usuario, name='salvar_usuario'),
    path('admin-painel/usuario/excluir/<int:user_id>/', views.excluir_usuario, name='excluir_usuario'),
    path('admin-painel/pacientes/', views.gerenciar_pacientes_admin, name='gerenciar_pacientes_admin'),
]