import nltk
import numpy as np
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

nltk.download('punkt') # first-time use only
nltk.download('wordnet')
lemmer = nltk.stem.WordNetLemmatizer()
GREETING_INPUTS = ("hello", "hi", "doubt", "question", "problem","query",)
GREETING_RESPONSES = ["Hi there,I'm Suraksha, always at your service!", "Hello there Sir/Madam", "*nods* Here for your service.",  "Hello", "I am glad! You reached out"]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
sent_tokens = []

cred = credentials.Certificate('service_acc.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
print('Connected')

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def chatbot(query):
    f = open('chatbot.txt','r',errors = 'ignore')
    raw = f.read().lower()
    sent_tokens.extend(nltk.sent_tokenize(raw))
    word_tokens = nltk.word_tokenize(raw)
    # flag=True
    # print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type bye. To generate reports on an area, type area")
    # while(flag==True):
    user_response = query
    user_response=user_response.lower()
    if(user_response!='bye' and user_response!='area'):
        if(user_response=='thanks' or user_response=='thank you' ):
            # flag=False
            return "You're welcome!"
        else:
            if(greeting(user_response)!=None):
                return "ROBO: " + greeting(user_response)
            else:
                return response(user_response)
                sent_tokens.remove(user_response)
    elif(user_response=="area"):
        docs = db.collection(u'areas').stream()
        d = {}
        for doc in docs:
            d[doc.id] = doc.to_dict()
        print(d['area1'])

    else:
        # flag=False
        print("ROBO: Bye! take care..")

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

def response(user_response):
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response = robo_response + "I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response
