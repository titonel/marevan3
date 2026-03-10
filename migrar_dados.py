import os
import django
import sqlite3
from datetime import datetime
from django.utils import timezone

# Configura o ambiente do Django para podermos usar os Models neste script isolado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marevan3.settings')
django.setup()

from core.models import Paciente, Medicao, Usuario

ARQUIVO_LEGADO = 'marevan.db'


def parse_date(date_str):
    """Lida com strings de data mal formatadas do SQLite do Flask"""
    if not date_str:
        return None
    try:
        # Pega apenas os 10 primeiros caracteres (YYYY-MM-DD)
        return datetime.strptime(str(date_str)[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def parse_datetime(dt_str):
    """Lida com strings de datetime do SQLite do Flask"""
    if not dt_str:
        return timezone.now()
    try:
        # Tenta parsear no formato padrão de log de BD (ignorando os milissegundos)
        dt = datetime.strptime(str(dt_str)[:19], '%Y-%m-%d %H:%M:%S')
        # Torna o datetime "aware" se o fuso horário estiver ativo no Django
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
    except ValueError:
        try:
            # Caso esteja só a data, converte para datetime à meia-noite
            dt = datetime.strptime(str(dt_str)[:10], '%Y-%m-%d')
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except ValueError:
            return timezone.now()


def migrar():
    print("Iniciando migração de dados Flask -> Django...")

    # 1. Cria um Usuário Genérico corrigindo o erro de constraint (email_verificado e mudar_senha)
    usuario_legado, created = Usuario.objects.get_or_create(
        username="legado_flask",
        defaults={
            'first_name': 'Sistema',
            'last_name': 'Legado (Flask)',
            'is_active': False,
            'email_verificado': True,  # <-- CORREÇÃO DO ERRO AQUI
            'mudar_senha': False  # <-- CORREÇÃO DO ERRO AQUI
        }
    )
    if created:
        print("Criado usuário 'legado_flask' para rastreabilidade.")

    # Conecta ao banco antigo do Flask
    try:
        conn = sqlite3.connect(ARQUIVO_LEGADO)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    except sqlite3.OperationalError:
        print(
            f"ERRO: Não foi possível encontrar o arquivo '{ARQUIVO_LEGADO}'. Certifique-se de que ele está na mesma pasta que este script.")
        return

    # --- MIGRANDO PACIENTES ---
    print("\nLendo tb_pacientes...")
    cursor.execute("SELECT * FROM tb_pacientes")
    pacientes_antigos = cursor.fetchall()

    pacientes_criados = 0
    for p in pacientes_antigos:
        # Se o paciente já existe (em caso de rodar o script 2 vezes), pula a criação
        if Paciente.objects.filter(id=p['id']).exists():
            continue

        try:
            Paciente.objects.create(
                id=p['id'],
                nome=p['nome'],
                cross=p['cross'],
                cpf=p['cpf'],
                sexo=p['sexo'],
                data_nascimento=parse_date(p['data_nascimento']),
                municipio=p['municipio'],
                indicacao=p['indicacao'],
                medico=p['medico'],
                meta=p['meta'],
                ativo=bool(p['ativo']),
                data_insercao=parse_datetime(p['data_insercao']),
                data_alta=parse_date(p['data_alta'])
            )
            pacientes_criados += 1
        except Exception as e:
            print(f"Erro ao importar paciente ID {p['id']} ({p['nome']}): {e}")

    print(f"Sucesso: {pacientes_criados} novos pacientes importados.")

    # --- MIGRANDO MEDIÇÕES ---
    print("\nLendo tb_medicoes...")
    cursor.execute("SELECT * FROM tb_medicoes")
    medicoes_antigas = cursor.fetchall()

    medicoes_criadas = 0
    for m in medicoes_antigas:
        if Medicao.objects.filter(id=m['id']).exists():
            continue

        try:
            paciente_obj = Paciente.objects.get(id=m['paciente_id'])

            Medicao.objects.create(
                id=m['id'],
                paciente=paciente_obj,
                usuario=usuario_legado,
                valor_inr=m['valor_inr'],
                data_medicao=parse_datetime(m['data_medicao']),
                intercorrencia=bool(m['intercorrencia']),
                intercorrencia_txt=m['intercorrencia_txt']
            )
            medicoes_criadas += 1
        except Paciente.DoesNotExist:
            print(f"Aviso: Medição {m['id']} ignorada pois o Paciente ID {m['paciente_id']} não existe.")
        except Exception as e:
            print(f"Erro ao importar medição ID {m['id']}: {e}")

    print(f"Sucesso: {medicoes_criadas} novas medições importadas.")

    conn.close()
    print("\nMigração concluída com sucesso!")


if __name__ == '__main__':
    migrar()