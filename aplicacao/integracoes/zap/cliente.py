from __future__ import annotations

from urllib.parse import urljoin

import httpx

from aplicacao.http_runtime.modelos import (
    AlvoHttpAutorizado,
)
from aplicacao.http_runtime.politica import (
    validar_alvo,
)


class ClienteZap:
    """
    Adaptador mínimo para uma instância ZAP já iniciada.

    Esta classe não inicia containers, não executa shell
    e não inicia active scan.
    """

    def __init__(
        self,
        zap_url: str = "http://127.0.0.1:8090",
        api_key: str | None = None,
        transport: httpx.AsyncBaseTransport
        | None = None,
    ) -> None:

        self.zap_url = zap_url.rstrip("/")
        self.api_key = api_key if api_key is not None else self._chave_local()
        self.transport = transport

    @staticmethod
    def _chave_local() -> str | None:
        import os
        import re
        import stat
        from pathlib import Path

        valor = os.environ.get("VERITASSEC_ZAP_API_KEY")
        if valor:
            return valor
        arquivo = Path(os.environ.get("VERITASSEC_ZAP_KEY_FILE", ""))
        if not str(arquivo) or str(arquivo) == "." or not arquivo.is_file():
            arquivo = Path.home() / "Documentos/Projetos/VeritasSec-Agent/.veritassec-zap-key.env"
        if not arquivo.is_file():
            return None
        st = arquivo.stat()
        if st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o600:
            raise PermissionError("Arquivo de chave ZAP sem protecao 600")
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.startswith("VERITASSEC_ZAP_API_KEY="):
                valor = linha.split("=", 1)[1].strip()
                # O arquivo e gerado com printf %q; aceita chaves hexadecimais sem interpretacao de shell.
                if not re.fullmatch(r"[A-Za-z0-9_-]+", valor):
                    raise ValueError("Formato de chave ZAP nao suportado; nenhuma chave exibida")
                return valor
        return None

    def _params(
        self,
        extras: dict[str, str] | None = None,
    ) -> dict[str, str]:

        params = dict(
            extras or {}
        )

        if self.api_key:
            params["apikey"] = self.api_key

        return params

    async def versao(
        self,
    ) -> str:

        async with httpx.AsyncClient(
            transport=self.transport,
            trust_env=False,
            timeout=5.0,
        ) as client:

            resposta = await client.get(
                self.zap_url
                + "/JSON/core/view/version/",
                params=self._params(),
            )

        resposta.raise_for_status()

        dados = resposta.json()

        return str(
            dados["version"]
        )

    async def acessar_url_autorizada(
        self,
        alvo: AlvoHttpAutorizado,
        url: str,
    ) -> dict:

        validar_alvo(alvo)

        if not url.startswith(
            alvo.base_url.rstrip("/") + "/"
        ) and url != alvo.base_url.rstrip("/"):
            raise PermissionError(
                "URL fora do alvo autorizado"
            )

        async with httpx.AsyncClient(
            transport=self.transport,
            trust_env=False,
            timeout=10.0,
        ) as client:

            resposta = await client.get(
                self.zap_url
                + "/JSON/core/action/accessUrl/",
                params=self._params(
                    {
                        "url": url,
                        "followRedirects": "false",
                    }
                ),
            )

        resposta.raise_for_status()

        return resposta.json()
