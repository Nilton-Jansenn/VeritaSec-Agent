from pathlib import Path

from fastapi.testclient import TestClient

from aplicacao.main import app


def test_interface_real_chama_pipeline_agent(
    tmp_path,
    monkeypatch,
):
    saidas = tmp_path / "saidas"

    monkeypatch.setenv(
        "VERITASSEC_SAIDAS_DIR",
        str(saidas),
    )

    codigo = tmp_path / "alvo.py"

    codigo.write_text(
        "print('veritassec-agent')\n",
        encoding="utf-8",
    )

    c = TestClient(app)

    r = c.post(
        "/api/interface/analisar",
        json={
            "id": "M13-E2E",
            "regra": "teste-controlado",
            "arquivo": str(codigo),
            "linha": 1,
            "execucao_dinamica_permitida": False,
        },
    )

    assert r.status_code == 200

    d = r.json()

    assert d["modo"] == "agent"

    assert (
        d["arquitetura"]
        == "multiagente"
    )

    resultado = d["resultado"]

    assert (
        len(
            resultado[
                "agentes_executados"
            ]
        )
        == 7
    )

    assert (
        len(resultado["trilha"])
        == 7
    )

    out = Path(
        d["artefatos"]["diretorio"]
    )

    assert out.is_dir()

    assert (
        out / "investigacao.json"
    ).is_file()

    assert (
        out / "trilha-agentes.jsonl"
    ).is_file()

    assert (
        out / "resumo.json"
    ).is_file()

    assert (
        out / "SHA256SUMS.txt"
    ).is_file()
