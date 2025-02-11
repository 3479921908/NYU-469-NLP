import re


def extract_phone_numbers(filename, output_filename):
    phone_pattern = re.compile(r'''
        (?:\(?\d{3}\)?[-.\s]?)?  # Optional area code (XXX) or XXX
        \d{3}  # First 3 digits
        [-.\s]?  # Separator (dash, dot, or space)
        \d{4}  # Last 4 digits
    ''', re.VERBOSE)

    matches = []

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            matches.extend(phone_pattern.findall(line))  # Extracts phone number candidates

    # Filter valid phone numbers
    filtered_matches = filter_phone_numbers(matches)

    with open(output_filename, 'w', encoding='utf-8') as out_file:
        for match in filtered_matches:
            out_file.write(match.strip() + '\n')  # Write only valid numbers


def filter_phone_numbers(matches):
    """
    Filters out numbers that are exactly 7-digit (XXX-XXXX format)
    and keeps only valid phone numbers.

    :param matches: List of phone number strings.
    :return: Filtered list of valid phone numbers.
    """
    filtered_numbers = []

    # Regex pattern to match valid phone numbers with area codes
    phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

    for number in matches:
        number = number.strip()

        # Remove exactly 7-digit numbers in the format XXX-XXXX
        if not re.fullmatch(r'\d{3}[-.\s]?\d{4}', number):
            filtered_numbers.append(number)

    return filtered_numbers


if __name__ == "__main__":
    input_file = input(
        "Enter file path (default: ./test.txt): ").strip() or "/Users/a1067098659/Documents/nyu/NLP469/regexp_corpora/test_dollar_phone_corpus.txt"
    output_file = "new_telephone_output.txt"

    extract_phone_numbers(input_file, output_file)
    print(f"Extracted phone numbers saved to {output_file}")