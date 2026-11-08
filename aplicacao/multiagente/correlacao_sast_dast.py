"""Correlação conservadora e rastreável SAST/SARIF ↔ ZAP/DAST.
Não altera classificação, veredito ou dados de origem.
"""
from __future__ import annotations
import hashlib
import json
import re
from urllib.parse import urlsplit

CAMPOS_SENSIVEIS = {'evidence', 'attack', 'request', 'response', 'cookie', 'authorization', 'apikey', 'password', 'token'}

def _categoria(texto):
    if not isinstance(texto, str): return None
    m = re.search(r'(?i)\bCWE[-_ ]?(\d{1,5})\b', texto)
    return 'CWE-' + str(int(m.group(1))) if m else None

def _url(valor):
    if not isinstance(valor, str): return None
    try:
        u=urlsplit(valor)
        if u.scheme not in ('http','https') or not u.hostname: return None
        return {'origem': u.scheme.lower()+'://'+u.netloc.lower(), 'caminho': u.path or '/'}
    except ValueError:
        return None

def _normalizar_sarif(obj):
    if isinstance(obj, dict) and isinstance(obj.get('runs'), list):
        return obj
    if isinstance(obj, dict):
        for chave in ('sarif','resultado_sarif','relatorio_sarif','dados_sarif'):
            valor=obj.get(chave)
            if isinstance(valor, dict) and isinstance(valor.get('runs'), list): return valor
    return None

def _achados_sarif(obj):
    sarif=_normalizar_sarif(obj)
    if sarif is None: return [], False
    saida=[]
    for indice_run, run in enumerate(sarif['runs']):
        if not isinstance(run, dict): continue
        regras={r.get('id'):r for r in run.get('tool',{}).get('driver',{}).get('rules',[]) if isinstance(r,dict)}
        for indice, r in enumerate(run.get('results',[])):
            if not isinstance(r,dict): continue
            rid=r.get('ruleId')
            regra=regras.get(rid,{})
            tags=regra.get('properties',{}).get('tags',[])
            cats=[_categoria(str(x)) for x in tags if isinstance(x,str)]
            for texto in (rid, regra.get('name'), regra.get('shortDescription',{}).get('text')):
                cats.append(_categoria(texto))
            categoria=next((c for c in cats if c),None)
            props=r.get('properties') or {}
            urls=[]
            for chave in ('url','endpoint','uri','requestUrl'):
                u=_url(props.get(chave))
                if u: urls.append(u)
            metodo=props.get('httpMethod') or props.get('method')
            parametro=props.get('parameter') or props.get('param')
            saida.append({'id':str(r.get('guid') or f'{indice_run}:{indice}:{rid or "sem-regra"}'),
                          'regra':str(rid or ''),'categoria':categoria,
                          'urls':urls,'metodo':str(metodo).upper() if isinstance(metodo,str) else None,
                          'parametro':str(parametro) if isinstance(parametro,str) else None})
    return saida, True

def _alertas_zap(alertas):
    saida=[]
    for i,a in enumerate(alertas):
        if not isinstance(a,dict): continue
        url=_url(a.get('url'))
        cat=_categoria(str(a.get('cweid') or a.get('cweId') or ''))
        if cat is None:
            cwe=a.get('cweid') or a.get('cweId')
            if str(cwe).isdigit() and int(cwe)>0: cat='CWE-'+str(int(cwe))
        metodo=a.get('method') or a.get('httpMethod')
        parametro=a.get('param') or a.get('parameter')
        saida.append({'id':str(a.get('id') or a.get('alertRef') or i),
                      'categoria':cat,'url':url,
                      'metodo':str(metodo).upper() if isinstance(metodo,str) else None,
                      'parametro':str(parametro) if isinstance(parametro,str) and parametro else None})
    return saida

def correlacionar(resultado, alertas):
    """Somente dados estruturados e identidade de endpoint/categoria justificam vínculos."""
    achados, disponivel=_achados_sarif(resultado)
    dast=_alertas_zap(alertas)
    vinculos=[]
    for s in achados:
        for d in dast:
            fatores=[]
            urls=s['urls']
            mesmo_endpoint=bool(d['url'] and any(u==d['url'] for u in urls))
            if mesmo_endpoint: fatores.append('origem_e_caminho')
            mesma_categoria=bool(s['categoria'] and s['categoria']==d['categoria'])
            if mesma_categoria: fatores.append('cwe')
            metodo=bool(s['metodo'] and d['metodo'] and s['metodo']==d['metodo'])
            if metodo: fatores.append('metodo_http')
            parametro=bool(s['parametro'] and d['parametro'] and s['parametro']==d['parametro'])
            if parametro: fatores.append('parametro')
            # Nenhuma correspondência apenas por CWE: risco de falso vínculo.
            if not mesmo_endpoint: continue
            # Método e parâmetro contraditórios impedem correspondência confirmada.
            contradicao=bool((s['metodo'] and d['metodo'] and not metodo) or
                             (s['parametro'] and d['parametro'] and not parametro) or
                             (s['categoria'] and d['categoria'] and not mesma_categoria))
            confirmado=(mesma_categoria and not contradicao and (metodo or parametro))
            nivel='CONFIRMADA' if confirmado else 'POSSIVEL'
            vinculos.append({'sarif_id':s['id'],'zap_id':d['id'],
                             'nivel':nivel,'criterios':fatores})
    return {'estado':'AVALIADA' if disponivel else 'SARIF_ESTRUTURADO_INDISPONIVEL',
            'achados_sarif_avaliados':len(achados),'alertas_zap_avaliados':len(dast),
            'correspondencias_confirmadas':sum(x['nivel']=='CONFIRMADA' for x in vinculos),
            'correspondencias_possiveis':sum(x['nivel']=='POSSIVEL' for x in vinculos),
            'achados_sem_correspondencia':sum(not any(v['sarif_id']==s['id'] for v in vinculos) for s in achados),
            'vinculos':vinculos,
            'ressalva':'Correlação por metadados não prova explorabilidade nem modifica TP/FP.'}
