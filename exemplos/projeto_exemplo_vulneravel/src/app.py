# Importa o Flask para construir uma API simples de exemplo.
from flask import Flask, request, jsonify

# Importa a função de acesso ao repositório.
from repositorio_usuario import buscar_usuario_por_identificador

# Importa a função de validação.
from validador_usuario import validar_identificador_usuario

# Cria a aplicação Flask.
app = Flask(__name__)


# Define a rota de consulta de usuário.
@app.route("/usuarios")
def obter_usuario():
    # Obtém o parâmetro "id" da URL.
    identificador_recebido = request.args.get("id", "")

    # Aplica validação forte antes de enviar ao repositório.
    identificador_validado = validar_identificador_usuario(identificador_recebido)

    # Chama a camada de repositório.
    resultado = buscar_usuario_por_identificador(identificador_validado)

    # Retorna o resultado.
    return jsonify(resultado)


# Executa a aplicação localmente.
if __name__ == "__main__":
    app.run(debug=True)
