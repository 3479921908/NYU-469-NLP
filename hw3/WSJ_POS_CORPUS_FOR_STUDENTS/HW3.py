import numpy as np

"""
NYU NLP Homework 3: Implement a Viterbi HMM POS tagger
    by WENJIE ZHANG (WZ2427)
    Spring 2025
"""

suffix_classes = {
    "able": "JJ", "ible": "JJ",
    "al": "JJ", "an": "JJ", "ar": "JJ",
    "ed": "VBD", "en": "VBN",
    "er": "JJR", "or": "NN",
    "est": "JJS", "ing": "VBG",
    "ish": "JJ", "ous": "JJ", "ful": "JJ", "less": "JJ",
    "ive": "JJ", "ly": "RB",
    "ment": "NN", "ness": "NN", "y": "JJ"
}


def classify_oov_word(word, oov_probabilities):
    for suffix, tag in suffix_classes.items():
        if word.endswith(suffix):
            return tag

    if word.isdigit():
        return "CD"
    if word[0].isupper():
        return "NNP"
    if not word.isalnum():
        return "."

    return max(oov_probabilities, key=oov_probabilities.get, default="NN")


def load_training_data(file_path):
    word_tag_counts = {}
    tag_counts = {}
    bigram_counts = {}
    vocab = set()
    rare_word_counts = {}

    prev_tag = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                prev_tag = None
                continue

            word, tag = line.split()
            vocab.add(word)

            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            word_tag_counts.setdefault(tag, {}).setdefault(word, 0)
            word_tag_counts[tag][word] += 1

            if word not in rare_word_counts:
                rare_word_counts[word] = tag
            else:
                rare_word_counts[word] = None

            if prev_tag:
                bigram_counts.setdefault(prev_tag, {}).setdefault(tag, 0)
                bigram_counts[prev_tag][tag] += 1

            prev_tag = tag

    rare_word_counts = {w: t for w, t in rare_word_counts.items() if t is not None}

    return tag_counts, word_tag_counts, bigram_counts, vocab, rare_word_counts


def compute_oov_probabilities(rare_word_counts, tag_counts):
    oov_probabilities = {tag: 0 for tag in tag_counts}

    for word, tag in rare_word_counts.items():
        oov_probabilities[tag] += 1

    total_rare_words = sum(oov_probabilities.values())

    if total_rare_words > 0:
        oov_probabilities = {tag: count / total_rare_words for tag, count in oov_probabilities.items()}
    else:
        oov_probabilities = {tag: 1 / len(tag_counts) for tag in tag_counts}  # Uniform distribution fallback

    return oov_probabilities


def compute_probabilities(tag_counts, word_tag_counts, bigram_counts):
    total_tags = sum(tag_counts.values())
    print("Total tags:", total_tags)

    transition_probs = {}
    for prev_tag, next_tags in bigram_counts.items():
        transition_probs[prev_tag] = {t: count / tag_counts[prev_tag] for t, count in next_tags.items()}

    likelihood_probs = {}
    for tag, words in word_tag_counts.items():
        likelihood_probs[tag] = {w: count / tag_counts[tag] for w, count in words.items()}

    prior_probs = {tag: count / total_tags for tag, count in tag_counts.items()}

    return prior_probs, transition_probs, likelihood_probs


def viterbi(words, prior_probs, transition_probs, likelihood_probs, vocab, oov_probabilities):
    tags = list(prior_probs.keys())
    n = len(words)
    m = len(tags)

    dp = np.zeros((m, n))
    backpointer = np.zeros((m, n), dtype=int)

    for i, tag in enumerate(tags):
        word = words[0]
        if word in vocab:
            likelihood = likelihood_probs.get(tag, {}).get(word, 1e-6)
        else:
            guessed_tag = classify_oov_word(word, oov_probabilities)
            likelihood = likelihood_probs.get(tag, {}).get(guessed_tag, 1e-6)
        dp[i, 0] = prior_probs.get(tag, 1e-6) * likelihood

    # Recursion step
    for t in range(1, n):
        for i, curr_tag in enumerate(tags):
            word = words[t]
            if word in vocab:
                likelihood = likelihood_probs.get(curr_tag, {}).get(word, 1e-6)
            else:
                guessed_tag = classify_oov_word(word, oov_probabilities)
                likelihood = likelihood_probs.get(curr_tag, {}).get(guessed_tag, 1e-6)

            max_prob, max_state = max(
                (dp[j, t - 1] * transition_probs.get(prev_tag, {}).get(curr_tag, 1e-6) * likelihood, j)
                for j, prev_tag in enumerate(tags)
            )
            dp[i, t] = max_prob
            backpointer[i, t] = max_state

    # Backtracking step
    best_path = []
    best_last_tag = np.argmax(dp[:, -1])
    best_path.append(tags[best_last_tag])

    for t in range(n - 1, 0, -1):
        best_last_tag = backpointer[best_last_tag, t]
        best_path.append(tags[best_last_tag])

    return list(reversed(best_path))


def tag_corpus(input_file, output_file, prior_probs, transition_probs, likelihood_probs, vocab, oov_probabilities):
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        sentence = []
        for line in fin:
            line = line.strip()
            if not line:
                if sentence:
                    tags = viterbi(sentence, prior_probs, transition_probs, likelihood_probs, vocab, oov_probabilities)
                    fout.writelines(f"{w}\t{t}\n" for w, t in zip(sentence, tags))
                    fout.write("\n")
                    sentence = []
            else:
                sentence.append(line)


def final_call(input_training_data, input_file, output_file):
    tag_counts, word_tag_counts, bigram_counts, vocab, rare_word_counts = load_training_data(input_training_data)

    print(f"Total tags: {len(tag_counts)}, Total unique words: {len(word_tag_counts)}, "
          f"Total bigrams: {len(bigram_counts)}, Vocabulary size: {len(vocab)}")

    oov_probabilities = compute_oov_probabilities(rare_word_counts, tag_counts)
    prior_probs, transition_probs, likelihood_probs = compute_probabilities(tag_counts, word_tag_counts, bigram_counts)

    print("Probability tables computed successfully!")

    tag_corpus(input_file, output_file, prior_probs, transition_probs, likelihood_probs, vocab, oov_probabilities)

    print(f"Tagging complete! Output saved to {output_file}")


# Run the program
final_call("WSJ_02-21.pos", "WSJ_23.words", "submission.pos")
