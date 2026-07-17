"""
Walking Simulator: Тени Старого Дома
Точка входа — запускает актуальную версию игры.
"""
from pathlib import Path
import runpy

GAME_FILE = Path(__file__).with_name("main2_grok_v1.6.py")


def main():
    if not GAME_FILE.is_file():
        raise SystemExit(f"Не найден файл игры: {GAME_FILE.name}")
    runpy.run_path(str(GAME_FILE), run_name="__main__")


if __name__ == "__main__":
    main()
