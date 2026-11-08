# Importa o módulo logging.
import logging


# Configura o comportamento global de logs da aplicação.
def configurar_logs() -> None:
    # Define nível e formato padrão.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )