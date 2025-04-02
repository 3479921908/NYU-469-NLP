import sys

def get_word_shape(word):
    """
    Generate a simple shape pattern for the word:
    Uppercase -> 'X', lowercase -> 'x', digit -> 'd', other chars stay same.
    E.g. "USA" -> "XXX", "Cat" -> "Xxx", "dog" -> "xxx", "F-16" -> "X-dd".
    """
    shape = []
    for ch in word:
        if ch.isdigit():
            shape.append('d')
        elif ch.isalpha():
            shape.append('X' if ch.isupper() else 'x')
        else:
            shape.append(ch)
    return "".join(shape)

def get_word_class(word):
    """
    Classify word into a coarse category: number, date, capitalized, lowercase, or other.
    """
    lower = word.lower()
    # Define sets for date-related words
    months = {"january","february","march","april","may","june","july",
              "august","september","october","november","december",
              "jan","feb","mar","apr","jun","jul","aug","sep","sept","oct","nov","dec"}
    days = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday",
            "mon","tue","wed","thu","fri","sat","sun"}
    # Check if word is a pure number (with possible punctuation like commas or periods)
    stripped = word.replace(",", "").replace(".", "").replace("/", "").replace("-", "")
    is_number = stripped.isdigit() and stripped != ""
    is_year = word.isdigit() and len(word) == 4  # e.g. "2021"
    if lower in months or lower in days or is_year:
        return "date"
    if is_number:
        return "number"
    if word and word[0].isupper():
        return "capitalized"
    if word.isalpha() and word.islower():
        return "lowercase"
    return "other"

# Main function
def main():
    if len(sys.argv) != 4:
        print("Usage: python make_features01.py <train|test> <input_file> <output_file>")
        sys.exit(1)
    mode = sys.argv[1].lower()
    if mode not in ("train", "test"):
        print(f"Error: mode must be 'train' or 'test', not '{sys.argv[1]}'")
        sys.exit(1)
    input_file = sys.argv[2]; output_file = sys.argv[3]

    # Read input data
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line == "":
                # blank line indicates sentence boundary
                data.append(("", "", ""))
            else:
                parts = line.split()
                if mode == "train":
                    if len(parts) != 3:
                        print(f"Error: training line doesn't have 3 columns: {line}")
                        sys.exit(1)
                    word, pos, chunk = parts
                    data.append((word, pos, chunk))
                else:  # test mode
                    if len(parts) != 2:
                        print(f"Error: test line doesn't have 2 columns: {line}")
                        sys.exit(1)
                    word, pos = parts
                    data.append((word, pos, None))

    # Prepare output
    START, END = "^START^", "^END^"
    with open(output_file, 'w', encoding='utf-8') as out:
        for i, (word, pos, chunk) in enumerate(data):
            if word == "" and pos == "":
                # Sentence boundary: write a blank line
                out.write("\n")
                continue

            # Determine context (previous and previous-2; next and next-2)
            if i == 0 or (i > 0 and data[i-1][0] == "" and data[i-1][1] == ""):
                # Beginning of sentence
                prev_word = prev_pos = prev2_word = prev2_pos = START
                prev_chunk = "O"  # no previous chunk, treat as Outside
            elif i == 1 or (i > 1 and data[i-2][0] == "" and data[i-2][1] == ""):
                # Second token in sentence
                prev_word, prev_pos, prev_chunk = data[i-1]
                prev2_word = prev2_pos = START
            else:
                # General case
                prev_word, prev_pos, prev_chunk = data[i-1]
                prev2_word, prev2_pos, _ = data[i-2]

            if i == len(data)-1 or (i < len(data)-1 and data[i+1][0] == "" and data[i+1][1] == ""):
                # End of sentence
                next_word = next_pos = next2_word = next2_pos = END
            elif i == len(data)-2 or (i < len(data)-2 and data[i+2][0] == "" and data[i+2][1] == ""):
                # Second to last token in sentence
                next_word, next_pos, _ = data[i+1]
                next2_word = next2_pos = END
            else:
                # General case for next tokens
                next_word, next_pos, _ = data[i+1]
                next2_word, next2_pos, _ = data[i+2]

            # Build features for current token
            features = []
            # Word identity and POS
            features.append(f"WORD={word}")
            features.append(f"POS={pos}")
            # Window of 2 context words/POS
            features.append(f"PREV_WORD={prev_word}")
            features.append(f"PREV_POS={prev_pos}")
            features.append(f"PREV2_WORD={prev2_word}")
            features.append(f"PREV2_POS={prev2_pos}")
            features.append(f"NEXT_WORD={next_word}")
            features.append(f"NEXT_POS={next_pos}")
            features.append(f"NEXT2_WORD={next2_word}")
            features.append(f"NEXT2_POS={next2_pos}")
            # Rich word shape features
            features.append("ALL_CAPS=True" if word.isalpha() and word.isupper() else "ALL_CAPS=False")
            features.append("ALL_LOWER=True" if word.isalpha() and word.islower() else "ALL_LOWER=False")
            features.append("INIT_CAP=True" if word and word[0].isupper() else "INIT_CAP=False")
            features.append("ALPHANUM=True" if any(ch.isalpha() for ch in word) and any(ch.isdigit() for ch in word) else "ALPHANUM=False")
            features.append("HAS_HYPHEN=True" if "-" in word else "HAS_HYPHEN=False")
            features.append("HAS_PUNCT=True" if any((not ch.isalnum()) for ch in word) else "HAS_PUNCT=False")
            features.append("HAS_DIGIT=True" if any(ch.isdigit() for ch in word) else "HAS_DIGIT=False")
            # Prefix/Suffix up to length 4
            if len(word) >= 2:
                features.append(f"PREF2={word[:2]}")
                features.append(f"SUFF2={word[-2:]}")
            if len(word) >= 3:
                features.append(f"PREF3={word[:3]}")
                features.append(f"SUFF3={word[-3:]}")
            if len(word) >= 4:
                features.append(f"PREF4={word[:4]}")
                features.append(f"SUFF4={word[-4:]}")
            # Word shape pattern
            features.append(f"SHAPE={get_word_shape(word)}")
            # Coarse word class feature
            features.append(f"WORD_CLASS={get_word_class(word)}")
            # POS bigrams
            features.append(f"PREV_CURR_POS={prev_pos}_{pos}")
            features.append(f"CURR_NEXT_POS={pos}_{next_pos}")
            # Lexical indicator features
            determiners = {"the","a","an","this","that","these","those",
                           "my","your","his","her","its","our","their",
                           "each","every","either","neither"}
            quantifiers = {"all","some","any","no","none","many","several","few",
                           "both","half","much","little","more","most","less","least",
                           "one","two","three","four","five","six","seven","eight","nine","ten"}
            prepositions = {"of","in","on","at","by","for","to","from","about","as",
                            "into","like","through","after","over","between","out",
                            "against","during","without","before","under","around","among","with","within","near","than"}
            np_heads = {"i","you","he","she","it","we","they","me","him","her","us","them",
                        "mr","mrs","ms","dr","sir","madam","president","prof","gov","govt",
                        "company","year","time","percent","people","man","woman","children","family","world"}
            features.append("DET=True"   if word.lower() in determiners  else "DET=False")
            features.append("QUANT=True" if word.lower() in quantifiers  else "QUANT=False")
            features.append("PREP=True"  if word.lower() in prepositions else "PREP=False")
            features.append("NP_HEAD=True" if word.lower() in np_heads   else "NP_HEAD=False")
            # Sentence boundary indicators
            features.append("BOS=True" if prev_word == START else "BOS=False")
            features.append("EOS=True" if next_word == END else "EOS=False")
            # Previous chunk tag feature (BIO tag history)
            if mode == "train":
                prev_bio = prev_chunk if prev_word != START and prev_chunk is not None else "O"
                features.append(f"Previous_BIO={prev_bio}")
            else:
                features.append("Previous_BIO=@@")

            # Write the output line
            if mode == "train":
                # word + features + gold chunk label
                out.write("\t".join([word] + features + [chunk]) + "\n")
            else:
                # word + features (no chunk label in test)
                out.write("\t".join([word] + features) + "\n")

if __name__ == "__main__":
    main()
