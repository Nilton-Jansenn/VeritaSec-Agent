"""Integração DAST controlada ao retorno SARIF, sem inferir TP/FP."""
from __future__ import annotations
import ipaddress
import json
import os
import re
import subprocess
from urllib.parse import urlsplit

def _inspecionar(nome):
    p = subprocess.run(["docker", "inspect", nome], capture_output=True, text=True, timeout=20, check=True)
    return json.loads(p.stdout)[0]

def _contexto_local():
    zap = _inspecionar("veritassec-zap-local")
    juice = _inspecionar("veritassec-juice-shop-local")
    if not (zap["State"]["Running"] and juice["State"]["Running"]):
        raise RuntimeError("RUNTIME_LOCAL_INATIVO")
    redes_z = zap["NetworkSettings"]["Networks"]
    redes_j = juice["NetworkSettings"]["Networks"]
    ips = {redes_j[n]["IPAddress"] for n in redes_z.keys() & redes_j.keys() if redes_j[n].get("IPAddress")}
    if len(ips) != 1: raise RuntimeError("DESTINO_NAO_UNIVOCO")
    ip = ips.pop()
    if not ipaddress.ip_address(ip).is_private: raise RuntimeError("DESTINO_NAO_PRIVADO")
    portas_z = zap["NetworkSettings"].get("Ports") or {}
    if not any(v and any(x.get("HostIp") in ("127.0.0.1", "::1") and x.get("HostPort") == "8090" for x in v) for v in portas_z.values()):
        raise RuntimeError("ZAP_NAO_RESTRITO_LOOPBACK")
    chave = None
    for nome in ("VERITASSEC_ZAP_API_KEY", "ZAP_API_KEY", "ZAP_APIKEY"):
        if os.environ.get(nome): chave = os.environ[nome]; break
    if not chave:
        for item in zap["Config"].get("Env", []) or []:
            nome, sep, valor = item.partition("=")
            if sep and nome in ("VERITASSEC_ZAP_API_KEY", "ZAP_API_KEY", "ZAP_APIKEY") and valor:
                chave = valor; break
    if not chave:
        args = (zap["Config"].get("Entrypoint") or []) + (zap["Config"].get("Cmd") or [])
        m = re.search(r"api\.key\s*=\s*([^\s\"';]+)", " ".join(args))
        if m: chave = m.group(1)
    if not chave: raise RuntimeError("CHAVE_ZAP_NAO_LOCALIZADA")
    return "http://" + ip + ":3000/", chave

def enriquecer_resultado_sarif(resultado):
    if not isinstance(resultado, dict): raise TypeError("RESULTADO_SARIF_INVALIDO")
    from .execucao_dast_controlada import executar
    alvo, chave = _contexto_local()
    execucao = executar(zap_url="http://127.0.0.1:8090", alvo_url=alvo, chave_api=chave, autorizado=True)
    confirmado = execucao.get("acesso_confirmado") is True
    if not confirmado: raise RuntimeError("ACESSO_DAST_NAO_CONFIRMADO")
    resumo = {"origem": "ZAP_LOCAL", "alvo": alvo, "acesso_confirmado": True,
              "versao_zap": execucao.get("zap_version"), "alertas_origem": execucao.get("alertas_origem"),
              "correlacao_sast_dast": "NAO_DETERMINADA",
              "observacao": "Alertas por origem nao comprovam correspondencia com achados SARIF nem TP/FP."}
    saida = dict(resultado)
    saida["integracao_dast"] = resumo
    return saida


# VERITASSEC_ETAPA05_CORRELACAO
_vs_etapa05_enriquecer_original = enriquecer_resultado_sarif

def enriquecer_resultado_sarif(resultado):
    import json as _json
    import urllib.parse as _parse
    import urllib.request as _request
    from .correlacao_sast_dast import correlacionar, _normalizar_sarif
    enriquecido = _vs_etapa05_enriquecer_original(resultado)
    # Sem achados SARIF estruturados não há vínculo verificável.
    # Evita acesso de rede nos testes de preservação de veredito.
    if _normalizar_sarif(resultado) is None:
        saida = dict(enriquecido)
        saida['correlacao_sast_dast'] = correlacionar(resultado, [])
        return saida
    alvo, chave = _contexto_local()
    parametros = _parse.urlencode({'apikey': chave, 'baseurl': alvo, 'start': 0, 'count': 1000})
    url = 'http://127.0.0.1:8090/JSON/core/view/alerts/?' + parametros
    try:
        with _request.urlopen(url, timeout=25) as resposta:
            dados = _json.loads(resposta.read(4_000_000))
        if not isinstance(dados, dict) or not isinstance(dados.get('alerts'), list):
            raise RuntimeError('CONTRATO_ALERTAS_ZAP_INVALIDO')
        alertas = dados['alerts']
        # Restringe à mesma origem do alvo, sem persistir parâmetros de consulta.
        from urllib.parse import urlsplit as _split
        origem = _split(alvo).netloc.lower()
        alertas = [a for a in alertas if isinstance(a, dict) and
                   isinstance(a.get('url'), str) and _split(a['url']).netloc.lower() == origem]
        correlacao = correlacionar(resultado, alertas)
    except Exception as erro:
        # Nunca expor a URL com a chave de API em mensagens ou logs.
        raise RuntimeError('COLETA_CORRELACAO_ZAP_FALHOU:' + type(erro).__name__) from None
    saida = dict(enriquecido)
    saida['correlacao_sast_dast'] = correlacao
    # VERITASSEC_FASE09_CONTRATO_SARIF
    from aplicacao.multiagente.integracao_semantica_dast import integrar as _vs_integrar_semantica
    saida['correlacao_semantica_http'] = _vs_integrar_semantica(resultado, alertas)
    return saida
