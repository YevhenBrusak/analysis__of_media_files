# Лабораторна робота 2 — транскрипція аудіофайлу з AWS S3

Файл `transcribe_from_s3.py` — це консольний скрипт, який:

- завантажує аудіофайл `lab_2.mp3` з AWS S3 бакета (через `boto3`);
- відправляє цей файл у сервіс `Deepgram` для розпізнавання мовлення;
- отримує текст транскрипції та зберігає його у файл `lab_2_transcript.txt`.

Скрипт використовує файл `.env` (не входить у репозиторій) для зберігання ключів доступу та параметрів:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION
- DEEPGRAM_API_KEY
- S3_BUCKET_NAME
- S3_OBJECT_KEY
  
## Вимоги

- Python 3.9+
- Пакети: `boto3`, `requests`, `python-dotenv`
  - Встановлення: `python -m pip install boto3 requests python-dotenv`

Потрібні облікові дані:
- Створений AWS S3 bucket із файлом lab_2.mp3
- IAM користувач з доступом до S3 (Access Key ID + Secret Access Key)
- Deepgram API Key (speech-to-text)

## Налаштування

Створіть файл .env у корені проєкту та додайте:
```
AWS_ACCESS_KEY_ID=XXXX
AWS_SECRET_ACCESS_KEY=XXXX
AWS_REGION=eu-central-1

DEEPGRAM_API_KEY=XXXX

S3_BUCKET_NAME=назва_вашого_бакета
S3_OBJECT_KEY=lab_2.mp3
```
Файл `.env` додано в `.gitignore`, тому він не потрапляє в репозиторій.

## Запуск

1) Перейдіть у папку проєкту.

2) Запустіть скрипт `transcribe_from_s3.py`.
