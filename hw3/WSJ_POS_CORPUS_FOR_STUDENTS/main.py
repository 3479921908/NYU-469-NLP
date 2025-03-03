import numpy as np


def load_training_data(file_path):
    word_tag_counts = {}  # P(word | tag)
    tag_counts = {}  # Count of each tag
    bigram_counts = {}  # P(tag_i | tag_i-1)
    vocab = set()  # Vocabulary set

    prev_tag = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                prev_tag = None  # Sentence boundary
                continue

            word, tag = line.split()
            vocab.add(word)

            # Update counts
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            word_tag_counts.setdefault(tag, {}).setdefault(word, 0)
            word_tag_counts[tag][word] += 1

            if prev_tag:
                bigram_counts.setdefault(prev_tag, {}).setdefault(tag, 0)
                bigram_counts[prev_tag][tag] += 1

            prev_tag = tag

    return tag_counts, word_tag_counts, bigram_counts, vocab


def compute_probabilities(tag_counts, word_tag_counts, bigram_counts):
    total_tags = sum(tag_counts.values())
    print("total tags is " + str(total_tags))
    # Transition probabilities P(tag_i | tag_i-1)
    transition_probs = {}
    for prev_tag, next_tags in bigram_counts.items():
        transition_probs[prev_tag] = {t: count / tag_counts[prev_tag] for t, count in next_tags.items()}

    # Likelihood probabilities P(word | tag)
    likelihood_probs = {}
    for tag, words in word_tag_counts.items():
        likelihood_probs[tag] = {w: count / tag_counts[tag] for w, count in words.items()}

    # Prior probabilities P(tag)
    prior_probs = {tag: count / total_tags for tag, count in tag_counts.items()}

    return prior_probs, transition_probs, likelihood_probs


def viterbi(words, prior_probs, transition_probs, likelihood_probs, vocab):
    tags = list(prior_probs.keys())
    n = len(words)
    m = len(tags)

    dp = np.zeros((m, n))
    backpointer = np.zeros((m, n), dtype=int)

    # Initialization step
    for i, tag in enumerate(tags):
        dp[i, 0] = prior_probs.get(tag, 1e-6) * likelihood_probs.get(tag, {}).get(words[0], 1e-6)

    # Recursion step
    for t in range(1, n):
        for i, curr_tag in enumerate(tags):
            max_prob, max_state = max(
                (dp[j, t - 1] * transition_probs.get(prev_tag, {}).get(curr_tag, 1e-6) *
                 likelihood_probs.get(curr_tag, {}).get(words[t], 1e-6), j)
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


def tag_corpus(input_file, output_file, prior_probs, transition_probs, likelihood_probs, vocab):
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        sentence = []
        for line in fin:
            line = line.strip()
            if not line:
                if sentence:
                    tags = viterbi(sentence, prior_probs, transition_probs, likelihood_probs, vocab)
                    fout.writelines(f"{w}\t{t}\n" for w, t in zip(sentence, tags))
                    fout.write("\n")
                    sentence = []
            else:
                sentence.append(line)


def final_call(input_training_data, input_file, output_file):
    tag_counts, word_tag_counts, bigram_counts, vocab = load_training_data(input_training_data)

    print(f"Total tags: {len(tag_counts)}, Total unique words: {len(word_tag_counts)}, "
          f"Total bigrams: {len(bigram_counts)}, Vocabulary size: {len(vocab)}")

    prior_probs, transition_probs, likelihood_probs = compute_probabilities(tag_counts, word_tag_counts, bigram_counts)

    print("Probability tables computed successfully!")

    tag_corpus(input_file, output_file, prior_probs, transition_probs, likelihood_probs, vocab)

    print(f"Tagging complete! Output saved to {output_file}")


input_training_data = "One_Sentence.pos"  # Training dataset
input_file = "One_Sentence.words"  # Unlabeled test data
output_file = "One_Sentence_output.pos"  # generated output

final_call(input_training_data, input_file, output_file)
