import argparse

from app.application import MedicalAssistantApp, default_data_file
from app.cli import run_cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Персональный медицинский ассистент с поддержкой CLI и web"
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("cli", "web"),
        default="web",
        help="режим запуска приложения",
    )
    parser.add_argument(
        "--data-file",
        default=default_data_file(),
        help="путь к JSON-файлу с данными",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="хост для запуска веб-приложения",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="порт для запуска веб-приложения",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    app = MedicalAssistantApp(args.data_file)
    if args.mode == "web":
        from app.web import run_web

        run_web(app, host=args.host, port=args.port)
        return
    run_cli(app)


if __name__ == "__main__":
    main()
