# test_Makefile.py

import subprocess

import pytest

# Targets that are safe to execute directly in a test environment
SAFE_TARGETS = ["lint", "format", "test", "gen-types"]

# Targets that might have significant side-effects (e.g., Docker, installations)
# We will test these with a dry-run to ensure they are defined correctly.
DRY_RUN_TARGETS = ["setup", "build", "up", "down", "reset"]


@pytest.mark.parametrize("target", SAFE_TARGETS)
def test_safe_makefile_targets_execute(target: str) -> None:
    """
    Test safe Makefile targets by executing them and checking for a success exit code.
    These targets should not have major side-effects and be quick to run.
    """
    try:
        # Execute the make command for real
        subprocess.run(
            ["make", target],
            check=True,  # Raises CalledProcessError for non-zero exit codes
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        pytest.fail("`make` command not found. Is it installed and in the PATH?")
    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"Executing 'make {target}' failed with exit code {e.returncode}.\n"
            f"Stdout:\n{e.stdout}\n"
            f"Stderr:\n{e.stderr}"
        )


@pytest.mark.parametrize("target", DRY_RUN_TARGETS)
def test_complex_makefile_targets_dry_run(target: str) -> None:
    """
    Test complex or stateful Makefile targets using a dry-run (`make -n`).
    This verifies the target exists and its commands are valid without executing them.
    """
    try:
        # Execute the make command with the --dry-run flag
        result = subprocess.run(
            ["make", "-n", target],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        # A dry run should produce some output (the commands to be run)
        assert (
            result.stdout
        ), f"'make -n {target}' produced no output, which is unexpected."
    except FileNotFoundError:
        pytest.fail("`make` command not found. Is it installed and in the PATH?")
    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"Dry-run for 'make {target}' failed with exit code {e.returncode}.\n"
            f"This might indicate the target is not defined or has a syntax error.\n"
            f"Stderr:\n{e.stderr}"
        )
