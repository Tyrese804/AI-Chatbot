import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf



lemmatizer = WordNetLemmatizer()

intents = json.loads(open(r"C:\Users\wtyre\Desktop\Projects\AI Chatbot\intents.json").read())


words = []
classes = []
documents = []
ignoreLetters = ['?', '!', '.', ',']

for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        wordList = nltk.word_tokenize(pattern)
        words.extend(wordList)
        documents.append((wordList, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignoreLetters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open(r"C:\Users\wtyre\Desktop\Projects\AI Chatbot\words.pkl", "wb"))
pickle.dump(classes, open(r"C:\Users\wtyre\Desktop\Projects\AI Chatbot\classes.pkl", "wb"))

training = []
outputEmpty = [0] * len(classes)

for document in documents:
    bag = []
    wordPatterns = document[0]
    wordPatterns = [lemmatizer.lemmatize(word.lower()) for word in wordPatterns]
    for word in words:
        bag.append(1) if word in wordPatterns else bag.append(0)

    outputRow = list(outputEmpty)
    outputRow[classes.index(document[1])] = 1
    training.append(bag + outputRow)

random.shuffle(training)
training = np.array(training, dtype=object)

trainX = training[:, :len(words)]
trainY = training[:, len(words):]

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(128, input_shape=(len(trainX[0]),), activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(64, activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(len(trainY[0]), activation='softmax'))

sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

model.fit(np.asarray(trainX).astype("float32"), np.asarray(trainY).astype("float32"), epochs=200, batch_size=5, verbose=1)
model.save(r"C:\Users\wtyre\Desktop\Projects\AI Chatbot\chatbot_model.h5")
print("done")