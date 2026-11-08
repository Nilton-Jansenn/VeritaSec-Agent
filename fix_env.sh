#!/bin/bash

set -e

echo "=========================================="
echo "🚀 INICIANDO CORREÇÃO DO AMBIENTE"
echo "=========================================="

PROJECT_DIR=$(pwd)
VENV_DIR=".venv"

echo "📁 Diretório do projeto: $PROJECT_DIR"

# -----------------------------------------
# 1. Remover ambiente antigo
# -----------------------------------------
echo "🧹 Removendo ambiente virtual antigo..."
rm -rf $VENV_DIR

# -----------------------------------------
# 2. Criar novo ambiente virtual
# -----------------------------------------
echo "🐍 Criando novo ambiente virtual..."
python3 -m venv $VENV_DIR

# -----------------------------------------
# 3. Ativar ambiente
# -----------------------------------------
echo "⚡ Ativando ambiente..."
source $VENV_DIR/bin/activate

# -----------------------------------------
# 4. Atualizar pip e ferramentas
# -----------------------------------------
echo "⬆️ Atualizando pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

# -----------------------------------------
# 5. Instalar dependências
# -----------------------------------------
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando requirements.txt..."
    pip install -r requirements.txt || {
        echo "❌ ERRO no requirements.txt!"
        echo "👉 Tente rodar manualmente: pip install -r requirements.txt"
        exit 1
    }
else
    echo "⚠️ requirements.txt não encontrado!"
fi

# -----------------------------------------
# 6. Garantir FastAPI instalado
# -----------------------------------------
echo "🔍 Verificando FastAPI..."

python - <<EOF
try:
    import fastapi
    print("✅ FastAPI OK - versão:", fastapi.__version__)
except Exception as e:
    print("⚠️ FastAPI não encontrado, instalando...")
EOF

pip install "fastapi[standard]"

# -----------------------------------------
# 7. Validar import
# -----------------------------------------
echo "🧪 Testando import..."

python - <<EOF
import sys
import fastapi
print("Python:", sys.executable)
print("FastAPI:", fastapi.__version__)
EOF

# -----------------------------------------
# 8. Criar config VS Code
# -----------------------------------------
echo "⚙️ Configurando VS Code..."

mkdir -p .vscode

cat > .vscode/settings.json <<EOF
{
  "python.defaultInterpreterPath": "\${workspaceFolder}/.venv/bin/python",
  "python.analysis.exclude": [
    "**/.venv/**",
    "**/__pycache__/**"
  ],
  "files.exclude": {
    "**/.venv": true
  }
}
EOF

echo "✅ VS Code configurado"

# -----------------------------------------
# 9. Limpar cache Python
# -----------------------------------------
echo "🧹 Limpando __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# -----------------------------------------
# 10. Configurar Snyk
# -----------------------------------------
echo "🔐 Configurando Snyk..."

if command -v snyk &> /dev/null
then
    echo "👉 Snyk encontrado"

    snyk ignore --file-path='.venv' || true

    echo "🔍 Rodando análise Snyk Code..."
    snyk code test || true

    echo "📦 Rodando análise dependências..."
    snyk test || true
else
    echo "⚠️ Snyk não instalado. Pulei essa etapa."
fi

# -----------------------------------------
# 11. Verificação final
# -----------------------------------------
echo "=========================================="
echo "✅ AMBIENTE PRONTO!"
echo "=========================================="

echo ""
echo "👉 Próximos passos:"
echo "1. Abra o VS Code"
echo "2. Ctrl + Shift + P"
echo "3. Python: Select Interpreter"
echo "4. Escolha .venv/bin/python"
echo ""
echo "👉 Rodar API:"
echo "uvicorn aplicacao.main:app --reload"
