import csv
import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

def read_specific_row(row_number):
    try:
        with open("movies.csv", mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for current_row_number, row in enumerate(reader):
                if current_row_number == row_number:
                    return str(row)
        return None
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return None

def get_sentence_vector(sentence):
    inputs = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
    return embeddings


def load_vectors_and_search(query_text, vector_file='text_vectors.csv'):
    vectors = pd.read_csv(vector_file, header=None).values
    query_vector = get_sentence_vector(query_text).flatten().reshape(1, -1)
    similarities = cosine_similarity(query_vector, vectors)
    most_similar_index = np.argmax(similarities)
    return most_similar_index

def update_vectors_and_save():
    df = pd.read_csv('movies.csv')
    texts = df['movie_info'].tolist()
    vectors = [get_sentence_vector(text).flatten() for text in texts]
    vector_df = pd.DataFrame(vectors)
    vector_df.to_csv('text_vectors.csv', index=False, header=False)


if __name__ == "__main__":
    update_vectors_and_save()
