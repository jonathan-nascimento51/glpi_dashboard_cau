import os
import subprocess
from pathlib import Path


def _run_script(tmp_path: Path, exit_code: int) -> subprocess.CompletedProcess[str]:
    curl_path = tmp_path / "curl"
    curl_path.write_text("#!/bin/sh\nexit {}\n".format(exit_code))
    curl_path.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    return subprocess.run(
        ["scripts/check_snyk_access.sh"],
        capture_output=True,
        text=True,
        env=env,
    )


def test_snyk_access_success(tmp_path: Path) -> None:
    result = _run_script(tmp_path, 0)
    assert result.returncode == 0
    assert "Connectivity" in result.stdout


def test_snyk_access_failure(tmp_path: Path) -> None:
    result = _run_script(tmp_path, 1)
    assert result.returncode == 1
    assert "Unable" in result.stderr
