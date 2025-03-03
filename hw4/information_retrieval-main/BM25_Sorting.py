import math
import re
from collections import Counter
from nltk.stem import PorterStemmer

from stop_list import closed_class_stop_words

STOP_WORDS = set(closed_class_stop_words)
STEMMER = PorterStemmer()

K = 1.2
B = 0.75

def tokenize(text):
    # keep alpha only
    text = re.sub(r'[^a-zA-Z]+', ' ', text)
    tokens = text.lower().split()
    result = []
    for t in tokens:
        if t not in STOP_WORDS:
            stemmed = STEMMER.stem(t)
            result.append(stemmed)
    return result

def parse_queries(qry_file):
    """
    Reads .qry file => returns list of query strings,
    in the order they appear. queries[i] => query # (i+1)
    """
    queries = []
    current_text = []
    reading_query = False

    with open(qry_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('.I'):
                # If we have a previous query text, store it
                if current_text:
                    queries.append(" ".join(current_text))
                current_text = []
                reading_query = False
            elif stripped.startswith('.W'):
                reading_query = True
            else:
                if reading_query:
                    current_text.append(stripped)

        # last one
        if current_text:
            queries.append(" ".join(current_text))

    return queries  # length 225

def parse_abstracts(doc_file):
    """
    Returns dict{doc_id -> full text}, merging .T, .A, .B, .W
    """
    docs = {}
    current_id = None
    sections_text = []
    reading_any_section = False

    with open(doc_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.rstrip('\n')
            if stripped.startswith('.I'):
                # store the previous doc if any
                if current_id is not None and sections_text:
                    docs[current_id] = " ".join(sections_text)
                # start new doc
                parts = stripped.split()
                current_id = int(parts[1])
                sections_text = []
                reading_any_section = False
            elif stripped.startswith('.T') or stripped.startswith('.A') \
                 or stripped.startswith('.B') or stripped.startswith('.W'):
                # now we read lines for that section
                reading_any_section = True
            else:
                if reading_any_section:
                    sections_text.append(stripped)

        # store last doc
        if current_id is not None and sections_text:
            docs[current_id] = " ".join(sections_text)

    return docs

def build_doc_index(docs):
    """
    docs: dict{doc_id->text}
    returns:
      doc_tokens: dict{doc_id->list_of_tokens}
      df_count:   Counter(term->doc_frequency)
      doc_lengths: dict{doc_id->int}
      avgdl: float
    """
    doc_tokens = {}
    df_count = Counter()
    doc_lengths = {}
    total_length = 0

    for d_id, text in docs.items():
        tokens = tokenize(text)
        doc_tokens[d_id] = tokens
        length = len(tokens)
        doc_lengths[d_id] = length
        total_length += length

        unique_terms = set(tokens)
        for t in unique_terms:
            df_count[t] += 1

    avgdl = total_length / float(len(docs)) if docs else 0.0
    return doc_tokens, df_count, doc_lengths, avgdl

def compute_idf(df_count, N):
    """
    BM25 IDF: idf(t) = ln( (N - df(t) + 0.5) / (df(t) + 0.5 ) )
    """
    idf_dict = {}
    for term, df_val in df_count.items():
        numerator = (N - df_val + 0.5)
        denominator = (df_val + 0.5)
        if denominator == 0:
            idf = 0.0
        else:
            idf = math.log(numerator / denominator)
        idf_dict[term] = idf
    return idf_dict

def bm25_score(query_tokens, d_id, doc_tokens, doc_lengths, idf_dict, avgdl):
    """
    BM25 = sum over query terms of [idf(t) * ((f*(k+1))/(f + k*(1 - b + b*(|d|/avgdl)))) ]
    where f is freq in doc, k=1.2, b=0.75
    """
    score = 0.0
    freq = Counter(doc_tokens[d_id])
    d_len = doc_lengths[d_id]

    for t in query_tokens:
        if t in idf_dict:
            f = freq[t]  # raw count
            if f > 0:
                idf = idf_dict[t]
                numerator = f * (K + 1.0)
                denominator = f + K * (1.0 - B + B * (d_len / avgdl))
                score += idf * (numerator / denominator)
    return score

def main():
    query_file = "data/cran.qry"
    doc_file = "./data/cran.all.1400"
    output_file = "output.txt"

    # 1) parse queries
    queries = parse_queries(query_file)
    num_queries = len(queries)

    # 2) parse docs (.T+.A+.B+.W)
    docs = parse_abstracts(doc_file)
    doc_ids = sorted(docs.keys())
    num_docs = len(doc_ids)

    print(f"Loaded {num_queries} queries and {num_docs} documents.")

    # 3) build doc index
    doc_tokens, df_count, doc_lengths, avgdl = build_doc_index(docs)

    # 4) compute BM25 idf
    idf_dict = compute_idf(df_count, num_docs)

    # 5) for each query, compute BM25, sort, write top 100
    with open(output_file, "w", encoding="utf-8") as outf:
        for q_index, q_text in enumerate(queries):
            q_id = q_index + 1  # 1-based
            q_tokens = tokenize(q_text)

            # compute BM25 for all docs
            results = []
            for d_id in doc_ids:
                score_val = bm25_score(q_tokens, d_id, doc_tokens, doc_lengths, idf_dict, avgdl)
                results.append((d_id, score_val))

            # sort descending
            results.sort(key=lambda x: x[1], reverse=True)

            # *** Only keep the top 100 ***
            top_100 = results[:100]

            # output lines: <q_id> <doc_id> <score>
            for d_id, s in top_100:
                outf.write(f"{q_id} {d_id} {s:.6f}\n")

    print(f"Done. Wrote at most 100 lines per query to {output_file}.")

if __name__ == "__main__":
    main()
