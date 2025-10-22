#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict

try:
    from pydub import AudioSegment
    from pydub.exceptions import CouldntDecodeError
except Exception as e:  # pydub може бути не встановлений
    AudioSegment = None  # type: ignore[assignment]
    CouldntDecodeError = Exception  # type: ignore[assignment]
    _PYDUB_IMPORT_ERROR = e
else:
    _PYDUB_IMPORT_ERROR = None

try:
    from mutagen import File as MutagenFile
except Exception as e:  # mutagen може бути не встановлений
    MutagenFile = None  # type: ignore[assignment]
    _MUTAGEN_IMPORT_ERROR = e
else:
    _MUTAGEN_IMPORT_ERROR = None


SUPPORTED_EXTS = {"mp3", "wav"}


def is_supported_media(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower().lstrip(".") in SUPPORTED_EXTS


def get_duration_seconds(path: str) -> float:
    if AudioSegment is None:
        raise RuntimeError(
            "Бібліотеку pydub не знайдено. Встановіть її: pip install pydub"
        ) from _PYDUB_IMPORT_ERROR

    ext = os.path.splitext(path)[1].lower().lstrip(".")
    try:
        audio = AudioSegment.from_file(path, format=ext)
    except CouldntDecodeError as e:
        raise RuntimeError(
            "Не вдалося декодувати файл через pydub/ffmpeg. "
            "Переконайтесь, що FFmpeg встановлено та додано до PATH."
        ) from e

    # pydub повертає довжину в мс
    return len(audio) / 1000.0


def get_metadata(path: str) -> Dict[str, str]:
    if MutagenFile is None:
        raise RuntimeError(
            "Бібліотеку mutagen не знайдено. Встановіть її: pip install mutagen"
        ) from _MUTAGEN_IMPORT_ERROR

    tags_out: Dict[str, str] = {}

    # Спочатку пробуємо спрощене представлення тегів
    mf_easy = MutagenFile(path, easy=True)
    if mf_easy is not None and getattr(mf_easy, "tags", None):
        for k, v in mf_easy.tags.items():  # type: ignore[union-attr]
            if isinstance(v, (list, tuple)):
                tags_out[k] = ", ".join(str(x) for x in v)
            else:
                tags_out[k] = str(v)

    # Якщо спрощені теги відсутні — пробуємо повні теги
    if not tags_out:
        mf_full = MutagenFile(path)
        if mf_full is not None and getattr(mf_full, "tags", None):
            try:
                items = mf_full.tags.items()  # type: ignore[union-attr]
            except Exception:
                items = []
            for k, v in items:
                val: str
                # Деякі фрейми мають атрибут .text (ID3 TextFrame)
                text = getattr(v, "text", None)
                if isinstance(text, (list, tuple)):
                    val = ", ".join(str(x) for x in text)
                else:
                    val = str(v)
                tags_out[str(k)] = val

    return tags_out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Перевіряє .mp3/.wav файл і виводить тривалість та метадані"
        )
    )
    parser.add_argument("path", help="Шлях до аудіофайла (.mp3 або .wav)")
    args = parser.parse_args(argv)

    path = args.path
    if not os.path.isfile(path):
        print(f"Помилка: файл не знайдено — {path}")
        return 1

    if not is_supported_media(path):
        print("Непідтримуваний формат. Дозволено лише .mp3 та .wav")
        return 2

    print(f"Файл: {path}")
    print(f"Формат: {os.path.splitext(path)[1].lower().lstrip('.')}")

    try:
        duration = get_duration_seconds(path)
    except Exception as e:
        print(f"Помилка при обчисленні тривалості: {e}")
        return 3

    print(f"Тривалість: {duration:.3f} c")

    try:
        md = get_metadata(path)
    except Exception as e:
        print(f"Не вдалося прочитати метадані: {e}")
        return 0

    if md:
        print("Метадані:")
        for k in sorted(md.keys()):
            print(f"  - {k}: {md[k]}")
    else:
        print("Метадані відсутні або не підтримуються для цього файла.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

