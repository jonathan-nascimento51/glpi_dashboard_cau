import shutil
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1] / "src"

# Mapeamento de arquivos: origem relativa -> destino relativa
# The repository no longer contains the legacy `glpi_dashboard` or `examples`
# directories referenced below. These mappings were used during the initial
# refactor to move files into the new `backend`, `frontend` and `shared`
# packages. All source files listed here have been deleted, so keeping them in
# the mapping only prints "file not found" messages.
mapping: dict[str, str] = {}


def ensure_dir(path):
    path.parent.mkdir(parents=True, exist_ok=True)


def move_file(src_rel, dst_rel):
    src = BASE_DIR / src_rel
    dst = BASE_DIR / dst_rel
    if not src.exists():
        print(f"❌ Arquivo não encontrado: {src_rel}")
        return
    ensure_dir(dst)
    shutil.move(str(src), str(dst))
    print(f"✅ {src_rel} → {dst_rel}")


if __name__ == "__main__":
    for src_rel, dst_rel in mapping.items():
        move_file(src_rel, dst_rel)
