import re as regex
import string

def lexer(contents):
    lines = contents.split('\n')
    special_char = set(string.punctuation) - {'"', "'"}

    for line in lines:
        chars = list(line)
        quote_count = 0
        tokens = []
        temp_str = ""
        for char in chars:

            if char == '"' or char == "'":
                quote_count += 1
            if quote_count % 2 == 0:
                in_quotes = False
            else:
                in_quotes = True

            if (char in special_char and temp_str != "" and in_quotes == False) or (char == " " and in_quotes == False):
                tokens.append(temp_str)
                temp_str = ""
                temp_str += char
                if temp_str in special_char:
                    tokens.append(temp_str)
                    temp_str = ""
                if temp_str == " ":
                    temp_str = ""
            else:
                temp_str += char
                
        if temp_str != "":
            tokens.append(temp_str)
        
        items = []

        for token in tokens:
            if token[0] == '"' or token[0] == "'":
                items.append(("String", token))
            elif regex.match(r"[.a-zA-Z]+", token):
                items.append(("Keyword", token))
            elif token in "+-*/%=":
                items.append(("Operator", token))
            elif token in special_char:
                items.append(("Delimeter", token))
            elif regex.match(r"[.0-9]+", token):
                items.append(("Number", token))

        print(items)

def parse(file):
    contents = open(file, "r").read()
    tokens = lexer(contents)
    return tokens