from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .modelos import (
    MetricasExperimentais,
    Pareamento,
    RegistroGroundTruth,
)


def hash_ground_truth(
    registros: list[RegistroGroundTruth],
) -> str:

    conteudo = json.dumps(
        [
            item.model_dump(
                mode="json"
            )
            for item in registros
        ],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(
        conteudo
    ).hexdigest()


def escrever_relatorios(
    diretorio: str | Path,
    pareamentos: list[Pareamento],
    metricas: MetricasExperimentais,
    hash_gt: str,
) -> Path:

    raiz = Path(diretorio)
    raiz.mkdir(
        parents=True,
        exist_ok=True,
    )

    resumo = {
        "hash_ground_truth": hash_gt,
        "metricas": metricas.model_dump(
            mode="json"
        ),
    }

    (
        raiz
        / "resumo-experimental.json"
    ).write_text(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    campos = [
        "chave",
        "pareado",
        "gt",
        "sistema",
        "origem",
    ]

    with (
        raiz
        / "matriz-comparacao.csv"
    ).open(
        "w",
        encoding="utf-8",
        newline="",
    ) as arquivo:

        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos,
        )

        writer.writeheader()

        for p in pareamentos:
            writer.writerow(
                {
                    "chave": p.chave,
                    "pareado": p.pareado,
                    "gt": (
                        p.ground_truth.classe.value
                        if p.ground_truth
                        else ""
                    ),
                    "sistema": (
                        p.sistema.classe.value
                        if p.sistema
                        else ""
                    ),
                    "origem": (
                        p.sistema.origem
                        if p.sistema
                        else ""
                    ),
                }
            )

    divergencias = [
        p
        for p in pareamentos
        if (
            p.pareado
            and p.ground_truth is not None
            and p.sistema is not None
            and (
                (
                    p.ground_truth.classe.value
                    == "positivo"
                    and p.sistema.classe.value
                    == "refutado"
                )
                or
                (
                    p.ground_truth.classe.value
                    == "negativo"
                    and p.sistema.classe.value
                    == "confirmado"
                )
            )
        )
    ]

    with (
        raiz
        / "divergencias.csv"
    ).open(
        "w",
        encoding="utf-8",
        newline="",
    ) as arquivo:

        writer = csv.writer(arquivo)

        writer.writerow(
            [
                "chave",
                "ground_truth",
                "sistema",
            ]
        )

        for p in divergencias:
            assert p.ground_truth
            assert p.sistema

            writer.writerow(
                [
                    p.chave,
                    p.ground_truth.classe.value,
                    p.sistema.classe.value,
                ]
            )

    nao_pareados = [
        p
        for p in pareamentos
        if not p.pareado
    ]

    with (
        raiz
        / "nao-pareados.csv"
    ).open(
        "w",
        encoding="utf-8",
        newline="",
    ) as arquivo:

        writer = csv.writer(arquivo)

        writer.writerow(
            [
                "chave",
                "lado",
            ]
        )

        for p in nao_pareados:
            lado = (
                "ground_truth"
                if p.ground_truth
                else "sistema"
            )

            writer.writerow(
                [
                    p.chave,
                    lado,
                ]
            )

    return raiz
