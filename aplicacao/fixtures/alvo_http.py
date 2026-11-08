from __future__ import annotations

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
)


def criar_fixture_segura() -> FastAPI:

    app = FastAPI()

    @app.get("/recurso/42")
    def recurso(
        x_identidade: str | None = Header(
            default=None
        ),
    ) -> dict:

        if x_identidade != "proprietario":
            raise HTTPException(
                status_code=403,
                detail="acesso negado",
            )

        return {
            "id": 42,
            "conteudo": "RECURSO_PROTEGIDO_42",
        }

    return app


def criar_fixture_vulneravel() -> FastAPI:
    """
    Fixture deliberadamente vulnerável usada
    exclusivamente nos testes automatizados.
    """

    app = FastAPI()

    @app.get("/recurso/42")
    def recurso() -> dict:
        return {
            "id": 42,
            "conteudo": "RECURSO_PROTEGIDO_42",
        }

    return app
