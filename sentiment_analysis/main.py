import torch
import numpy as np
import librosa
from transformers import HubertForSequenceClassification, Wav2Vec2FeatureExtractor

class SentimentAnalysis():
    """
    run(file_path) : provides sentiment analysis with audio file located at `file_path`
    """
    def __init__(self) -> None:
        self.model = HubertForSequenceClassification.from_pretrained("superb/hubert-base-superb-er")
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/hubert-base-superb-er")

    def map_to_array(self, file_path):
        speech, _ = librosa.load(file_path, sr=16000, mono=True)
        return speech

    def split_audio(self, audio, chunk_size=16000*15):
        """
        Splits the audio into chunks of `chunk_size` samples (default: 15 seconds).
        """
        return [audio[i:i + chunk_size] for i in range(0, len(audio), chunk_size)]

    def analyze_chunks(self, chunks):
        """
        Analyzes each chunk and returns the sentiment labels.
        """
        labels = []
        for chunk in chunks:
            inputs = self.feature_extractor([chunk], sampling_rate=16000, padding=True, return_tensors="pt")
            logits = self.model(**inputs).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            label = self.model.config.id2label[predicted_ids.item()]
            labels.append(label)
        return labels

    def run(self, file_path="audio3.mp3"):
        try:
            audio = self.map_to_array(file_path)
            chunks = self.split_audio(audio)
            labels = self.analyze_chunks(chunks)
            return labels
        except Exception as e:
            print(e)