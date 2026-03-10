import json
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Paciente, Medicao, Usuario
from .decorators import health_team, admin_only


# --- 1. AUTENTICAÇÃO E LOGIN ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Usuário inativo. Contate a administração.')
            else:
                login(request, user)
                if user.mudar_senha:
                    return redirect('trocar_senha')
                return redirect('index')
        else:
            messages.error(request, 'E-mail, usuário ou senha inválidos.')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def trocar_senha(request):
    if request.method == 'POST':
        nova = request.POST.get('nova_senha')
        conf = request.POST.get('confirmacao')
        if nova == conf and len(nova) >= 6:
            request.user.set_password(nova)
            request.user.mudar_senha = False
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Senhas não conferem ou são muito curtas (mínimo 6 caracteres).')
    return render(request, 'trocar_senha.html')


# --- 2. ROTAS PROTEGIDAS DO MAREVAN ---
@login_required
def index(request):
    if request.user.mudar_senha:
        return redirect('trocar_senha')
    return render(request, 'index.html')


@login_required
@health_team
def gestao_pacientes(request):
    termo = request.GET.get('busca', '')
    if termo:
        pacientes = Paciente.objects.filter(
            Q(nome__icontains=termo) | Q(cpf__icontains=termo) | Q(cross__icontains=termo)
        ).order_by('-ativo', 'nome')
    else:
        pacientes = Paciente.objects.all().order_by('-ativo', 'nome')

    return render(request, 'pacientes.html', {'pacientes': pacientes})


@login_required
@health_team
def salvar_paciente(request):
    """View para criar ou editar um paciente via Modal"""
    if request.method == 'POST':
        p_id = request.POST.get('paciente_id')

        if p_id:
            p = get_object_or_404(Paciente, id=p_id)
        else:
            p = Paciente()

        p.nome = request.POST.get('nome', '').upper()
        p.cpf = request.POST.get('cpf')

        cross = request.POST.get('cross')
        p.cross = int(cross) if cross else None

        nasc = request.POST.get('data_nascimento')
        if nasc: p.data_nascimento = nasc

        d_ins = request.POST.get('data_insercao')
        if d_ins: p.data_insercao = d_ins

        p.sexo = request.POST.get('sexo')
        p.municipio = request.POST.get('municipio')
        p.medico = request.POST.get('medico')
        p.indicacao = request.POST.get('indicacao')

        meta = request.POST.get('meta')
        p.meta = int(meta) if meta else 2
        p.ativo = True if request.POST.get('ativo') else False

        p.save()
        messages.success(request, 'Paciente salvo com sucesso!')
    return redirect('gestao_pacientes')


@login_required
@health_team
def dar_alta_paciente(request, id):
    """View API para inativar o paciente"""
    if request.method == 'POST':
        p = get_object_or_404(Paciente, id=id)
        p.ativo = False
        p.data_alta = date.today()
        p.save()
        return JsonResponse({'status': 'success', 'message': 'Alta realizada.'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
@health_team
def atendimento(request):
    """Carrega a fila de atendimento ou o prontuário de um paciente específico"""

    # Verifica se um paciente foi clicado na lista
    paciente_id = request.GET.get('id')

    if paciente_id:
        # ================= TELA DO PRONTUÁRIO =================
        paciente = get_object_or_404(Paciente, id=paciente_id)

        # Busca Histórico
        medicoes = paciente.medicoes.all().order_by('-data_medicao')
        historico_tabela = medicoes[:10]

        # Gráfico (ordem cronológica - do mais antigo pro mais novo)
        dados_grafico = paciente.medicoes.all().order_by('data_medicao')
        grafico_labels = [m.data_medicao.strftime('%d/%m/%Y') for m in dados_grafico]
        grafico_data = [m.valor_inr for m in dados_grafico]

        # Faixa Terapêutica
        meta_min, meta_max = 2.0, 3.0
        indicacao_txt = (paciente.indicacao or "").lower()
        if 'prótese' in indicacao_txt or 'mecanica' in indicacao_txt:
            meta_min, meta_max = 2.5, 3.5

        return render(request, 'atendimento.html', {
            'paciente': paciente,
            'historico': historico_tabela,
            'grafico_labels': json.dumps(grafico_labels),
            'grafico_data': json.dumps(grafico_data),
            'meta_min': meta_min,
            'meta_max': meta_max,
        })

    else:
        # ================= TELA DA FILA DE ATENDIMENTO =================
        # Se não há ID, mostra a lista alfabética de pacientes ativos
        pacientes = Paciente.objects.filter(ativo=True).order_by('nome')
        return render(request, 'atendimento.html', {'pacientes_lista': pacientes})

@login_required
@health_team
def registrar_atendimento(request):
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente_id')
        inr = request.POST.get('inr')
        obs = request.POST.get('obs')

        paciente = get_object_or_404(Paciente, id=paciente_id)

        Medicao.objects.create(
            paciente=paciente,
            usuario=request.user,
            valor_inr=float(inr.replace(',', '.')),  # Prevenção de erro de digitação
            intercorrencia_txt=obs,
            intercorrencia=bool(obs)
        )
        messages.success(request, 'INR registrado com sucesso!')
        # Redireciona de volta para o prontuário do paciente
        return redirect(f"/atendimento/?id={paciente.id}")
    return redirect('atendimento')

@login_required
@admin_only
def linha_cuidado(request):
    return render(request, 'dashboard.html')


# --- ROTAS DE API (Usadas pelo scripts.js e Chart.js) ---

@login_required
@health_team
def api_paciente(request, id):
    """API chamada pelo JavaScript para preencher o Modal de Edição"""
    try:
        p = get_object_or_404(Paciente, id=id)

        # Formatação segura de datas para o input type="date"
        d_nasc = p.data_nascimento.strftime('%Y-%m-%d') if p.data_nascimento else ''
        d_ins = p.data_insercao.strftime('%Y-%m-%d') if p.data_insercao else ''

        return JsonResponse({
            'status': 'success',
            'id': p.id,
            'nome': p.nome or '',
            'cpf': p.cpf or '',
            'cross': p.cross or '',
            'nascimento': d_nasc,
            'data_insercao': d_ins,
            'municipio': p.municipio or '',
            'medico': p.medico or '',
            'meta': p.meta or 2,
            'indicacao': p.indicacao or '',
            'sexo': p.sexo or 1,
            'ativo': p.ativo
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@admin_only
def api_dashboard(request):
    """API blindada para o Dashboard"""
    # Busca pacientes ativos (considerando 1 ou True)
    pacientes = Paciente.objects.filter(ativo__in=[True, 1]).prefetch_related('medicoes')
    hoje = date.today()

    lista_pacientes = []
    for p in pacientes:
        # Cálculo de idade seguro
        idade = 0
        if p.data_nascimento:
            idade = hoje.year - p.data_nascimento.year - (
                        (hoje.month, hoje.day) < (p.data_nascimento.month, p.data_nascimento.day))

        # Identifica a meta
        meta_min, meta_max = 2.0, 3.0
        indicacao_txt = (p.indicacao or "").lower()
        if any(x in indicacao_txt for x in ['prótese', 'mecanica', 'protese', 'mecanica']):
            meta_min, meta_max = 2.5, 3.5

        # Captura medições garantindo formato de data string para JS
        lista_medicoes = []
        for m in p.medicoes.all():
            if m.data_medicao:
                lista_medicoes.append({
                    'data': m.data_medicao.strftime('%Y-%m-%d'),
                    'inr': m.valor_inr or 0.0
                })

        lista_pacientes.append({
            'sexo': 'Masculino' if str(p.sexo) == '1' else 'Feminino',
            'idade': idade,
            'municipio': (p.municipio or "Não Informado").title(),
            'indicacao': (p.indicacao or "OUTROS").strip().upper(),
            'meta_min': meta_min,
            'meta_max': meta_max,
            'medicoes': lista_medicoes
        })

    return JsonResponse({'dados_pacientes': lista_pacientes}, safe=False)