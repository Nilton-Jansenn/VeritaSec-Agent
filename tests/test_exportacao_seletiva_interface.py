import pytest

from fastapi import HTTPException

from aplicacao.ui.interface_agent import pagina_interface
from aplicacao.api.interface_agent import (
    exportar_execucao_final_136,
)


def test_controles_renderizados():
    html = pagina_interface()

    for identificador in (
        "vs4SelecionarTodos",
        "vs4FormatoDocx",
        "vs4FormatoCsv",
        "vs4ExportarFinal",
    ):
        assert html.count(f'id="{identificador}"') == 1


def test_layout_aprovado_preservado():
    html = pagina_interface()

    assert 'id="vsUxAbasCorrecao20261020"' in html
    assert 'id="vsUxAbasScript20261020"' in html
    assert 'id="vsLayoutConsolidado20261019"' in html


def test_chamada_envia_formatos():
    html = pagina_interface()

    assert "JSON.stringify({formatos:formatos})" in html
    assert "Selecione DOCX, CSV ou ambos." in html


@pytest.mark.parametrize(
    "formatos",
    [
        [],
        ["PDF"],
        ["CSV", "PDF"],
        ["docx"],
        [123],
        None,
    ],
)
def test_rejeita_formatos_invalidos(formatos):
    with pytest.raises(HTTPException) as erro:
        exportar_execucao_final_136(
            job_id="teste-inexistente",
            formatos=formatos,
        )

    assert erro.value.status_code == 400


@pytest.mark.parametrize(
    "formatos",
    [
        ["DOCX"],
        ["CSV"],
        ["DOCX", "CSV"],
    ],
)
def test_formatos_validos_exigem_execucao_real(formatos):
    with pytest.raises(HTTPException) as erro:
        exportar_execucao_final_136(
            job_id="execucao-inexistente-para-teste",
            formatos=formatos,
        )

    assert erro.value.status_code == 404
