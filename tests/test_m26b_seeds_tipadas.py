from pathlib import Path
import tempfile

from aplicacao.multiagente.modelos import (
    AchadoMultiagente,
    DecisaoAgenteLLM,
)

from aplicacao.multiagente.seeds_cognitivas import (
    aplicar_sementes_ao_plano,
    extrair_sementes_tipadas,
    validar_sementes_cognitivas,
)

from aplicacao.multiagente.plano_evidencia import (
    construir_plano_aquisicao,
)

from aplicacao.multiagente.politica_escopo import (
    calcular_capacidades_autorizadas,
)


def test_schema_seed_tipado():

    d = DecisaoAgenteLLM(
        decisao="teste",
        sementes_sugeridas=[
            "../fora.txt"
        ],
    )

    assert (
        d.sementes_sugeridas
        == ["../fora.txt"]
    )


def test_nul_rejeitado():

    r = validar_sementes_cognitivas(
        [
            "../x\x00.txt"
        ]
    )

    assert not r[
        "sementes_validas"
    ]


def test_tamanho_rejeitado():

    r = validar_sementes_cognitivas(
        [
            "A" * 513
        ]
    )

    assert not r[
        "sementes_validas"
    ]


def test_maximo_16():

    r = validar_sementes_cognitivas(
        [
            f"s-{x}"
            for x in range(20)
        ]
    )

    assert len(
        r["sementes_validas"]
    ) == 16


def test_deduplicacao():

    r = validar_sementes_cognitivas(
        [
            "../x",
            "../x",
        ]
    )

    assert r[
        "sementes_validas"
    ] == [
        "../x"
    ]


def test_texto_livre_nao_vira_seed():

    decisoes = [
        (
            "planejador",
            {
                "decisao": (
                    "../../nao.txt"
                ),
                "observacoes": [
                    "../tambem-nao.txt"
                ],
                "sementes_sugeridas": [],
            },
        )
    ]

    seeds, _ = (
        extrair_sementes_tipadas(
            decisoes
        )
    )

    assert seeds == ()


def test_campo_tipado_vira_seed():

    decisoes = [
        (
            "planejador",
            {
                "decisao": "texto",
                "sementes_sugeridas": [
                    "../sim.txt"
                ],
            },
        )
    ]

    seeds, _ = (
        extrair_sementes_tipadas(
            decisoes
        )
    )

    assert seeds == (
        "../sim.txt",
    )


def test_tipo_plano_preservado():

    plano = construir_plano_aquisicao(
        decisoes_por_agente=[
            (
                "planejador",
                {
                    "ferramentas_sugeridas": [
                        "path_traversal"
                    ]
                },
            )
        ],
        capacidades_registradas={
            "path_traversal"
        },
        capacidades_autorizadas={
            "path_traversal"
        },
        execucao_dinamica_permitida=True,
    )

    novo = aplicar_sementes_ao_plano(
        plano,
        sementes=(
            "../fora.txt",
        ),
        capacidades_autorizadas={
            "path_traversal"
        },
    )

    assert type(novo) is type(plano)

    assert hasattr(
        novo,
        "model_dump",
    )


def test_seed_nao_autoriza_dinamica():

    with tempfile.TemporaryDirectory() as td:

        arquivo = Path(td) / "x.py"

        arquivo.write_text(
            "print('x')\n",
            encoding="utf-8",
        )

        achado = AchadoMultiagente(
            id="M26B",
            arquivo=str(arquivo),
            sementes=[
                "../fora.txt"
            ],
            execucao_dinamica_permitida=False,
        )

        politica = (
            calcular_capacidades_autorizadas(
                achado=achado
            )
        )

        assert "path_traversal" not in (
            politica.capacidades_autorizadas
        )


def test_seed_controlada_com_sandbox():

    with tempfile.TemporaryDirectory() as td:

        raiz = Path(td)

        sandbox = raiz / "sandbox"
        sandbox.mkdir()

        arquivo = raiz / "x.py"

        arquivo.write_text(
            "print('x')\n",
            encoding="utf-8",
        )

        achado = AchadoMultiagente(
            id="M26B-PATH",
            arquivo=str(arquivo),
            sementes=[
                "../fora.txt"
            ],
            execucao_dinamica_permitida=True,
            raiz_sandbox=str(sandbox),
            max_iteracoes=3,
        )

        politica = (
            calcular_capacidades_autorizadas(
                achado=achado
            )
        )

        assert "path_traversal" in (
            politica.capacidades_autorizadas
        )
