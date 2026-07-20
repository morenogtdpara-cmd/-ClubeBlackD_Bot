import json
from pathlib import Path

ARQUIVO_FILA = Path("fila.json")


def carregar_fila():
    if not ARQUIVO_FILA.exists():
        return []

    with open(ARQUIVO_FILA, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_fila(fila):
    with open(ARQUIVO_FILA, "w", encoding="utf-8") as arquivo:
        json.dump(
            fila,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def adicionar_na_fila(item):
    fila = carregar_fila()

    fila.append(item)

    salvar_fila(fila)


def pegar_fila():
    return carregar_fila()


def remover_da_fila(indice):
    fila = carregar_fila()

    if 0 <= indice < len(fila):
        fila.pop(indice)

    salvar_fila(fila)