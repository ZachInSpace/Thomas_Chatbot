import json
import torch
import random

import numpy as np
import torch.nn as nn

from torch.utils.data import Dataset, DataLoader
from nltk_utils_company import tokenize, stem, bag_of_words
from Company_model import NeuralNet

with open('intents.json', 'r') as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []
#loop through each sentence in intents patterns
for intent in intents['intents']:
    tag = intent['tag']
    #add to tag list
    tags.append(tag)
    for pattern in intent['patterns']:
        #tokenize each word in the sentence
        w = tokenize(pattern)
        #add to our word list
        all_words.extend(w)
        #add to xy pair
        xy.append((w, tag))

#stem and lower each word
ignore_words = ['?', '!', '.', ',', '\ ', '/', '=', '+', '(', ')', '*', '&', '%', '<', '>', ';', ':', '-']
all_words = [stem(w) for w in all_words if w not in ignore_words]
#remove duplicates and sort
all_words = sorted(set(all_words))
tags = sorted(set(tags))

#create training data
x_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    #X: bag of words for each pattern_sentence
    bag = bag_of_words(pattern_sentence, all_words)
    x_train.append(bag)
    #Y: PyTorch CrossEntropyLoss needs only class labels, not one-hot
    label = tags.index(tag)
    y_train.append(label)

x_train = np.array(x_train)
y_train = np.array(y_train)

class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(x_train)
        self.x_data = x_train
        self.y_data = y_train

    #dataset[index]
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    #len(dataset) to return the size
    def __len__(self):
        return self.n_samples

#Hyperparameters
batch_size = 8
hidden_size = 8
output_size = len(tags)
input_size = len(x_train[0])
learning_rate = 0.001
num_epochs = 1000


dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset,
                            batch_size=batch_size,
                            shuffle=True,
                            num_workers=0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = NeuralNet(input_size, hidden_size, output_size).to(device)

#loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

#Train the model
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)

        #forward pass
        outputs = model(words)
        loss = criterion(outputs, labels)

        #backward pass & optimizer
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch +1) % 100 == 0:
        print(f'epoch {epoch+1}/{num_epochs}, loss={loss.item():.4f}')

print(f'final loss, loss={loss.item():.4f}')

data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "output_size": output_size,
    "hidden_size": hidden_size,
    "all_words": all_words,
    "tags": tags
}

FILE = "data.pth"
torch.save(data, FILE)

print(f'training complete. file saved to {FILE}')
