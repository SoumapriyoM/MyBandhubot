
# train.py

import os,json
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Bidirectional, LSTM, LayerNormalization, Dense, Embedding, Input, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import plot_model
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random
import nltk
import re
import pickle

def clean_sentence(verification_data):
    line = verification_data
    # Remove whitespace from line and lower case iter
    line = line.strip().lower()
    # Removing word with @ sign as we dont need name tags of twitter
    line = " ".join(filter(lambda x: x[0] != '@', line.split()))
    # Remove punctuations and numbers from the line
    punct = line.maketrans("", "", '.*%$^0123456789#!][\?&/)/(+-<>')
    result = line.translate(punct)
    # Tokenize the whole tweet sentence
    tokened_sentence = nltk.word_tokenize(result)
    # We take the tweet sentence from tokened sentence
    sentence = tokened_sentence[0:len(tokened_sentence)]
    return sentence

def preprocess_data(data):
    dic = {"tag": [], "patterns": [], "responses": []}
    for i in range(len(data)):
        ptrns = data[data.index == i]['patterns'].values[0]
        rspns = data[data.index == i]['responses'].values[0]
        tag = data[data.index == i]['tag'].values[0]
        for j in range(len(ptrns)):
            dic['tag'].append(tag)
            dic['patterns'].append(ptrns[j])
            dic['responses'].append(rspns)

    df = pd.DataFrame.from_dict(dic)

    tokenizer = Tokenizer(lower=True, split=' ')
    tokenizer.fit_on_texts(df['patterns'])
    vocab_size = len(tokenizer.word_index)

    ptrn2seq = tokenizer.texts_to_sequences(df['patterns'])
    X = pad_sequences(ptrn2seq, padding='post')

    lbl_enc = LabelEncoder()
    y = lbl_enc.fit_transform(df['tag'])

    return tokenizer, vocab_size, X, lbl_enc, y, df

def build_model(vocab_size, max_sequence_length, num_classes):
    model = Sequential()
    model.add(Input(shape=(max_sequence_length)))
    model.add(Embedding(input_dim=vocab_size + 1, output_dim=100, mask_zero=True))

    # Bidirectional LSTM layers
    model.add(Bidirectional(LSTM(32, return_sequences=True)))
    model.add(LayerNormalization())
    model.add(Bidirectional(LSTM(32, return_sequences=True)))
    model.add(LayerNormalization())
    model.add(Bidirectional(LSTM(32)))
    model.add(LayerNormalization())
    # Dense layers
    model.add(Dense(128, activation="relu"))
    model.add(LayerNormalization())
    model.add(Dropout(0.2))
    model.add(Dense(128, activation="relu"))
    model.add(LayerNormalization())
    model.add(Dropout(0.2))

    # Output layer
    model.add(Dense(num_classes, activation="softmax"))

    # Compile the model
    model.compile(optimizer='adam', loss="sparse_categorical_crossentropy", metrics=['accuracy'])

    return model

def train_model(model, X, y, callbacks=None, epochs=50, batch_size=10):
    model_history = model.fit(x=X,
                              y=y,
                              batch_size=batch_size,
                              callbacks=callbacks,
                              epochs=epochs)

def save_pipeline(model, tokenizer, lbl_enc, df, model_path, tokenizer_path, pipeline_path):
    pickle_folder = 'model_jar'

    # Save the trained model
    model.save(os.path.join(pickle_folder, model_path))

    # Save tokenizer using pickle in the pickle folder
    with open(os.path.join(pickle_folder, tokenizer_path), 'wb') as tokenizer_file:
        pickle.dump(tokenizer, tokenizer_file)

    # Save other pipeline components in the pickle folder
    pipeline = {
        'lbl_enc': lbl_enc,
        'df': df
    }
    with open(os.path.join(pickle_folder, pipeline_path), 'wb') as pipeline_file:
        pickle.dump(pipeline, pipeline_file)

def main():
    # Load data from intents.json
    with open('dataset/intents.json', 'r') as f:
        data = json.load(f)

    # Preprocess data
    tokenizer, vocab_size, X, lbl_enc, y, df = preprocess_data(pd.DataFrame(data['intents']))

    # Build and train the model
    max_sequence_length = X.shape[1]
    num_classes = len(np.unique(y))
    model = build_model(vocab_size, max_sequence_length, num_classes)
    train_model(model, X, y)

    # Save the trained model and associated components
    save_pipeline(model, tokenizer, lbl_enc, df,
                  model_path='model.h5',
                  tokenizer_path='tokenizer.pkl',
                  pipeline_path='pipeline.pkl')

if __name__ == "__main__":
    main()
