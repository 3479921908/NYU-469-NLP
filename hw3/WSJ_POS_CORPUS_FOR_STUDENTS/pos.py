import re
import itertools


def open_files():
    with open("./WSJ_24_sys.pos", 'r') as file:
        content = file.read()
    return content


# Read training data
list_training = open_files().split()
list_tags = list_training[1::2]  # Extract tags
set_tags = set(list_tags)  # Get unique tags

# Extract words (tokens) from training data
list_words_training = [item for item in list_training if item not in list_tags]

# Clean the set_tags by removing single alphabetic characters
pattern = r'\b[A-Za-z]\b'
cleaned_tags = {tag for tag in set_tags if not re.match(pattern, tag)}
set_tags = cleaned_tags  # Update set_tags

print(len(set_tags))


def prior_p(list_words, list_tags, set_tags):
    """Computes prior probabilities of tags."""
    dict_tags = {tag: 0 for tag in set_tags}  # Initialize dictionary
    tracking = 0

    for i in range(len(list_words)):
        if list_words[i] == "." or i < len(list_words) - 1:
            if list_tags[i + 1] in dict_tags:
                dict_tags[list_tags[i + 1]] += 1
                tracking += 1

    # Convert counts to probabilities
    for tag in dict_tags:
        dict_tags[tag] /= tracking if tracking > 0 else 1

    return dict_tags


def transition_probabilities(set_tags, list_tags, current_term, previous_term):
    """Computes transition probabilities between tags."""
    transition_dict = {pair: 0 for pair in itertools.product(set_tags, set_tags)}
    bigrams_tags = [(list_tags[i], list_tags[i + 1]) for i in range(len(list_tags) - 1)]

    # Count occurrences of tag bigrams
    for bigram in bigrams_tags:
        if bigram in transition_dict:
            transition_dict[bigram] += 1

    # Convert counts to probabilities
    for pair in transition_dict:
        transition_dict[pair] /= (2 * len(list_tags)) if len(list_tags) > 0 else 1

    return transition_dict.get((current_term, previous_term), 0)


# Print prior probabilities
print(prior_p(list_words_training, list_tags, set_tags))
