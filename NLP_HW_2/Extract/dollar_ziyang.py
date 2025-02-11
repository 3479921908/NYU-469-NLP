import re
import sys

def get_extract_dollar_regex():
    def reg_or(*args):
        return r"(?:{})".format("|".join(args))

    def reg_seq(*args):
        return r"".join(args)

    def reg_opt(*args):
        return r"(?:{})?".format(reg_seq(*args))

    def reg_opt_rep(arg):
        return r"(?:{})*".format(arg)

    space_exp = r"[\s\t\n]{1,10}"
    eng_digit_exp = reg_or("a", "half", "quarter", "zero", "one", "two", "three",
                           "four", "five", "six", "seven", "eight", "nine")
    eng_teen_exp = reg_or("ten", "eleven", "twelve", "thirteen", "fourteen",
                          "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
    eng_tens_exp = reg_or("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
    eng_hundreds_exp = reg_or("hundred", "thousand", "million", "billion", "trillion", "gazillion")
    eng_number_component_exp = reg_or(eng_digit_exp, eng_teen_exp, eng_tens_exp, eng_hundreds_exp)
    eng_number_exp = reg_seq(reg_opt_rep(reg_seq(eng_number_component_exp, space_exp)), eng_number_component_exp)

    digits_integer_exp = reg_or(r"\d{1,3}(?:,\d{3})*", r"\d+")
    digits_decimal_exp = r"\.\d+"
    digits_number_exp = reg_seq(digits_integer_exp, reg_opt(digits_decimal_exp))

    nationality_abbr_exp = reg_or("USD", "CAD", "AUD", "NZD", "HKD", "SGD")
    nationality_exp = reg_or("US", "American", "Canadian", "Australian", "Hong Kong", "New Zealand", "Singapore")

    exp = reg_or(
        reg_seq(
            reg_opt("US", reg_opt(space_exp)), r"\$",
            reg_opt(space_exp), digits_number_exp, reg_opt(reg_opt(space_exp), eng_hundreds_exp)
        ),
        reg_seq(
            reg_or(eng_number_exp, digits_number_exp), space_exp, reg_or("dollars", "dollar"),
            space_exp, "and", reg_or(eng_number_exp, digits_number_exp),
            reg_opt(space_exp, reg_or("cents", "cent"))
        ),
        reg_seq(
            reg_or(eng_number_exp, digits_number_exp), space_exp,
            reg_or(
                reg_seq(reg_opt(nationality_exp, reg_opt(space_exp)), reg_or("dollars", "dollar", "cents", "cent")),
                nationality_abbr_exp
            )
        ),
    )
    return exp

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "-regex":
        print(get_extract_dollar_regex())
        sys.exit(0)
    elif len(sys.argv) != 2:
        print("Usage: python3 dollar_program.py [-regex] <file>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    exp = re.compile(get_extract_dollar_regex(), re.IGNORECASE)
    matches = [match.group() for match in re.finditer(exp, text)]
    print("\n".join(matches))

if __name__ == "__main__":
    main()