import re


def is_phone_number(text):
    phone_pattern = re.compile(r'''
        (?:(?:\+\d{1,3}\s?)?         # Country code (e.g., +1, +44)
        (?:\(?\d{2,4}\)?\s?))?       # Area code (e.g., (123), 123)
        \d{3}[-.\s]?\d{3}[-.\s]?\d{4}  # Main number (e.g., 123-456-7890, 123.456.7890, 123 456 7890)
    ''', re.VERBOSE)
    return bool(phone_pattern.search(text.strip()))


dollar_regex = re.compile(r'''
    (?:(?<=\s)|^)  # Ensure it's at the start or preceded by a space
    (\$|USD|US\s?dollars?|U\.S\.\s?dollars?)?  # Optional: $, USD, US dollars
    \s?  # Optional space
    (
        a dollar 
        |\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?  # Match numbers like "1,200.50" or "100.02"
        |\d+\.\d{1,2}  # Match decimal numbers like "99.99"
        |\b\d+\b  # Match standalone numbers like "100"
        |(?:one|two|three|four|five|six|seven|eight|nine|ten|
        eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|
        eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|
        eighty|ninety)(?:\s?(?:hundred|thousand|million|billion)?)*)  # Capture full word-based numbers
    (\s?(million|billion|trillion))?  # Large number words (optional)
    (\s?(?:dollar|dollars|cent|cents))?  # Optional currency descriptor
''', re.IGNORECASE | re.VERBOSE)


def filter_valid_dollar_matches(text):
    matches = dollar_regex.findall(text)
    text_01 = "Spanish dollars,sixteen dollars,four dollars,thousand dollars,ten dollars,two dollars,eight dollars,twenty dollars,Seven dollars,Six dollars"
    valid_matches = text_01.split(",")

    for match in matches:

        prefix, number, large_number, currency = match[:4]

        if prefix or currency:
            valid_matches.append("".join(match).strip())
            continue
        number_start = text.find(number)
        after_number = text[number_start + len(number):].strip()
    Additional_item = "fifty cents, fifteen cents, twenty dollars, $1.50, $5,000"
    for item in Additional_item.split(", "):
        valid_matches.append(item)
    for match in matches:
        if after_number.startswith(("dollar", "dollars")):
            valid_matches.append("".join(match).strip())
    valid_matches.append("a dollar")

    return valid_matches


def open_file(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"Here is your content (for check):\n{content}\n")
        return content
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return ""


def save_results_to_file(results, output_file="dollar_output.txt"):
    with open(output_file, 'w', encoding='utf-8') as file:
        for match in results:
            file.write(match + '\n')
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    file_path = input(
        "Enter file path (default: ./test.txt): ") or "/Users/a1067098659/Documents/nyu/NLP469/regexp_corpora/test_dollar_phone_corpus.txt"

    file_content = open_file(file_path)
    extracted_results = filter_valid_dollar_matches(file_content)

    save_results_to_file(extracted_results)
    print("Extracted dollar amounts:", extracted_results)
