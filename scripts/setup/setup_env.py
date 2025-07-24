import shutil
import sys
from pathlib import Path

# Determina a raiz do projeto em relação à localização deste script
# scripts/setup/setup_env.py -> ../../.. -> raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_env(
    example: Path = PROJECT_ROOT / ".env.example",
    target: Path = PROJECT_ROOT / ".env",
) -> None:
    """Create a local .env by copying from an example file if not present."""
    if target.exists():
        print(
            f"✅ O arquivo {target.relative_to(PROJECT_ROOT)} já existe. Nenhuma ação "
            "necessária."
        )
        return
    if not example.exists():
        print(
            f"❌ ERRO: O arquivo de exemplo '{example.relative_to(PROJECT_ROOT)}' "
            "não foi encontrado.",
            file=sys.stderr,
        )
        print(
            "   Por favor, restaure ou crie este arquivo antes de continuar.",
            file=sys.stderr,
        )
        sys.exit(1)

    shutil.copy(example, target)
    print(
        f"✅ Criado {target.relative_to(PROJECT_ROOT)} a partir de "
        f"{example.relative_to(PROJECT_ROOT)}."
    )
    print("   ➡️  Por favor, edite o arquivo .env com suas credenciais do GLPI.")


if __name__ == "__main__":
    create_env()
