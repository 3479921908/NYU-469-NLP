#!/usr/bin/env python3
import re

def get_word_shape(token):
    """
    Transform the token into a word shape pattern.
    For each character:
      - Uppercase letters => 'X'
      - Lowercase letters => 'x'
      - Digits         => 'd'
      - Other symbols  => the symbol itself
    Example: 'McDonald' -> 'XxXxxxxx'
    """
    shape = []
    for ch in token:
        if ch.isupper():
            shape.append('X')
        elif ch.islower():
            shape.append('x')
        elif ch.isdigit():
            shape.append('d')
        else:
            # For punctuation or others, use the character itself
            shape.append(ch)
    return "".join(shape)

def get_prefix(token, n):
    """Return the first n characters of the token (if possible)."""
    return token[:n] if len(token) >= n else token

def get_suffix(token, n):
    """Return the last n characters of the token (if possible)."""
    return token[-n:] if len(token) >= n else token

def extract_features_for_sentence(tokens, pos_tags, bio_tags=None):
    """
    Extract enhanced feature strings for each token in a sentence.
    tokens   : list of words in the sentence.
    pos_tags : list of POS tags corresponding to tokens.
    bio_tags : list of BIO chunk tags (for training data). Set to None for test data.
    Returns a list of feature lines (strings), one per token.
    """
    feature_lines = []
    n = len(tokens)
    for i in range(n):
        token = tokens[i]
        pos = pos_tags[i]
        bio = bio_tags[i] if bio_tags is not None else None

        # Basic features
        features = [f"POS={pos}",
                    f"lower={token.lower()}",
                    f"shape={get_word_shape(token)}"]

        # Add prefix and suffix features if token length allows
        if len(token) >= 2:
            features.append(f"prefix2={get_prefix(token,2)}")
            features.append(f"suffix2={get_suffix(token,2)}")
        if len(token) >= 3:
            features.append(f"prefix3={get_prefix(token,3)}")
            features.append(f"suffix3={get_suffix(token,3)}")
            
        # Capitalization, digit and hyphen features
        features.append("capitalized=yes" if token and token[0].isupper() else "capitalized=no")
        features.append("has_digit=yes" if any(ch.isdigit() for ch in token) else "has_digit=no")
        features.append("has_hyphen=yes" if '-' in token else "has_hyphen=no")
        
        # Contextual features: previous tokens
        if i > 0:
            features.append(f"prev_word={tokens[i-1]}")
            features.append(f"prev_POS={pos_tags[i-1]}")
            # Also add lower and shape for previous token
            features.append(f"prev_lower={tokens[i-1].lower()}")
            features.append(f"prev_shape={get_word_shape(tokens[i-1])}")
            if i > 1:
                features.append(f"prev2_word={tokens[i-2]}")
                features.append(f"prev2_POS={pos_tags[i-2]}")
        # Contextual features: next tokens
        if i < n - 1:
            features.append(f"next_word={tokens[i+1]}")
            features.append(f"next_POS={pos_tags[i+1]}")
            features.append(f"next_lower={tokens[i+1].lower()}")
            features.append(f"next_shape={get_word_shape(tokens[i+1])}")
            if i < n - 2:
                features.append(f"next2_word={tokens[i+2]}")
                features.append(f"next2_POS={pos_tags[i+2]}")
                
        # For training data: add a feature for previous BIO tag (simulate MEMM dependency)
        if bio_tags is not None and i > 0:
            # Using the special placeholder; the underlying MaxEnt system should use the previous tag during decoding.
            features.append("prev_BIO=@@")
            
        # Build the output line: first field is token, then the features.
        # For training data, append the actual BIO label as the last field.
        if bio_tags is not None:
            line = "\t".join([token] + features + [bio])
        else:
            line = "\t".join([token] + features)
        feature_lines.append(line)
    return feature_lines

def process_file(input_path, output_path, is_training=True):
    """
    Process an input file (training or test) to produce an output feature file.
    The input file is expected to have:
      - Training: token<TAB>POS<TAB>BIO
      - Test: token<TAB>POS
    Sentence boundaries are blank lines.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            tokens, pos_tags, bio_tags = [], [], []
            for line in infile:
                line = line.rstrip("\n")
                if line == "":
                    # End of sentence: generate features for this sentence and write them out.
                    if tokens:
                        feature_lines = extract_features_for_sentence(
                            tokens, pos_tags, bio_tags if is_training else None)
                        for feat_line in feature_lines:
                            outfile.write(feat_line + "\n")
                        outfile.write("\n")  # Preserve sentence boundary
                    tokens, pos_tags, bio_tags = [], [], []
                else:
                    parts = line.split("\t")
                    if is_training:
                        if len(parts) != 3:
                            parts = line.split()  # fallback if tabs aren’t used
                        if len(parts) != 3:
                            continue  # skip malformed line
                        token, pos, bio = parts
                        tokens.append(token)
                        pos_tags.append(pos)
                        bio_tags.append(bio)
                    else:
                        if len(parts) != 2:
                            parts = line.split()
                        if len(parts) != 2:
                            continue
                        token, pos = parts
                        tokens.append(token)
                        pos_tags.append(pos)
            # Process any remaining sentence (if file doesn't end with a blank line)
            if tokens:
                feature_lines = extract_features_for_sentence(
                    tokens, pos_tags, bio_tags if is_training else None)
                for feat_line in feature_lines:
                    outfile.write(feat_line + "\n")
    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

def main():
    # Process the training file to create training.feature
    process_file("WSJ_02-21.pos-chunk", "training.feature", is_training=True)
    # Process the development (or test) file to create test.feature
    process_file("WSJ_24.pos", "test.feature", is_training=False)
    # You can also create a separate feature file for the final test corpus, e.g.:
    process_file("WSJ_23.pos", "WSJ_23.feature", is_training=False)

if __name__ == "__main__":
    main()
