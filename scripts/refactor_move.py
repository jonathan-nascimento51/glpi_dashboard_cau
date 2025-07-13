import sys

from rope.base.project import Project
from rope.refactor.move import Move


def main(project_root: str, old_path: str, new_path: str) -> None:
    project = Project(project_root)
    resource_to_move = project.get_resource(old_path)
    move_refactoring = Move(project, resource_to_move)
    changes = move_refactoring.get_changes(project.get_resource(new_path))
    project.do(changes)
    print(
        (
            f"Refatoração concluída: '{old_path}' movido para '{new_path}' "
            "e importações atualizadas."
        )
    )
    project.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Uso: python scripts/refactor_move.py <project_root> <old_path> <new_path>"
        )
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
