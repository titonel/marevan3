import shutil
import os


def copiar_projeto():
    # Configuração de origem e destino
    origens = ['core', 'marevan3']
    destino_base = r'\\172.15.0.152\marevan'  # Ajuste o nome da pasta se necessário

    for pasta in origens:
        caminho_origem = os.path.join(os.getcwd(), pasta)
        caminho_destino = os.path.join(destino_base, pasta)

        try:
            # Remove a pasta no destino se já existir para garantir uma cópia limpa
            if os.path.exists(caminho_destino):
                shutil.rmtree(caminho_destino)

            shutil.copytree(caminho_origem, caminho_destino)
            print(f"Sucesso: {pasta} copiada para {destino_base}")
        except Exception as e:
            print(f"Erro ao copiar {pasta}: {e}")


if __name__ == "__main__":
    copiar_projeto()