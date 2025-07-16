#!/usr/bin/env python
"""Generate a prompt summarizing recent errors and warnings."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from prompt_config import PromptConfig

# This line adds the 'src' directory to the Python path automatically
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))


CONFIG = PromptConfig()


def run_command(cmd: list[str]) -> str:
    """Run a command and return its output (stdout + stderr)."""
    # Ensure Python scripts run cross-platform
    # Use the current Python interpreter to run modules for consistency
    if cmd[0] in {"pytest", "flake8"}:
        cmd = [sys.executable, "-m", *cmd]
    # For scripts, ensure they are run with the correct interpreter
    # This logic is already good.
    elif cmd[0].endswith(".py"):
        cmd = [sys.executable, *cmd]
    try:
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return f"Command not found: {' '.join(cmd)}\n"
    return completed.stdout


def build_prompt(logs: dict[str, str]) -> str:
    """Construct the bug fix prompt from log data."""
    sections = [
        "# Identidade",
        "Você é um assistente de depuração para o projeto GLPI Dashboard.",
        "",
        "## Instruções",
        (
            "Analise os erros abaixo e sugira correções de código "
            "mantendo o estilo do projeto."
        ),
        "",
        "## Erros e avisos",
    ]
    for name, output in logs.items():
        sections.append(f"### {name}\n```\n{output}\n```")
    sections.append("## Ação\nForneça um plano de correção passo a passo.")
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=CONFIG.prompts_dir / "bug_prompt.md",
        help="Opcional: arquivo para salvar o prompt gerado",
    )
    args = parser.parse_args()

    CONFIG.ensure_dirs()

    logs = {
        "pytest": run_command(["pytest", "-q"]),
        "flake8": run_command(["flake8"]),
        "merge_conflicts": run_command(["scripts/check_merge_conflicts.py"]),
    }

    prompt = build_prompt(logs)
    if args.output:
        args.output.write_text(prompt, encoding="utf-8")
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
