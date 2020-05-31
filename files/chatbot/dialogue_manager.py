import os
from sklearn.metrics.pairwise import pairwise_distances_argmin

from chatterbot import ChatBot
from chatterbot.response_selection import get_first_response
import chatterbot
from .utils import *

class ThreadRanker(object):
    def __init__(self, paths):
        self.word_embeddings, self.embeddings_dim = load_embeddings(paths['WORD_EMBEDDINGS'])
        self.thread_embeddings_folder = paths['THREAD_EMBEDDINGS_FOLDER']

    def __load_embeddings_by_tag(self, tag_name):
        print(self.thread_embeddings_folder)
        embeddings_path = os.path.join(self.thread_embeddings_folder, tag_name + ".pkl")
        thread_ids, thread_embeddings = unpickle_file(embeddings_path)
        return thread_ids, thread_embeddings

    def get_best_thread(self, question, tag_name):
        # Id of the thread that is most similar to the question.
        # Search is performed only among questions of a given tag.
        
        thread_ids, thread_embeddings = self.__load_embeddings_by_tag(tag_name)

        # HINT: you have already implemented a similar routine in the 3rd assignment.
        question_vec = question_to_vec(question, self.word_embeddings, self.embeddings_dim)
        best_thread = pairwise_distances_argmin([question_vec], thread_embeddings, metric='cosine')
        
        return thread_ids[best_thread]


class DialogueManager(object):
    def __init__(self):      
        # Check if the pre-trained bot files are available,
        # download from S3 if it is not.

        print("Checking resource availablity...")
        # Structure of files in S3 bucket.
        bucket_structure = { 
          "pickles/" : [
              "intent_recognizer.pkl",
              "tfidf_vectorizer.pkl",
              "tag_classifier.pkl"],
          "word_embeddings/" : ["starspace_embedding.tsv"],
          "thread_embeddings_by_tags/" : [
              "c#.pkl",
              "c_cpp.pkl",
              "java.pkl",
              "javascript.pkl",
              "php.pkl",
              "python.pkl",
              "r.pkl",
              "ruby.pkl",
              "swift.pkl",
              "vb.pkl"
          ],
          "bot_database/" : ["db.sqlite3"]
        }
        # url to the public bucket with files
        PATH = 'https://s3-management-console.s3-us-west-2.amazonaws.com'
        
        get_pickles(PATH, bucket_structure)

        print("Loading resources...")

        # List of all pre-trained components.
        pickles_path = {
          'INTENT_RECOGNIZER' : "./chatbot/pickles/intent_recognizer.pkl",
          'TFIDF_VECTORIZER' : "./chatbot/pickles/tfidf_vectorizer.pkl",
          'TAG_CLASSIFIER' : "./chatbot/pickles/tag_classifier.pkl",
          "WORD_EMBEDDINGS" : "./chatbot/word_embeddings/starspace_embedding.tsv",
          "THREAD_EMBEDDINGS_FOLDER" : "./chatbot/thread_embeddings_by_tags"
        }

        # Intent recognition:
        self.intent_recognizer = unpickle_file(pickles_path['INTENT_RECOGNIZER'])
        self.tfidf_vectorizer = unpickle_file(pickles_path['TFIDF_VECTORIZER'])

        self.ANSWER_TEMPLATE = "I think it is about %s\nThis thread might help you: https://stackoverflow.com/questions/%s"

        # Task-oriented part:
        self.tag_classifier = unpickle_file(pickles_path['TAG_CLASSIFIER'])
        self.thread_ranker = ThreadRanker(pickles_path)


    def create_chitchat_bot(self):
        # Initialize conversationl chatbot, thrained on nltk english corpus, cornell movies dataset, and wikipedia.
        self.chatbot = ChatBot('Example Bot',
                                storage_adapter='chatterbot.storage.SQLStorageAdapter',
                                logic_adapters=[
                                  {
                                      'import_path': "chatterbot.logic.BestMatch",
                                      'default_response': 'I am sorry, but I do not understand.',
                                      'maximum_similarity_threshold': 0.90,
                                      'statement_comparison_function': "chatterbot.comparisons.levenshtein_distance",
                                      'response_selection_method': get_first_response
                                  },
                                  'chatterbot.logic.MathematicalEvaluation'
                                ],
                                database_uri='sqlite:///chatbot/bot_database/db.sqlite3',
                                read_only=True)


    def generate_answer(self, question):
        # Recognize intent, call chatbot for general conversation, or 
        # tag classifier and thread ranker for stackoverflow search.
        
        prepared_question = text_prepare(question)
        features = self.tfidf_vectorizer.transform([prepared_question])
        intent = self.intent_recognizer.predict(features)

        # Conversation:   
        if intent == 'dialogue':
            # Pass question to chitchat_bot to generate a response.       
            response = self.chatbot.get_response(question)
            return response
        
        # Task:
        else:        
            # Pass features to tag_classifier to get predictions.
            tag = self.tag_classifier.predict(features)[0]
           
            # Pass prepared_question to thread_ranker to get predictions.
            thread_id = self.thread_ranker.get_best_thread(prepared_question, tag)
           
            return self.ANSWER_TEMPLATE % (tag, thread_id[0])
