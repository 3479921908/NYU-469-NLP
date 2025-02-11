def reg_or(*args):
    body = "|".join(args)
    return f"(?:{body})"


def reg_opt(*args):
    body = reg_seq(*args)
    return f"(?:{body})?"


def reg_seq(*args):
    body = "".join(args)
    return body


def reg_rep(arg):
    return f"(?:{arg}){{1,}}"


def reg_opt_rep(arg):
    return f"(?:{arg}){{0,}}"


def reg_lookahead(*arg):
    body = reg_seq(*arg)
    return f"(?={body})"


def reg_lookbehind(*arg):
    body = reg_seq(*arg)
    return f"(?<={body})"


def reg_neg_lookahead(*arg):
    body = reg_seq(*arg)
    return f"(?!{body})"


def reg_neg_lookbehind(*arg):
    body = reg_seq(*arg)
    return f"(?<!{body})"