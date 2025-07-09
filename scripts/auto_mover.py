import shutil
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1] / "src"

# Mapeamento de arquivos: origem relativa -> destino relativa
mapping = {
    "api/__init__.py": "backend/api/__init__.py",
    "glpi_dashboard/acl/dto.py": "backend/adapters/dto.py",
    "glpi_dashboard/acl/mapping_service.py": "backend/adapters/mapping_service.py",
    "glpi_dashboard/acl/normalization.py": "backend/adapters/normalization.py",
    "glpi_dashboard/acl/ticket_models.py": "backend/models/ticket_models.py",
    "glpi_dashboard/cache.py": "backend/utils/cache.py",
    "glpi_dashboard/cli/tickets_groups.py": "backend/core/tickets_groups.py",
    "glpi_dashboard/config/settings.py": "backend/core/settings.py",
    "glpi_dashboard/dashboard/callbacks.py": "frontend/callbacks/callbacks.py",
    "glpi_dashboard/dashboard/components.py": "frontend/components/components.py",
    "glpi_dashboard/dashboard/layout.py": "frontend/layout/layout.py",
    "glpi_dashboard/data/database.py": "backend/db/database.py",
    "glpi_dashboard/data/transform.py": "backend/utils/transform.py",
    "glpi_dashboard/events/consumer.py": "backend/services/events_consumer.py",
    "glpi_dashboard/glpi_adapter.py": "backend/adapters/glpi_adapter.py",
    "glpi_dashboard/services/aggregated_metrics.py": "backend/services/aggregated_metrics.py",
    "glpi_dashboard/services/langgraph_workflow.py": "backend/services/langgraph_workflow.py",
    "glpi_dashboard/services/worker_api.py": "backend/api/worker_api.py",
    "glpi_dashboard/utils/redis_client.py": "backend/utils/redis_client.py",
    "examples/resilience/retry_decorator.py": "shared/utils/resilience/retry_decorator.py",
    "examples/order_observer.py": "shared/order_observer.py",
}


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
