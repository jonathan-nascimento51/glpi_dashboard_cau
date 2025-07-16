"""Interactive CLI to suggest asyncio strategies."""

from __future__ import annotations

import click


def suggest(interactive: bool, flask_dash: bool, recursive_run: bool) -> list[str]:
    """Return a list of strategy suggestions based on answers."""
    suggestions: list[str] = []
    if interactive:
        suggestions.append(
            "Ambiente interativo detectado: use nest_asyncio apenas para testes"
        )
    if flask_dash:
        suggestions.append(
            "Para apps Flask/Dash considere migrar para ASGI "
            "(FastAPI + Uvicorn) ou usar run_in_executor para trechos bloqueantes"
        )
    if recursive_run:
        suggestions.append(
            "Evite chamadas recursivas de asyncio.run; "
            "refatore usando await ou asyncio.create_task"
        )
    if not suggestions:
        suggestions.append("Nenhum ajuste específico necessário")
    return suggestions


@click.command()
def main() -> None:
    """Ask questions and output the recommended asyncio strategy."""
    interactive = click.confirm(
        "Executa em ambiente interativo (Jupyter)?", default=False
    )
    flask_dash = click.confirm("Usa Flask ou Dash?", default=False)
    recursive = click.confirm(
        "Suas funções chamam asyncio.run() de forma recursiva?", default=False
    )

    tips = suggest(interactive, flask_dash, recursive)

    click.echo("\nSugestões:")
    for tip in tips:
        click.echo(f"- {tip}")


if __name__ == "__main__":  # pragma: no cover
    main()
