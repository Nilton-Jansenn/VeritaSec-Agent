from pathlib import Path
import tempfile

from aplicacao.multiagente.modelos import (
    AchadoMultiagente,
)

from aplicacao.multiagente.ciclo_finding import (
    construir_callbacks_ciclo,
)


def _dados(
    autorizadas=None,
):

    return {
        "scr": {
            "nivel_sustentacao": (
                "PLAUSIVEL"
            ),
        },
        "seeds_cognitivas": {
            "sementes_validadas": [
                "../fora.txt"
            ],
        },
        "politica_escopo": {
            "capacidades_autorizadas": (
                autorizadas
                or []
            ),
        },
        "plano_aquisicao_evidencia": {},
        "aquisicao_evidencia": {},
    }


def test_planejador_retorna_dict():

    with tempfile.TemporaryDirectory() as td:

        raiz = Path(td)

        sandbox = raiz / "sandbox"
        sandbox.mkdir()

        arquivo = raiz / "x.js"
        arquivo.write_text(
            "x",
            encoding="utf-8",
        )

        achado = AchadoMultiagente(
            id="m27b",
            regra="path traversal",
            cwe="CWE-22",
            arquivo=str(arquivo),
            linha=1,
            execucao_dinamica_permitida=True,
            raiz_sandbox=str(sandbox),
            sementes=[
                "../fora.txt"
            ],
            max_iteracoes=3,
        )

        contexto, planejar, _ = (
            construir_callbacks_ciclo(
                achado=achado,
                dados=_dados(
                    [
                        "path_traversal",
                        "busca_evolucionaria",
                        "oraculo_path_traversal",
                    ]
                ),
            )
        )

        pedido = planejar(
            contexto
        )

        assert isinstance(
            pedido,
            dict,
        )

        assert (
            pedido["capacidade"]
            == "path_traversal"
        )


def test_autorizador_retorna_dict():

    with tempfile.TemporaryDirectory() as td:

        arquivo = Path(td) / "x.py"

        arquivo.write_text(
            "x=1",
            encoding="utf-8",
        )

        achado = AchadoMultiagente(
            id="m27b2",
            arquivo=str(arquivo),
        )

        _, _, autorizar = (
            construir_callbacks_ciclo(
                achado=achado,
                dados=_dados(
                    [
                        "path_traversal"
                    ]
                ),
            )
        )

        resultado = autorizar(
            {
                "capacidade": (
                    "path_traversal"
                ),
                "parametros": {},
            }
        )

        assert isinstance(
            resultado,
            dict,
        )

        assert (
            resultado["autorizada"]
            is True
        )


def test_capability_nao_autorizada():

    with tempfile.TemporaryDirectory() as td:

        arquivo = Path(td) / "x.py"

        arquivo.write_text(
            "x=1",
            encoding="utf-8",
        )

        achado = AchadoMultiagente(
            id="m27b3",
            arquivo=str(arquivo),
        )

        _, _, autorizar = (
            construir_callbacks_ciclo(
                achado=achado,
                dados=_dados(),
            )
        )

        r = autorizar(
            {
                "capacidade": (
                    "path_traversal"
                )
            }
        )

        assert (
            r["autorizada"]
            is False
        )


def test_sem_dinamica_retorna_sem_acao():

    with tempfile.TemporaryDirectory() as td:

        arquivo = Path(td) / "x.py"

        arquivo.write_text(
            "x=1",
            encoding="utf-8",
        )

        achado = AchadoMultiagente(
            id="m27b4",
            arquivo=str(arquivo),
        )

        contexto, planejar, _ = (
            construir_callbacks_ciclo(
                achado=achado,
                dados=_dados(),
            )
        )

        pedido = planejar(
            contexto
        )

        assert isinstance(
            pedido,
            dict,
        )

        assert (
            pedido["sem_acao"]
            is True
        )
