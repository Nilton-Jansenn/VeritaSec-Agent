from pathlib import Path

from aplicacao.multiagente.sarif_agent import (
    carregar_achados_sarif,
)
from aplicacao.multiagente.pipeline_agent import (
    executar_pipeline_sarif_agent,
)


PROJ = Path(__file__).resolve().parents[1]

SARIF = (
    PROJ
    / "input"
    / "sarif"
    / "juiceShop_code.sarif"
)

JUICE = (
    PROJ
    / "input"
    / "projects"
    / "juice-shop"
)


def test_sarif_real_36():
    achados = carregar_achados_sarif(
        str(SARIF),
        str(JUICE),
    )

    assert len(achados) == 36

    assert len(
        {
            a["fingerprint"]
            for a in achados
        }
    ) == 36


def test_arquivos_ficam_dentro_do_projeto():
    achados = carregar_achados_sarif(
        str(SARIF),
        str(JUICE),
    )

    raiz = JUICE.resolve()

    for a in achados:
        Path(
            a["arquivo"]
        ).resolve().relative_to(
            raiz
        )


def test_pipeline_primeiro_achado_real():
    pacote = executar_pipeline_sarif_agent(
        sarif_path=str(SARIF),
        projeto_path=str(JUICE),
        indice=0,
    )

    assert (
        pacote[
            "total_achados_sarif"
        ]
        == 36
    )

    r = pacote["resultado"]

    assert (
        len(r["agentes_executados"])
        == 7
    )

    assert len(r["trilha"]) == 7

    assert (
        pacote["achado"][
            "metadados"
        ]["origem"]
        == "sarif"
    )
