"""Entry point for `python -m digital_clone` (e.g. `python -m digital_clone doctor`)."""

import sys

from digital_clone.doctor import run_doctor


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] != "doctor":
        print("usage: python -m digital_clone doctor")
        return 2
    return run_doctor()


if __name__ == "__main__":
    sys.exit(main())
