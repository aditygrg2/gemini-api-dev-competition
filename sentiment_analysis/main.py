import torch
import numpy as np
import librosa
from datasets import load_dataset
from transformers import HubertForSequenceClassification, Wav2Vec2FeatureExtractor


class SentimentAnalysis():
    """
    run(file_path) : provides sentiment analysis with audio file located at `file_path`
    """
    def __init__(self) -> None:
        self.model = HubertForSequenceClassification.from_pretrained("superb/hubert-base-superb-er")
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/hubert-base-superb-er")

    def map_to_array(self,example):
        speech, _ = librosa.load(example, sr=16000, mono=True)
        return speech

    def run(self, file_path = "audio3.mp3"):
        try:
            inputs = self.feature_extractor([self.map_to_array(file_path)], sampling_rate=16000, padding=True, return_tensors="pt")
            logits = self.model(**inputs).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            labels = [self.model.config.id2label[_id] for _id in predicted_ids.tolist()]
            return labels[0]
        except Exception as e:
            print(e)