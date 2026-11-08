from pathlib import Path

from fastapi.testclient import TestClient

from aplicacao.main import app


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


def test_interface_visual_agent():
    c = TestClient(app)

    r = c.get("/interface")

    assert r.status_code == 200

    html = r.text

    assert (
        "VeritasSec-Agent"
        in html
    )

    assert (
        "Investigação Multiagente"
        in html
    )

    assert (
        "agent-trace"
        in html
    )


def test_interface_real_sarif(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv(
        "VERITASSEC_SAIDAS_DIR",
        str(tmp_path / "saidas"),
    )

    c = TestClient(app)

    r = c.post(
        "/api/interface/analisar",
        json={
            "sarif_path": str(SARIF),
            "projeto_path": str(JUICE),
            "indice": 0,
        },
    )

    assert r.status_code == 200

    d = r.json()

    assert d["modo"] == "agent"
    assert d["origem"] == "sarif"

    assert (
        d["total_achados_sarif"]
        == 36
    )

    assert (
        len(
            d["resultado"][
                "agentes_executados"
            ]
        )
        == 7
    )

    assert (
        len(
            d["resultado"]["trilha"]
        )
        == 7
    )
