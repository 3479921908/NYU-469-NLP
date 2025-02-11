import re

def extract_dollar_amounts(filename, output_filename):
    # Define a regex pattern for matching numeric and word-based dollar amounts
    dollar_pattern = re.compile(r'''
        (?:(?<=\s)|^)    # Ensure it's at the start or preceded by a space
        (?:\$\s?|USD\s?|US\s?dollars?|U.S.\s?dollars?)  # Dollar sign or US Dollar variations
        (?:
            (?:\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)  # Numbers with commas and optional decimals
            |(?:\d+\.\d{1,2})  # Decimal numbers
            |(?:(?:one|two|three|four|five|six|seven|eight|nine|ten|
                eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|
                eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|
                eighty|ninety)(?:\s?(?:hundred|thousand|million|billion)?)*)  # Capture full word-based numbers
        )
        (?:
            \s?(million|billion|trillion)?  # Large number words
        )?
        (?:\s?(?:dollar|dollars|cent|cents))?  # Optional currency descriptor
        (?:\sand\s\d{1,2}\s?(?:cent|cents))?  # Optional cents after "and"
        (?=[.,\s]|$)  # Ensure proper termination
    ''', re.IGNORECASE | re.VERBOSE)

    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        print("File content:\n", content)  # Debugging: Print file content

    matches = dollar_pattern.findall(content)  # Apply regex to content

    # Extract matched values from the tuple output of findall()
    extracted_matches = [match[0].strip() if isinstance(match, tuple) else match.strip() for match in matches if match]

    print("Extracted dollar amounts:", extracted_matches)  # Debugging: Print extracted values

    # Write results to the output file
    with open(output_filename, 'w', encoding='utf-8') as out_file:
        for match in extracted_matches:
            out_file.write(match + '\n')

if __name__ == "__main__":
    input_text = "I have five hundred dollars in my hand."
    with open("test.txt", "w", encoding="utf-8") as file:
        file.write(input_text)

    extract_dollar_amounts("test.txt", "dollar_output.txt")
    print("Extraction complete. Check 'dollar_output.txt'.")
