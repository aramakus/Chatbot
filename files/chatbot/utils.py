import nltk
import pickle
import re
import numpy as np
import requests
import os
from tqdm import tqdm

nltk.download('stopwords')
from nltk.corpus import stopwords

# Paths for all resources for the bot.
RESOURCE_PATH = {
    'INTENT_RECOGNIZER': 'intent_recognizer.pkl',
    'TAG_CLASSIFIER': 'tag_classifier.pkl',
    'TFIDF_VECTORIZER': 'tfidf_vectorizer.pkl',
    'THREAD_EMBEDDINGS_FOLDER': 'thread_embeddings_by_tags',
    'WORD_EMBEDDINGS': 'word_embeddings.tsv',
}


def text_prepare(text):
    """Performs tokenization and simple preprocessing."""

    replace_by_space_re = re.compile('[/(){}\[\]\|@,;]')
    bad_symbols_re = re.compile('[^0-9a-z #+_]')
    stopwords_set = set(stopwords.words('english'))

    text = text.lower()
    text = replace_by_space_re.sub(' ', text)
    text = bad_symbols_re.sub('', text)
    text = ' '.join([x for x in text.split() if x and x not in stopwords_set])

    return text.strip()


def load_embeddings(embeddings_path):
    """Loads pre-trained word embeddings from tsv file.

    Args:
      embeddings_path - path to the embeddings file.

    Returns:
      embeddings - dict mapping words to vectors;
      embeddings_dim - dimension of the vectors.
    """

    # Hint: you have already implemented a similar routine in the 3rd assignment.
    # Note that here you also need to know the dimension of the loaded embeddings.
    # When you load the embeddings, use numpy.float32 type as dtype

    with open(embeddings_path, encoding='utf8') as file:
      embeddings = {}
      for line in file:
          content = line.split()
          word = content[0]
          vect = np.array([float(elem) for elem in content[1:]])
          embeddings[word] = vect
  
    embeddings_dim = len(vect)

    return embeddings, embeddings_dim
    

def get_pickles(PATH, file_structure):
    '''
    Download pre-trained files from S3 publick bucket.
    '''
    # Extract S3 bucket name from PATH
    BUCKET = re.search("(?<=\/{2})(.*)(?=.com)", PATH).group(0) + ".com"
    PATH = PATH + "/"
    
    # Headers for S3 get request
    headers = {'Host': BUCKET}

    for directory, files in file_structure.items():
        if os.path.exists("chatbot/" + directory) is False:
            os.mkdir("chatbot/" + directory)

        for file in files:
            # Check the file exists
            if os.path.exists("chatbot/" + directory + file): continue

            url = PATH + directory + file
            r = requests.get(url, stream=True, headers=headers) #  for a nice quite progress bar
            
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024
            
            with open("chatbot/" + directory + file, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                    for data in r.iter_content(block_size):
                        f.write(data)
                        pbar.set_postfix(file=file, refresh=False)
                        pbar.update(len(data))


def question_to_vec(question, embeddings, dim):
    """Transforms a string to an embedding by averaging word embeddings."""

    # Hint: you have already implemented exactly this function in the 3rd assignment.

    tokens = [elem for elem in question.split()]
    vec = np.zeros(dim)
    cnt = 0
    for token in tokens:
        if token in embeddings: 
            vec += embeddings[token]
            cnt += 1
    
    if cnt == 0: return vec
    else: return vec/cnt

def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)
