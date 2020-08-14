import numpy as np 
import pandas as pd
import pickle
import tensorflow as tf
import tensorflow_hub as hub
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

 
#dataset preparation
# import numpy as np
# import nltk
# import re
# import pandas as pd
# import pickle
# import tensorflow as tf
# import tensorflow_hub as hub

# module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
# model = hub.load(module_url)

# data_path = "WHO_FAQ.xlsx"
# dataset = pd.read_excel(data_path, index_col=0, engine="openpyxl")

# def embed(input):
#   return model([input])
# dataset['Question_Vector'] = dataset.Question.map(embed)
# dataset['Question_Vector'] = dataset.Question_Vector.map(np.array)

# print("dumping......")

# pickle.dump(df, open('dataset2.pkl', 'wb'))
# print("completed dmping .....")
        
class DialogueManager(object):
    def __init__(self):
 
        #self.model = tf.saved_model.load("../data/tmp/mobilenet/1/")
        self.model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        self.dataset = pickle.load(open('dataset.pkl', mode='rb'))
        self.questions = self.dataset.Question
        self.QUESTION_VECTORS = np.array(self.dataset.Question_Vector)
        self.COSINE_THRESHOLD = 0.5
        
        self.chitchat_bot = ChatBot("Chatterbot")       
        trainer = ChatterBotCorpusTrainer(self.chitchat_bot)
        trainer.train("chatterbot.corpus.english")
        
        self.words = []

        for sent in self.questions:
            self.words = self.words + sent[0].split()
 
         
        
    def embed(self,input):
        return self.model([input])  
        
    def cosine_similarity(self,v1, v2):
        mag1 = np.linalg.norm(v1)
        mag2 = np.linalg.norm(v2)
        if (not mag1) or (not mag2):
            return 0
        return np.dot(v1, v2) / (mag1 * mag2)
        
        
    def semantic_search(self, query, data, vectors):        
        query_vec = np.array(self.embed(query))
        query_avg = self.avg_sentence_vector(query_vec, query)
        res = []
        for i, d in enumerate(data):
            qvec = vectors[i].ravel()
            qavg = self.avg_sentence_vector(qvec, self.questions[i][0])
            sim = self.cosine_similarity(query_avg, qavg)
            # print(sim)
            res.append((sim, d[:100], i))
            
        print(res[:2])
        return sorted(res, key=lambda x : x[0], reverse=True)       
            
    
    def generate_answer(self, question):
        '''This will return list of all questions according to their similarity,but we'll pick topmost/most relevant question'''
        most_relevant_row = self.semantic_search(question, self.questions, self.QUESTION_VECTORS)[0]
        print(most_relevant_row)
        if most_relevant_row[0][0]>=self.COSINE_THRESHOLD:
            answer = self.dataset.Answer[most_relevant_row[2]]
        else:
            answer = self.chitchat_bot.get_response(question)
        return answer
    
    def avg_sentence_vector(self, feature_vec, q):
        #function to average all words vectors in a given paragraph
        # featureVec = np.zeros((num_features,), dtype="float32")
        a = 0.001
        avg = np.full((feature_vec.shape[0], ), a)
        feature_vec = np.add(avg, feature_vec)
        nwords = []
        # print('shap', feature_vec.shape[0])

        for word in q.split():
            nwords += [self.words.count(word)]
        
        nwords = np.array(nwords)
        m = np.mean(nwords)

        feature_vec = np.divide(feature_vec, a + m)
        return feature_vec
         