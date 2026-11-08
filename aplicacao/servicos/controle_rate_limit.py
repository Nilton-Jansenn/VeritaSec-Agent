import random
import time
from threading import BoundedSemaphore
from typing import Callable, TypeVar

T = TypeVar("T")


def erro_eh_transitorio_ou_rate_limit(exc: Exception) -> bool:
    """
    Retorna True quando a exceção indica indisponibilidade temporária,
    quota/rate-limit, timeout ou erro transitório de rede/serviço.
    """
    texto = str(exc).lower()

    sinais = [
        # Rate limit / quota
        "429",
        "too many requests",
        "rate limit",
        "rate-limits",
        "insufficient_quota",
        "quota exceeded",
        "resource exhausted",
        "resource_exhausted",
        "you exceeded your current quota",
        "retrydelay",

        # Timeout / rede
        "timeout",
        "timed out",
        "connection refused",
        "failed to establish a new connection",
        "max retries exceeded",
        "connection reset",
        "network",

        # Serviço temporariamente indisponível
        "502",
        "503",
        "504",
        "service unavailable",
        "temporarily unavailable",
        "internal server error",
        "bad gateway",
        "gateway timeout",
    ]

    return any(sinal in texto for sinal in sinais)


def executar_com_retry_e_backoff(
    nome_provedor: str,
    semaforo: BoundedSemaphore,
    funcao: Callable[[], T],
    max_tentativas: int = 4,
    atraso_base: float = 2.0,
    atraso_maximo: float = 20.0,
) -> T:
    """
    Executa uma função protegida por:
    - semáforo de concorrência;
    - retry com backoff exponencial + jitter.

    Observação:
    Esta função é síncrona porque o seu endpoint atual também é síncrono.
    """
    ultima_excecao = None

    with semaforo:
        for tentativa in range(max_tentativas):
            try:
                return funcao()

            except Exception as exc:
                ultima_excecao = exc

                # Se não for erro transitório/rate limit, não adianta insistir.
                if not erro_eh_transitorio_ou_rate_limit(exc):
                    raise

                # Se já é a última tentativa, não dorme.
                if tentativa == max_tentativas - 1:
                    break

                # Backoff exponencial + jitter
                espera = min(atraso_base * (2 ** tentativa), atraso_maximo) + random.uniform(0, 0.8)

                print(
                    f"[WARN] {nome_provedor} indisponível/rate-limit "
                    f"(tentativa {tentativa + 1}/{max_tentativas}). "
                    f"Aguardando {espera:.2f}s antes de tentar novamente."
                )

                time.sleep(espera)

    raise RuntimeError(
        f"{nome_provedor} falhou após {max_tentativas} tentativas. "
        f"Último erro: {str(ultima_excecao)}"
    ) from ultima_excecao