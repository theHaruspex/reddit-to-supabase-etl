from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("reddit-researcher: hello")
        return 0
    if argv and argv[0] in {"-h", "--help"}:
        print("Usage: reddit-researcher [name]")
        return 0
    name = argv[0]
    print(f"hello, {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
