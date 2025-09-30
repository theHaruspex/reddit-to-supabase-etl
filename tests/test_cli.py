from __future__ import annotations

from reddit_researcher.cli.cli import main


def test_main_prints_hello(capsys) -> None:
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "reddit-researcher: hello" in captured.out
