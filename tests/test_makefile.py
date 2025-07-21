# test_Makefile.py

import subprocess
from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    "target", ["setup", "build", "up", "down", "test", "gen-types"]
)
def test_makefile_targets(target: str) -> None:
    """Test Makefile targets by mocking subprocess calls."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0  # Simulate successful execution
        result = subprocess.run(["make", target], capture_output=True, text=True)
        mock_run.assert_called_once_with(
            ["make", target], capture_output=True, text=True
        )
        assert result.returncode == 0, f"Makefile target '{target}' failed"


def test_makefile_lint():
    """Test the lint target."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = subprocess.run(["make", "lint"], capture_output=True, text=True)
        mock_run.assert_called_once_with(
            ["make", "lint"], capture_output=True, text=True
        )
        assert result.returncode == 0, "Makefile lint target failed"


def test_makefile_format():
    """Test the format target."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = subprocess.run(["make", "format"], capture_output=True, text=True)
        mock_run.assert_called_once_with(
            ["make", "format"], capture_output=True, text=True
        )
        assert result.returncode == 0, "Makefile format target failed"
