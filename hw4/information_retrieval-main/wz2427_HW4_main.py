import re
import math
from collections import Counter
from nltk.stem import PorterStemmer

from stop_list import closed_class_stop_words

STOP_WORDS = set(closed_class_stop_words)
STEMMER = PorterStemmer()


def tokenize(text):
    text = re.sub(r'[^a-zA-Z]+', ' ', text)  # Keep only letters
    tokens = text.lower().split()
    result = [STEMMER.stem(t) for t in tokens if t not in STOP_WORDS]
    return result  # Return as a list of tokens


def parse_queries(qry_file):
    queries = []
    current_text = []
    reading_query = False

    with open(qry_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('.I'):
                if current_text:
                    queries.append(" ".join(current_text))
                current_text = []
                reading_query = False
            elif stripped.startswith('.W'):
                reading_query = True
            elif reading_query:
                current_text.append(stripped)

        if current_text:
            queries.append(" ".join(current_text))

    return queries


def parse_abstracts(doc_file):
    docs = {}
    current_id = None
    sections_text = []
    reading_any_section = False

    with open(doc_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.rstrip('\n')
            if stripped.startswith('.I'):
                if current_id is not None and sections_text:
                    docs[current_id] = " ".join(sections_text)
                parts = stripped.split()
                current_id = int(parts[1])
                sections_text = []
                reading_any_section = False
            elif stripped.startswith('.T') or stripped.startswith('.A') or stripped.startswith(
                    '.B') or stripped.startswith('.W'):
                reading_any_section = True
            elif reading_any_section:
                sections_text.append(stripped)

        if current_id is not None and sections_text:
            docs[current_id] = " ".join(sections_text)

    return docs


def compute_tfidf(docs):
    doc_tokens = {d_id: tokenize(text) for d_id, text in docs.items()}
    doc_term_counts = {d_id: Counter(tokens) for d_id, tokens in doc_tokens.items()}
    doc_lengths = {d_id: len(tokens) for d_id, tokens in doc_tokens.items()}
    all_terms = set(term for tokens in doc_tokens.values() for term in tokens)

    # Compute document frequency (df) for each term
    df_count = Counter()
    for tokens in doc_tokens.values():
        unique_terms = set(tokens)
        for term in unique_terms:
            df_count[term] += 1

    N = len(docs)  # Total number of documents

    # Compute IDF values
    idf = {term: math.log(N / (df_count[term] + 1)) for term in all_terms}

    # Compute TF-IDF for each document
    doc_tfidf = {}
    for d_id, term_count in doc_term_counts.items():
        tfidf_scores = {term: (count / doc_lengths[d_id]) * idf[term] for term, count in term_count.items()}
        doc_tfidf[d_id] = tfidf_scores

    return doc_tfidf, idf, all_terms


def compute_cosine_similarity(query, doc_tfidf, idf, all_terms):
    """
    Computes cosine similarity between a query and all documents.
    Returns: List of (doc_id, similarity_score), sorted in descending order.
    """
    query_tokens = tokenize(query)
    query_tf = Counter(query_tokens)

    # Compute query TF-IDF vector
    query_tfidf = {term: (query_tf[term] / len(query_tokens)) * idf.get(term, 0) for term in query_tf}

    # Compute cosine similarity
    scores = {}
    for d_id, doc_vector in doc_tfidf.items():
        dot_product = sum(query_tfidf.get(term, 0) * doc_vector.get(term, 0) for term in all_terms)
        doc_magnitude = math.sqrt(sum(val ** 2 for val in doc_vector.values()))
        query_magnitude = math.sqrt(sum(val ** 2 for val in query_tfidf.values()))

        # Avoid division by zero
        if doc_magnitude > 0 and query_magnitude > 0:
            scores[d_id] = dot_product / (doc_magnitude * query_magnitude)
        else:
            scores[d_id] = 0.0

    # Sort by similarity score in descending order
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked_results[:100]  # Keep only top 100


def main():
    query_file = "data/cran.qry"
    doc_file = "./data/cran.all.1400"
    output_file = "output.txt"

    queries = parse_queries(query_file)
    docs = parse_abstracts(doc_file)

    print(f"Loaded {len(queries)} queries and {len(docs)} documents.")

    # Compute TF-IDF for all documents
    doc_tfidf, idf, all_terms = compute_tfidf(docs)

    # Compute cosine similarity for each query
    ranked_results = []
    for q_index, query_text in enumerate(queries):
        q_id = q_index + 1  # 1-based index
        top_docs = compute_cosine_similarity(query_text, doc_tfidf, idf, all_terms)

        for d_id, score in top_docs:
            ranked_results.append(f"{q_id} {d_id} {score:.6f}")

    with open(output_file, "w", encoding="utf-8") as outf:
        for line in ranked_results:
            outf.write(line + "\n")

    print(f"Finished")


if __name__ == "__main__":
    main()
