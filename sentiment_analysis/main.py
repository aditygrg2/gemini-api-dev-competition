import torch
import numpy as np
import librosa
from transformers import HubertForSequenceClassification, Wav2Vec2FeatureExtractor
from database.main import Database

model = HubertForSequenceClassification.from_pretrained("superb/hubert-base-superb-er")
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/hubert-base-superb-er")

class SentimentAnalysis():
    """
    run(file_path) : provides sentiment analysis with audio file located at `file_path`
    """
    def __init__(self) -> None:
        self.model = model
        self.feature_extractor = feature_extractor
        self.db = Database()

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

    def analyze_audio(self, file_path):
        try:
            audio = self.map_to_array(file_path)
            chunks = self.split_audio(audio)
            labels = self.analyze_chunks(chunks)
            return labels.pop()
        except Exception as e:
            print(e)

    def analyze_audio_and_save(self, file_path, isAgent, phoneNumber):
        def get_type(isAgent: bool):
            return "AI" if isAgent else "Human"

        try:
            label = self.analyze_audio(file_path)
            data = {
                "type": get_type(isAgent),
                "sent": label,
                "file": file_path
            }
            self.db.insert_audio_analysis(phoneNumber, data)
        except Exception as e:
            print(e)

    def analyze_chat(self, chat_history: str):
        tracker = self.db.get_trackers()
        words = tracker['words']
        title = tracker['title']
        count = dict()
        for word in words:
            count[word] = chat_history.count(word)
        return {"title":title,"trackerCount":count}

    def analyze_chat_and_save(self,chat_history,phoneNumber):
        try:
            tracker_analysis = self.analyze_chat(chat_history)
            self.db.insert_tracker_analysis(phoneNumber,tracker_analysis)
        except Exception as e:
            print(e)
            return "Some error occured"