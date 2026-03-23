from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub


parent_dir = Path(__file__).parent


def create_translator_hub() -> TranslatorHub:
    translator_hub = TranslatorHub(
        {"ru": ("ru", "en"), "en": ("en",)},
        [
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=[parent_dir / "locales/ru/LC_MESSAGES/txt.ftl"],
                ),
            ),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=[parent_dir / "locales/en/LC_MESSAGES/txt.ftl"],
                ),
            ),
        ],
    )
    return translator_hub
