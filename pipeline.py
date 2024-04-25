# chatbot_pipeline.py
import requests
import os
import json
import joblib
import random
import nltk
nltk.download('punkt')
import neattext.functions as nfx
import pickle
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Bidirectional, LSTM, LayerNormalization, Dense, Embedding, Input, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

class ChatbotPipeline:
    def __init__(self, model, tokenizer, lbl_enc,pipe_lr, df):
        self.model = model
        self.tokenizer = tokenizer
        self.lbl_enc = lbl_enc
        self.pipe_lr=pipe_lr
        self.df = df

    def clean_sentence(self, verification_data):
        line = verification_data
        line = line.strip().lower()
        line = " ".join(filter(lambda x: x[0] != '@', line.split()))
        punct = line.maketrans("", "", '.*%$^0123456789#!][\?&/)/(+-<>')
        result = line.translate(punct)
        tokened_sentence = nltk.word_tokenize(result)
        sentence = tokened_sentence[0:len(tokened_sentence)]
        return sentence

    def preprocess_input(self, pattern):
        cleaned_pattern = self.clean_sentence(pattern)
        text = [cleaned_pattern]
        x_test = self.tokenizer.texts_to_sequences(text)
        x_test = pad_sequences(x_test, padding='post', maxlen=self.model.input_shape[1])
        return x_test

    def save_pipeline(self, model_path, tokenizer_path, pipeline_path):
        # Exclude _thread.RLock object from pickling
        model_copy = self.model
        model_copy._stop_thread = None

        # Save Keras model
        model_copy.save(model_path)

        # Save tokenizer using pickle
        with open(tokenizer_path, 'wb') as tokenizer_file:
            pickle.dump(self.tokenizer, tokenizer_file)

        # Save other pipeline components
        pipeline = {
            'lbl_enc': self.lbl_enc,
            'df': self.df
        }
        with open(pipeline_path, 'wb') as pipeline_file:
            pickle.dump(pipeline, pipeline_file)

    def generate_answer(self, pattern):
        x_test = self.preprocess_input(pattern)
        y_pred = self.model.predict(x_test)
        predicted_tag = self.lbl_enc.inverse_transform([y_pred.argmax()])[0]
        responses = self.df[self.df['tag'] == predicted_tag]['responses'].values[0]

        if not responses:
            random_response = "I don't get it."
        else:
            random_response = random.choice(responses)

        print("Bot:", random_response)
        return random_response

    def get_text_emotion(self,pattern, api_key2):
        url = "https://twinword-emotion-analysis-v1.p.rapidapi.com/analyze/"
        payload = { "text": pattern }
        default_api_key = api_key2
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": default_api_key,
            "X-RapidAPI-Host": "twinword-emotion-analysis-v1.p.rapidapi.com"
        }
        response = requests.post(url, data=payload, headers=headers)
        emotions_detected = response.json()['emotions_detected'][0]
        return emotions_detected

    def predict_emotions(self,pattern):
        pattern_text = nfx.remove_stopwords(pattern)
        results = self.pipe_lr.predict([pattern])
        return results[0]

    def get_prediction_proba(self,pattern):
        results = self.pipe_lr.predict_proba([pattern])
        return results

    def get_emotion(self, pattern,api_key2):
        emotions_detected = self.get_text_emotion(pattern, api_key2=api_key2)
        return emotions_detected

    @classmethod
    def load_pipeline(cls, model_path, tokenizer_path, pipe_lr,pipeline_path):
        loaded_model = tf.keras.models.load_model(model_path)

        with open(tokenizer_path, 'rb') as tokenizer_file:
            loaded_tokenizer = pickle.load(tokenizer_file)

        with open(pipeline_path, 'rb') as pipeline_file:
            pipeline = pickle.load(pipeline_file)
        
        pipe_lr = joblib.load(open(pipe_lr, "rb"))

        return cls(
            model=loaded_model,
            tokenizer=loaded_tokenizer,
            lbl_enc=pipeline['lbl_enc'],
            pipe_lr=pipe_lr,
            df=pipeline['df']
        )
