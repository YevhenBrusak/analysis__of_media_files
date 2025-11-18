import sys
import json
import os
from pathlib import Path

from PIL import Image, ExifTags
import cv2


def validate_jpeg(image_path: Path) -> bool:
    """
    Перевіряє, що файл є валідним JPEG.
    1) Файл існує.
    2) Відкривається через Pillow без помилок.
    3) Формат == 'JPEG'.
    """
    if not image_path.exists():
        print(f"[ERROR] Файл не знайдено: {image_path}")
        return False

    try:
        with Image.open(image_path) as img:
            img.verify()  # перевірка цілісності
        with Image.open(image_path) as img2:
            if img2.format != "JPEG":
                print(f"[ERROR] Файл існує, але формат не JPEG, а: {img2.format}")
                return False
    except Exception as e:
        print(f"[ERROR] Файл не є валідним зображенням JPEG: {e}")
        return False

    print("[OK] Файл валідний JPEG.")
    return True


def extract_exif(image_path: Path, output_json_path: Path):
    """
    Отримує EXIF-метадані через Pillow та зберігає їх у JSON.
    Якщо EXIF відсутній – створює порожній JSON-об'єкт.
    """
    print("[INFO] Отримую EXIF-метадані...")
    exif_data_clean = {}

    try:
        with Image.open(image_path) as img:
            exif = img.getexif()

            if not exif:
                print("[WARN] EXIF-дані відсутні.")
            else:
                # мапа ID -> назви тегів
                tag_map = {v: k for k, v in ExifTags.TAGS.items()}
                for tag_id, value in exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    # приводимо до str, щоб JSON міг зберегти
                    try:
                        exif_data_clean[tag_name] = str(value)
                    except Exception:
                        exif_data_clean[tag_name] = repr(value)

    except Exception as e:
        print(f"[ERROR] Не вдалося прочитати EXIF: {e}")

    # зберігаємо у JSON
    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(exif_data_clean, f, ensure_ascii=False, indent=4)
        print(f"[OK] EXIF-метадані збережені у: {output_json_path}")
    except Exception as e:
        print(f"[ERROR] Не вдалося зберегти EXIF у JSON: {e}")


def detect_faces_and_draw(image_path: Path, output_image_path: Path):
    """
    Виявляє фронтальні обличчя на зображенні за допомогою
    каскаду Хаара OpenCV та малює червоні рамки.
    Результат зберігає у output_image_path.
    """
    print("[INFO] Шукаю обличчя на зображенні...")

    # завантажуємо каскад Хаара з OpenCV
    face_cascade_path = os.path.join(
        cv2.data.haarcascades, "haarcascade_frontalface_default.xml"
    )
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    if face_cascade.empty():
        print("[ERROR] Не вдалося завантажити каскад Хаара.")
        return

    # читаємо зображення
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"[ERROR] Не вдалося завантажити зображення через OpenCV: {image_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    print(f"[INFO] Знайдено обличь: {len(faces)}")

    # малюємо червоні рамки (BGR: (0, 0, 255))
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # зберігаємо результат
    success = cv2.imwrite(str(output_image_path), image)
    if success:
        print(f"[OK] Зображення з рамками збережене як: {output_image_path}")
    else:
        print("[ERROR] Не вдалося зберегти результат.")


def main():
    if len(sys.argv) != 2:
        print("Використання:")
        print(f"  python {Path(sys.argv[0]).name} new_york.jpeg")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    # 1. Перевірка валідності JPEG
    if not validate_jpeg(input_path):
        sys.exit(1)

    # Формуємо імена вихідних файлів
    output_image_path = input_path.with_name(input_path.stem + "_faces" + input_path.suffix)
    output_json_path = input_path.with_name(input_path.stem + "_metadata.json")

    # 2. EXIF → JSON
    extract_exif(input_path, output_json_path)

    # 3. Обличчя → зображення з рамками
    detect_faces_and_draw(input_path, output_image_path)


if __name__ == "__main__":
    main()
