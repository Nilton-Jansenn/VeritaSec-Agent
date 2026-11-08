from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .modelos import AchadoMultiagente


# Hipoteses estaticas, nao vulnerabilidades confirmadas.
# Nenhum resultado recebe classificacao TP automaticamente.

_PADROES = (
    (
        "VS-DESC-EVAL",
        "CWE-95",
        re.compile(r"\beval\s*\("),
    ),
    (
        "VS-DESC-FUNCTION",
        "CWE-95",
        re.compile(r"\bnew\s+Function\s*\("),
    ),
    (
        "VS-DESC-EXEC",
        "CWE-78",
        re.compile(
            r"\b(?:execSync|child_process\.exec)\s*\("
        ),
    ),
    (
        "VS-DESC-TLS",
        "CWE-295",
        re.compile(
            r"\brejectUnauthorized\s*:\s*false\b"
        ),
    ),
    (
        "VS-DESC-HTML",
        "CWE-79",
        re.compile(
            r"\bdangerouslySetInnerHTML\b"
        ),
    ),
)


def descobrir_candidatos(
    projeto: str,
    *,
    max_arquivos: int = 3000,
    max_candidatos: int = 100,
) -> list[AchadoMultiagente]:
    """
    Descoberta estatica independente do SARIF.

    Resultados sao candidatos, nao vulnerabilidades
    confirmadas. Nao executa codigo nem acessa a rede.
    """

    raiz = Path(projeto).expanduser().resolve()

    if not raiz.is_dir():
        raise ValueError("PROJETO_INVALIDO")

    ignorados = {
        ".git", "node_modules", "vendor",
        "dist", "build", ".venv", "coverage",
        ".next", "target",
    }

    extensoes = {
        ".js", ".jsx", ".ts", ".tsx",
        ".py", ".java", ".vue",
    }

    candidatos = []
    examinados = 0

    for caminho in sorted(raiz.rglob("*")):

        if any(
            parte in ignorados
            for parte in caminho.relative_to(raiz).parts
        ):
            continue

        if caminho.suffix.lower() not in extensoes:
            continue

        if caminho.is_symlink():
            continue

        if not caminho.is_file():
            continue

        if not caminho.resolve().is_relative_to(raiz):
            continue

        if caminho.stat().st_size > 512 * 1024:
            continue

        examinados += 1

        if examinados > max_arquivos:
            break

        try:
            linhas = caminho.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()
        except OSError:
            continue

        for numero, linha in enumerate(linhas, 1):
            for regra, cwe, padrao in _PADROES:

                if not padrao.search(linha):
                    continue

                identidade = (
                    f"{caminho.relative_to(raiz)}:"
                    f"{numero}:{regra}"
                )

                digest = hashlib.sha256(
                    identidade.encode("utf-8")
                ).hexdigest()[:20]

                candidatos.append(
                    AchadoMultiagente(
                        id=f"desc-{digest}",
                        regra=regra,
                        cwe=cwe,
                        mensagem=(
                            "Padrao potencialmente sensivel "
                            "identificado por descoberta "
                            "estatica autonoma. Requer "
                            "investigacao contextual."
                        ),
                        arquivo=str(caminho),
                        linha=numero,
                        metadados={
                            "projeto": str(raiz),
                            "origem": "DESCOBERTA_AUTONOMA",
                            "identidade": identidade,
                            "confirmacao": "NAO_CONFIRMADA",
                        },
                        execucao_dinamica_permitida=False,
                    )
                )

                if len(candidatos) >= max_candidatos:
                    return candidatos

    return candidatos
