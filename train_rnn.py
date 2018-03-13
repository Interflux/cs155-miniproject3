"""
Filename:     train_rnn.py
Version:      -
Date:         2018/3/12 (last modified)

Description:  Processes data for RNN training and trains an RNN model for text
              prediction.

Author(s):    https://github.com/vivshaw/, very slightly modified by Dennis Lam

Note #1:      This code is from the shakespeare-LSTM repository which can be
              found here: https://github.com/vivshaw/shakespeare-LSTM. Thank you 
              to the author "vivshaw" for making this code publicly available.
              
Note #2:      Please note in the definition of the lambda function that is passed
              to the Lambda layer, the temperature parameter must be set using
              a numerical value and not a variable. This is because TensorFlow
              will save the variable name but not its declaration or value when
              saving the model to the "model.yaml" file, resulting in an error
              when attempting to load this model into another program (e.g., 
              the GenerativeNetwork class defined in "generate_rnn.py" in this
              repository).

"""

import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation, Lambda
from keras.callbacks import ModelCheckpoint

with open("../sonnets_unlabeled.txt") as corpus_file:
    corpus = corpus_file.read()
print("Loaded a corpus of {0} characters".format(len(corpus)))

# Set parameters
lstm_size = 200
num_epochs = 200
sequence_length = 40

# Get a unique identifier for each char in the corpus, then make some dicts to ease encoding and decoding
chars = sorted(list(set(corpus)))
num_chars = len(chars)
encoding = {c: i for i, c in enumerate(chars)}
decoding = {i: c for i, c in enumerate(chars)}
print("Our corpus contains {0} unique characters.".format(num_chars))

# it slices, it dices, it makes julienned datasets!
# chop up our data into X and y, slice into roughly (num_chars / skip) overlapping 'sentences'
# of length sentence_length, and encode the chars
sentence_length = sequence_length
skip = 1
X_data = []
y_data = []
for i in range (0, len(corpus) - sentence_length, skip):
    sentence = corpus[i:i + sentence_length]
    next_char = corpus[i + sentence_length]
    X_data.append([encoding[char] for char in sentence])
    y_data.append(encoding[next_char])

num_sentences = len(X_data)
print("Sliced our corpus into {0} sentences of length {1}".format(num_sentences, sentence_length))

# Vectorize our data and labels. We want everything in one-hot
# because smart data encoding cultivates phronesis and virtue.
print("Vectorizing X and y...")
X = np.zeros((num_sentences, sentence_length, num_chars), dtype=np.bool)
y = np.zeros((num_sentences, num_chars), dtype=np.bool)
for i, sentence in enumerate(X_data):
    for t, encoded_char in enumerate(sentence):
        X[i, t, encoded_char] = 1
    y[i, y_data[i]] = 1

# Double check our vectorized data before we sink hours into fitting a model
print("Sanity check y. Dimension: {0} # Sentences: {1} Characters in corpus: {2}".format(y.shape, num_sentences, len(chars)))
print("Sanity check X. Dimension: {0} Sentence length: {1}".format(X.shape, sentence_length))

# Define our model
print("Let's build a brain!")
model = Sequential()
model.add(LSTM(lstm_size, input_shape=(sentence_length, num_chars)))
model.add(Dense(num_chars))
model.add(Lambda(lambda x: x / 1.50)) # Temperature value must be set here, without the use of variables
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')

# Dump our model architecture to a file so we can load it elsewhere
architecture = model.to_yaml()
with open('model.yaml', 'a') as model_file:
    model_file.write(architecture)

# Set up checkpoints
file_path="weights-{epoch:02d}-{loss:.3f}.hdf5"
checkpoint = ModelCheckpoint(file_path, monitor="loss", verbose=1, save_best_only=True, mode="min")
callbacks = [checkpoint]

# Action time! [Insert guitar solo here]
model.fit(X, y, nb_epoch=num_epochs, batch_size=128, callbacks=callbacks)

