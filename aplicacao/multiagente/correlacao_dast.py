"""Normalização e correlação conservadora SAST/DAST sem executar varreduras."""
from __future__ import annotations
from urllib.parse import urlsplit
import json, os, pathlib, tempfile

def normalizar_alerta_zap(alerta):
    if not isinstance(alerta,dict): raise TypeError('ALERTA_INVALIDO')
    campos={'origem':'DAST','ferramenta':'OWASP ZAP','regra':str(alerta.get('pluginId') or alerta.get('alertRef') or ''),
      'nome':str(alerta.get('alert') or alerta.get('name') or ''),'url':str(alerta.get('url') or ''),
      'metodo':str(alerta.get('method') or '').upper(),'parametro':str(alerta.get('param') or ''),
      'cwe':str(alerta.get('cweid') or ''),'risco':str(alerta.get('risk') or ''),
      'confianca':str(alerta.get('confidence') or ''),'evidencia':str(alerta.get('evidence') or ''),
      'mensagem':str(alerta.get('messageId') or '')}
    campos.update(classificacao='inconclusivo',investigacao_necessaria=True,
      justificativa='Alerta DAST ainda sem comprovação independente suficiente.')
    return campos

def correlacionar(achado,alerta):
    if not isinstance(achado,dict) or not isinstance(alerta,dict): raise TypeError('ACHADO_INVALIDO')
    cwe=lambda s:str(s or '').upper().removeprefix('CWE-')
    origem=urlsplit(alerta.get('url') or '')
    comparacoes={'endpoint':bool(achado.get('caminho_http') and achado['caminho_http']==origem.path),
      'metodo':bool(achado.get('metodo_http') and alerta.get('metodo') and achado['metodo_http'].upper()==alerta['metodo']),
      'cwe':bool(achado.get('cwe') and alerta.get('cwe') and cwe(achado['cwe'])==cwe(alerta['cwe']))}
    return {'id_sast':str(achado.get('id') or ''),'regra_dast':alerta.get('regra'),
      'comparacoes':comparacoes,'correspondencia':all(comparacoes.values()),
      'classificacao':'inconclusivo','investigacao_necessaria':True,
      'justificativa':'Correspondência de atributos não é comprovação da vulnerabilidade.'}

def registrar_resultados(destino,alertas,correlacoes):
    destino=pathlib.Path(destino);destino.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.dast-',dir=destino.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump({'esquema':'veritassec.dast.v1','alertas':list(alertas),
              'correlacoes':list(correlacoes)},f,ensure_ascii=False,indent=2)
            f.flush();os.fsync(f.fileno())
        os.chmod(tmp,0o600);os.replace(tmp,destino)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return destino


# VERITASSEC_ASSOCIACAO_CONTEXTUAL_ENDPOINT_V1
def associar_contexto_endpoint(achado, alerta):
    """
    Associação contextual, sem confirmar vulnerabilidade.

    Exige igualdade de endpoint e método HTTP.
    A CWE é registrada como informação complementar.
    """
    if not isinstance(achado, dict) or not isinstance(alerta, dict):
        raise TypeError("ACHADO_INVALIDO")

    from urllib.parse import urlsplit

    caminho = urlsplit(str(alerta.get("url") or "")).path

    metodo_sast = str(
        achado.get("metodo_http") or ""
    ).upper()

    metodo_dast = str(
        alerta.get("metodo") or ""
    ).upper()

    endpoint_igual = bool(
        achado.get("caminho_http")
        and achado["caminho_http"] == caminho
    )

    metodo_igual = bool(
        metodo_sast
        and metodo_dast
        and metodo_sast == metodo_dast
    )

    correlacao_original = correlacionar(
        achado,
        alerta,
    )

    return {
        "id_sast": str(achado.get("id") or ""),
        "regra_dast": alerta.get("regra"),
        "endpoint": caminho,
        "metodo": metodo_dast,
        "associacao_contextual": (
            endpoint_igual and metodo_igual
        ),
        "correlacao_vulnerabilidade": (
            correlacao_original["correspondencia"]
        ),
        "comparacoes": correlacao_original["comparacoes"],
        "classificacao": "inconclusivo",
        "investigacao_necessaria": True,
        "justificativa": (
            "Coincidencia de endpoint e metodo nao "
            "comprova a vulnerabilidade identificada pelo SAST."
        ),
    }
