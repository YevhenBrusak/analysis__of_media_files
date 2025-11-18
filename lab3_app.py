import argparse
import os
import time
import boto3
import json
from langdetect import detect
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from dotenv import load_dotenv

# Завантажуємо nltk ресурси
nltk.download('vader_lexicon', quiet=True)

# Завантажуємо spaCy модель
nlp = spacy.load("en_core_web_sm")


def transcribe_with_aws(audio_s3_uri):
    transcribe = boto3.client(
        'transcribe',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    job_name = f"lab3_transcription_job_{int(time.time())}"

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        LanguageCode="en-US",
        MediaFormat="wav",
        Media={"MediaFileUri": audio_s3_uri},
    )

    # Очікуємо завершення
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        state = status["TranscriptionJob"]["TranscriptionJobStatus"]

        if state in ["COMPLETED", "FAILED"]:
            break
        time.sleep(2)

    if state == "FAILED":
        raise Exception("Transcription failed.")

    transcript_url = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]

    # Завантажуємо результат
    import requests
    response = requests.get(transcript_url)
    data = response.json()

    text = data["results"]["transcripts"][0]["transcript"]
    return text


def detect_language(text):
    return detect(text)


def sentiment(text):
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)
    if score["compound"] >= 0.05:
        return "Positive"
    elif score["compound"] <= -0.05:
        return "Negative"
    else:
        return "Neutral"


def search_phrase(text, phrase):
    pos = text.lower().find(phrase.lower())
    return pos if pos != -1 else None


def extract_entities(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents]


def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-source", required=True, help="WAV audio file name stored in S3")
    parser.add_argument("--phrase", required=True, help="Phrase to search for in the text")
    args = parser.parse_args()

    bucket = os.getenv("S3_BUCKET_NAME")
    audio_uri = f"s3://{bucket}/{args.audio_source}"

    print("Transcribing audio using AWS Transcribe...")
    text = transcribe_with_aws(audio_uri)

    print("\nTranscription:")
    print(text)

    print("\nLanguage:")
    print(detect_language(text))

    print("\nSentiment:")
    print(sentiment(text))

    print("\nPhrase search:")
    index = search_phrase(text, args.phrase)
    if index is not None:
        print(f"Phrase found at position: {index}")
    else:
        print("Phrase not found.")

    print("\nNamed entities:")
    entities = extract_entities(text)
    print(", ".join(entities) if entities else "No entities found.")


if __name__ == "__main__":
    main()
