#!/bin/bash
# Script para iniciar refatoração assistida por IA

echo "🔧 Iniciando processo de refatoração..."

# Verifica estrutura (usa tree se disponível, senão usa find)
if command -v tree &> /dev/null
then
    tree src/
else
    echo "(tree não encontrado, usando find como alternativa...)"
    find src/ -type f
fi

echo ""
echo "✅ Siga os prompts em docs/PROMPTS.md"
echo "✅ Registre alterações em docs/REFACTOR_LOG.md"
