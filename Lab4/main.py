import argparse

from app.application import MedicalAssistantApp, default_data_file
from app.cli import run_cli
from app.gui import run_gui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Персональный медицинский ассистент с поддержкой CLI и GUI"
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("cli", "gui"),
        default="cli",
        help="режим запуска приложения",
    )
    parser.add_argument(
        "--data-file",
        default=default_data_file(),
        help="путь к JSON-файлу с данными",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    app = MedicalAssistantApp(args.data_file)
    if args.mode == "gui":
        run_gui(app)
        return
    run_cli(app)


if __name__ == "__main__":
    main()
