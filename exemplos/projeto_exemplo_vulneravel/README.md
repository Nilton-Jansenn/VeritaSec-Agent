# Projeto de Exemplo do VeritasSec

Este exemplo foi criado para validar o comportamento do VeritasSec em um caso onde:

- uma ferramenta SAST pode apontar possível SQL Injection;
- porém o contexto multicamadas mostra validação forte anterior;
- a IA precisa diferenciar:
  - explorabilidade real;
  - falso positivo;
  - recomendação por defesa em profundidade.

## Arquivos

- `src/app.py`
- `src/validador_usuario.py`
- `src/repositorio_usuario.py`
