import os
import boto3
import requests
from dotenv import load_dotenv

def load_env():
    """
    Завантажує змінні середовища з .env файлу.
    """
    load_dotenv()
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "eu-central-1")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_object_key = os.getenv("S3_OBJECT_KEY")

    if not all([aws_access_key_id, aws_secret_access_key, deepgram_api_key, s3_bucket_name, s3_object_key]):
        raise ValueError("Не всі змінні середовища задані. Перевір .env файл.")

    return {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
        "aws_region": aws_region,
        "deepgram_api_key": deepgram_api_key,
        "s3_bucket_name": s3_bucket_name,
        "s3_object_key": s3_object_key,
    }


def download_file_from_s3(config, local_filename):
    """
    Завантажує файл з S3 у локальний файл.
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=config["aws_access_key_id"],
        aws_secret_access_key=config["aws_secret_access_key"],
        region_name=config["aws_region"],
    )

    print(f"Завантажую {config['s3_object_key']} з бакета {config['s3_bucket_name']}...")
    s3.download_file(config["s3_bucket_name"], config["s3_object_key"], local_filename)
    print(f"Файл збережено локально як {local_filename}")


def transcribe_with_deepgram(config, audio_filename, output_filename):
    """
    Відправляє локальний аудіофайл в Deepgram і зберігає транскрипт у текстовий файл.
    """
    print("Відправляю аудіо в Deepgram для транскрипції...")

    url = "https://api.deepgram.com/v1/listen"

    headers = {
        "Authorization": f"Token {config['deepgram_api_key']}",
        "Content-Type": "audio/mpeg",  # для mp3
    }

    params = {
        "model": "nova-2",   # або інша доступна модель
        "language": "uk",    # 'uk' для української, 'en' для англійської
        "punctuate": "true",
    }

    with open(audio_filename, "rb") as audio_file:
        response = requests.post(url, headers=headers, params=params, data=audio_file)

    if response.status_code != 200:
        print("Помилка при зверненні до Deepgram:")
        print(response.status_code, response.text)
        return

    data = response.json()

    try:
        transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
    except (KeyError, IndexError):
        print("Не вдалося витягнути текст транскрипції з відповіді Deepgram.")
        print(data)
        return

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Транскрипція збережена у файл {output_filename}")


def main():
    # 1. Завантажити налаштування
    config = load_env()

    # 2. Завантажити аудіо з S3
    local_audio_filename = "lab_2.mp3"
    download_file_from_s3(config, local_audio_filename)

    # 3. Зробити транскрипцію через Deepgram
    output_transcript_filename = "lab_2_transcript.txt"
    transcribe_with_deepgram(config, local_audio_filename, output_transcript_filename)


if __name__ == "__main__":
    main()
