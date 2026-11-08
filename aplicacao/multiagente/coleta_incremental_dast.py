"""Coleta incremental somente de alertas já existentes no ZAP; sem varredura ativa."""
from __future__ import annotations
import hashlib, json
from urllib.parse import urlsplit
import httpx
from aplicacao.multiagente.correlacao_dast import normalizar_alerta_zap, correlacionar, registrar_resultados

class ColetaDASTInvalida(ValueError): pass

def _origem(url):
    u=urlsplit(url)
    if u.scheme not in ('http','https') or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):
        raise ColetaDASTInvalida('URL_BASE_INVALIDA')
    return (u.scheme.lower(),u.hostname.lower(),u.port or (443 if u.scheme=='https' else 80))

def _chave(alerta):
    campos=[alerta.get(k,'') for k in ('pluginId','alertRef','url','param','method','evidence','messageId')]
    return hashlib.sha256(json.dumps(campos,ensure_ascii=False,sort_keys=True,default=str).encode()).hexdigest()

async def coletar_alertas_existentes(cliente_zap, url_base, autorizado, *, limite=500, pagina=100):
    """Consulta alertas existentes. Não invoca spider, activeScan ou accessUrl.
    A autorização aqui é necessária, mas não substitui a política de execução por achado.
    """
    if autorizado is not True: raise ColetaDASTInvalida('AUTORIZACAO_EXPLICITA_OBRIGATORIA')
    origem=_origem(url_base)

    import os

    base_aprovada = os.environ.get(
        "VERITASSEC_RUNTIME_LOCAL_BASE_URL",
        "",
    ).strip()
    if base_aprovada:

        if not base_aprovada:
            raise ColetaDASTInvalida(
                "RUNTIME_LOCAL_NAO_CONFIGURADO"
            )

        try:
            origem_aprovada = _origem(base_aprovada)
        except (ValueError, TypeError) as exc:
            raise ColetaDASTInvalida(
                "RUNTIME_LOCAL_INVALIDO"
            ) from exc

        if origem != origem_aprovada:
            raise ColetaDASTInvalida(
                "ALVO_FORA_DO_ESCOPO"
            )

    if not isinstance(limite,int) or isinstance(limite,bool) or not 1<=limite<=5000: raise ColetaDASTInvalida('LIMITE_INVALIDO')
    if not isinstance(pagina,int) or isinstance(pagina,bool) or not 1<=pagina<=500: raise ColetaDASTInvalida('PAGINA_INVALIDA')
    unicos={}
    async with httpx.AsyncClient(transport=cliente_zap.transport,trust_env=False,timeout=10.0) as http:
        for inicio in range(0,limite,pagina):
            quantidade=min(pagina,limite-inicio)
            resposta=await http.get(cliente_zap.zap_url+'/JSON/alert/view/alerts/',params=cliente_zap._params({'baseurl':url_base,'start':str(inicio),'count':str(quantidade)}))
            resposta.raise_for_status()
            dados=resposta.json()
            if not isinstance(dados,dict) or not isinstance(dados.get('alerts'),list): raise ColetaDASTInvalida('RESPOSTA_ZAP_INVALIDA')
            itens=dados['alerts']
            for item in itens:
                if not isinstance(item,dict): continue
                try:
                    if _origem_alerta(item.get('url',''))!=origem: continue
                except (ValueError,TypeError): continue
                unicos[_chave(item)]=normalizar_alerta_zap(item)
            if len(itens)<quantidade: break
    return list(unicos.values())

def _origem_alerta(url):
    u=urlsplit(url)
    if u.scheme not in ('http','https') or not u.hostname or u.username or u.password: raise ValueError('ORIGEM_INVALIDA')
    return (u.scheme.lower(),u.hostname.lower(),u.port or (443 if u.scheme=='https' else 80))

def correlacionar_e_registrar(destino,achados_sast,alertas_dast):
    achados=list(achados_sast)
    correlacoes=[]
    for alerta in alertas_dast:
        for achado in achados:
            resultado=correlacionar(achado,alerta)
            if resultado['correspondencia']: correlacoes.append(resultado)
    registrar_resultados(destino,alertas_dast,correlacoes)
    return {'alertas':len(alertas_dast),'correlacoes':len(correlacoes),'classificacao':'inconclusivo','investigacao_necessaria':True}
