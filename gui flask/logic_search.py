import pandas as pd
import string
import math 
import numpy as np 
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def exec_logic(gui_query):
    
    pd.set_option('display.max_colwidth', 0)
    df = pd.read_csv("publications_data.csv")

    df['doc_content'] = df['name']+ ' ' + df['doc_title'] +" "+ df['doc_abstract']
    df = df.dropna()
    one_word_titles = df[df['doc_title'].str.count('\s') == 0]['doc_title']
    df = df[~df['doc_title'].isin(one_word_titles)]
    df = df.reset_index()
    df = df.drop(columns = 'index')

    df_final = df.drop(columns = ['doc_content'])

    def clean_docs(i, doc):
        stops = stopwords.words('english')
        words = doc.split()

        final = []

        for word in words:
            word = word.lower()
            word = word.replace('-', ' ')
            if word not in stops:
                final.append(word)
            
        final = " ". join(final)
        final = final.translate(str.maketrans("", "", string.punctuation))
        df_final.loc[i, 'doc_content'] = final

    for i in range(0, len(df)):
        data = df.loc[i, 'doc_content']
        clean_docs(i, data)

    documents = list(df_final['doc_content'])

    vectorizer = TfidfVectorizer(lowercase = True)

    tfidf_matrix = vectorizer.fit_transform(documents)
    # print(tfidf_matrix.toarray())

    def query_processor(query):
        stops = stopwords.words('english')
        words = query.split()

        final = []

        for word in words:
            word = word.lower()
            word = word.replace('-', ' ')
            if word not in stops:
                final.append(word)
            
        final = " ". join(final)
        final = final.translate(str.maketrans("", "", string.punctuation))
        return final


    query = gui_query
    processed_query = query_processor(query)
    #Transform the query using the fitted vectorizer
    query_vector = vectorizer.transform([processed_query])

    #Compute the cosine similarity
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix)

    #Find the most similar document, argsort() causes the max value's index to be at the last 
    most_similar_doc_index = cosine_similarities.argsort()[0]
    #converting most_similar_doc_index to a list so that the index values can be reversed (in descending order)
    similar_index_list = list(most_similar_doc_index)
    similar_index_list.reverse()

    similarities = []
    similarities_percentage = []
    most_similar_doc = []

    for index in similar_index_list[0:10]:
        similarities.append(cosine_similarities[0][index]) 
        most_similar_doc.append(documents[index])
    
    for s in similarities:
        similarities_percentage.append(((s + 1) / 2 * 100))
    
    # print("Most similar document: \n", most_similar_doc[0])

    final_result = []

    for i in range(0, len(most_similar_doc)):
        result = df_final.loc[similar_index_list[i]]
    #     print(f"Similarity: {similarities[i]},\nAuthor: {result['name']},\nDocument Link: {result['doc_link']}")
    #     print()
    #     print(f"{result['doc_title']}")
    #     print()
    #     print(f"{result['doc_abstract']}")
    #     print("~"*100)

        final_result.append({"Similarity": similarities[i],
                        "Author": result['name'],
                        "Document Link": result['doc_link'],
                        "Title" : result['doc_title'],
                        "Abstract" : result['doc_abstract']
                        })

    return final_result

