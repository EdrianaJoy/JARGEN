from syntax import *

def flatten_and_convert(lexer_output):
    """
    Convert the lexer output into a single list of Token objects,
    ignoring line structure.
    """
    flat_list = []
    for line in lexer_output:
        for (token_type, token_value) in line:
            flat_list.append(Token(token_type, token_value))
    return flat_list