import re as regex
import string

# 1. Assignment Operator
Assignment_Operator = ["=", "+=", "-=", "*=", "/=", "%=", "^="]

# 2. Arithmetic Operator
Arithmetic_Operator = ["+", "-", "*", "/", "%", "^"]

# 3. Unary Operator
Unary_Operator = ["++", "--"]

# 4. Logical Operator
Logical_Operator = ["!", "&&", "||"]

# 5. Relational Operator
Relational_Operator = ["==", "!=", ">", "<", ">=", "<="]

# 6. Keywords
Keywords = [
    "flex",
    "nocap",
    "bet",
    "forreal",
    "sus",
    "else",
    "tryme",
    "mood",
    "ouchy",
    "spill",
    "looptalk",
    "like",
    "unlike",
    "reply",
    "post",
    "talk",
    "scene"
]

# 7. Reserved Words
Reserved_Words = [
    "tru",
    "barbers",
    "cancel",
    "fresh",
    "stat",
    "super",
    "class",
    "char",
    "num",
    "caption",
    "feed",
    "trend"
]

# 8. Noise Words
# 9. Delimiters
# 10.Brackets

# Insert All Token Types of JARGEN
# Example: Assignment_Operator = {=, +=, -=, *=, /=, %=}
# You can use other techniques other than explicitly typing it if it is more efficient

def lexer(contents):
    lines = contents.split('\n')
    special_char = set(string.punctuation) - {'"', "'"}

    nLines = []

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

            if (char in special_char and temp_str != "" and in_quotes == False) or (char.isspace() and in_quotes == False and temp_str != ""):
                tokens.append(temp_str)
                temp_str = ""
                temp_str += char
                if temp_str in special_char:
                    tokens.append(temp_str)
                    temp_str = ""
                if temp_str.isspace():
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

        nLines.append(items)
    return nLines

def parse(file):
    contents = open(file, "r").read()
    tokens = lexer(contents)
    return tokens
