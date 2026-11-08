from aplicacao.llm.runtime_local import (
    carregar_configuracao_runtime_local,
    criar_provedor_runtime_local,
)


def test_runtime_config_real():
    cfg = carregar_configuracao_runtime_local()

    assert cfg.modelo == "veritassec-local"
    assert cfg.container_ip


def test_runtime_provedor_local():
    provedor = criar_provedor_runtime_local()

    assert provedor.escopo == "local"
    assert provedor.modelo == "veritassec-local"
