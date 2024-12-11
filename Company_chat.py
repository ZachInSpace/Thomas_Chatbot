import random
import json
import torch
import logging

from Company_model import NeuralNet
from nltk_utils_Company import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Thomas"

logging.basicConfig(filename='ChatBotChat.log', encoding='utf-8', level=logging.DEBUG)

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])

    return "I do not understand... Give us a call at; [phone_number] , or, send us an e-mail at 'sales@[company]railings.com' with more information and we will be happy to help further."

log = open("ChatBotResponses.log", "w")

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:

        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        log.write('Customer:')
        log.write(sentence)
        log.write('\n')
        log.write('Chatbot:')
        log.write(resp)
        log.write('\n')
        print(resp)