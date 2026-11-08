import json
import requests

from aplicacao.ia.contratos import EntradaIA, SaidaIA


class ProvedorIA:
    def __init__(
        self,
        provedor: str,
        modelo: str,
        gemini_api_key: str = "",
        openai_api_key: str = "",
        ollama_url: str = "http://localhost:11434",
    ):
        self.provedor = provedor.lower().strip()
        self.modelo = modelo
        self.gemini_api_key = gemini_api_key
        self.openai_api_key = openai_api_key
        self.ollama_url = ollama_url.rstrip("/")

    def executar(self, entrada: EntradaIA) -> SaidaIA:
        if self.provedor == "gemini":
            return self._executar_gemini(entrada)

        if self.provedor == "openai":
            return self._executar_openai(entrada)

        if self.provedor == "ollama":
            return self._executar_ollama(entrada)

        raise ValueError(f"Provedor de IA inválido: {self.provedor}")

    def _prompt_base(self, entrada: EntradaIA) -> str:
        return json.dumps(
            {
                "instrucao": "Responda somente JSON válido no contrato: classificacao, confianca, justificativa, evidencias, recomendacoes.",
                "entrada": entrada.model_dump(),
            },
            ensure_ascii=False,
        )

    def _normalizar_saida(self, texto: str) -> SaidaIA:
        texto = texto.strip()

        if texto.startswith("```json"):
            texto = texto.removeprefix("```json").removesuffix("```").strip()
        elif texto.startswith("```"):
            texto = texto.removeprefix("```").removesuffix("```").strip()

        dados = json.loads(texto)

        dados["provedor"] = self.provedor
        dados["modelo"] = self.modelo

        return SaidaIA(**dados)

    def _executar_gemini(self, entrada: EntradaIA) -> SaidaIA:
        from google import genai

        cliente = genai.Client(api_key=self.gemini_api_key)

        resposta = cliente.models.generate_content(
            model=self.modelo,
            contents=self._prompt_base(entrada),
        )

        return self._normalizar_saida(resposta.text)

    def _executar_openai(self, entrada: EntradaIA) -> SaidaIA:
        from openai import OpenAI

        cliente = OpenAI(api_key=self.openai_api_key)

        resposta = cliente.responses.create(
            model=self.modelo,
            input=self._prompt_base(entrada),
        )

        return self._normalizar_saida(resposta.output_text)

    def _executar_ollama(self, entrada: EntradaIA) -> SaidaIA:
        resposta = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.modelo,
                "prompt": self._prompt_base(entrada),
                "stream": False,
            },
            timeout=120,
        )

        resposta.raise_for_status()

        texto = resposta.json()["response"]

        return self._normalizar_saida(texto)
