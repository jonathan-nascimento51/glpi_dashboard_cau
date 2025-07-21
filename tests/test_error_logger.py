import json
import sys
from io import StringIO
from pathlib import Path

import pytest

import scripts.error_logger as error_logger


def test_read_error_text_from_arg(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    assert error_logger.read_error_text("oops") == "oops"


def test_read_error_text_from_stdin(monkeypatch: pytest.MonkeyPatch):
    stream = StringIO("stdin error")
    stream.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr(sys, "stdin", stream)

    assert error_logger.read_error_text(None) == "stdin error"


def test_read_error_text_no_input(monkeypatch: pytest.MonkeyPatch):
    stream = StringIO()
    stream.isatty = lambda: True  # type: ignore[method-assign]
    monkeypatch.setattr(sys, "stdin", stream)

    assert error_logger.read_error_text(None) == ""


def test_extract_metadata_with_stack():
    text = 'Traceback\n  File "foo.py", line 5, in <module>'
    meta = error_logger.extract_metadata(text, agent="codex")

    assert meta["file"] == "foo.py"
    assert meta["line"] == 5
    assert meta["language"] == "py"
    assert meta["agent"] == "codex"


def test_extract_metadata_without_stack():
    meta = error_logger.extract_metadata("no stack", agent=None)

    assert meta["file"] is None
    assert meta["line"] is None
    assert meta["language"] is None


def test_append_log_creates_and_appends(tmp_path: Path):
    log_file = tmp_path / "log.json"
    first: dict[str, object] = {"msg": "one"}

    error_logger.append_log(first, log_file)
    with log_file.open() as fh:
        data = json.load(fh)
    assert data == [first]

    second: dict[str, object] = {"msg": "two"}
    error_logger.append_log(second, log_file)
    with log_file.open() as fh:
        data = json.load(fh)
    assert data == [first, second]


def test_main_cli(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    log = tmp_path / "out.json"
    argv = [
        "error_logger.py",
        "--text",
        "boom",
        "--agent",
        "tester",
        "--logfile",
        str(log),
    ]

    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys, "argv", argv)
    rc = error_logger.main()
    captured = capsys.readouterr().out

    assert rc == 0
    assert "Logged error" in captured
    with log.open() as fh:
        data = json.load(fh)
    assert data[0]["stack"] == "boom"
    assert data[0]["agent"] == "tester"


def test_main_no_input_exits(
    monkeypatch: pytest.MonkeyPatch,
):
    """main() should exit with status 2 if no input is provided."""
    # Simulate no --text and an interactive terminal
    monkeypatch.setattr(sys, "argv", ["error_logger.py"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    with pytest.raises(SystemExit) as excinfo:
        error_logger.main()
    assert excinfo.value.code == 2
