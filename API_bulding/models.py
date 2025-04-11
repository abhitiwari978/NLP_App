import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
import sys
import __main__

nltk.download('stopwords')

# Define the tokenizer (must be here for loading the vectorizer)
def recipe_tokenizer(text):
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    for mark in string.punctuation:
        text = text.replace(mark, '')
    words = text.split()
    return [stemmer.stem(w) for w in words if w not in stop_words and w.strip() != '']

# Make sure pickle can access the tokenizer
__main__.recipe_tokenizer = recipe_tokenizer

def recommend_recipes_api(user_input, top_n=1):

    with open('./input/combined_embeddings.pkl', 'rb') as f:
        recipe_embeddings = pickle.load(f)

    # Load the same vectorizer used during training (TF-IDF)
    with open('./input/tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)

    # Load original recipe data
    recipes_df = pd.read_pickle('./input/sampled_data.pkl')

    # Convert input to vector
    user_vector = vectorizer.transform([user_input]).toarray()

    # Adjust shape if needed
    if user_vector.shape[1] < recipe_embeddings.shape[1]:
        pad = recipe_embeddings.shape[1] - user_vector.shape[1]
        user_vector = np.pad(user_vector, ((0, 0), (0, pad)))
    else:
        user_vector = user_vector[:, :recipe_embeddings.shape[1]]

    # Find top N similar recipes
    similarities = cosine_similarity(user_vector, recipe_embeddings)[0]
    top_indices = similarities.argsort()[::-1][:top_n]

    # Format results as JSON-friendly list
    # results = []
    for idx in top_indices:
        recipe = recipes_df.iloc[idx]
        # results.append({
        #     "name": recipe['name'].capitalize(),
        #     "ingredients": recipe['ingredients'].replace("[", "").replace("]", "").replace("'", ""),
        #     "description": recipe['description'].capitalize()
        # })
        results={
            "name": recipe['name'].capitalize(),
            "ingredients": recipe['ingredients'].replace("[", "").replace("]", "").replace("'", ""),
        }

    return results

# a="italian food"
# print(recommend_recipes_api(a))

