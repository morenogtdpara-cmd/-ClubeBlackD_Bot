import json
from pathlib import Path
from threading import RLock


ARQUIVO_FILA = Path("fila.json")
LOCK_FILA = RLock()


def carregar_fila():
    with LOCK_FILA:
        if not ARQUIVO_FILA.exists():
            return []

        try:
            with ARQUIVO_FILA.open(
                "r",
                encoding="utf-8",
            ) as arquivo:
                dados = json.load(arquivo)
        except (json.JSONDecodeError, OSError):
            return []

        return dados if isinstance(dados, list) else []


def salvar_fila(fila):
    with LOCK_FILA:
        temporario = ARQUIVO_FILA.with_suffix(".tmp")

        with temporario.open(
            "w",
            encoding="utf-8",
        ) as arquivo:
            json.dump(
                fila,
                arquivo,
                ensure_ascii=False,
                indent=4,
            )

        temporario.replace(ARQUIVO_FILA)


def adicionar_na_fila(item):
    with LOCK_FILA:
        fila = carregar_fila()
        fila.append(item)
        salvar_fila(fila)


def pegar_fila():
    return carregar_fila()


def remover_da_fila(indice):
    with LOCK_FILA:
        fila = carregar_fila()

        if 0 <= indice < len(fila):
            fila.pop(indice)

        salvar_fila(fila)


def atualizar_item(indice, dados):
    with LOCK_FILA:
        fila = carregar_fila()

        if 0 <= indice < len(fila):
            fila[indice] = dados

        salvar_fila(fila)
