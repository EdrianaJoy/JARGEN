import re as regex
import string

# 1-5. OPERATOR SYMBOLS
Operator_Symbol = [
    "=", 
    "+=", 
    "-=", 
    "*=", 
    "/=", 
    "%=", 
    "^=", 
    "+", 
    "-", 
    "*", 
    "/", 
    "%", 
    "^", 
    "++", 
    "--", 
    "!", 
    "&&", 
    "||", 
    "==", 
    "!=", 
    ">", 
    "<", 
    ">=", 
    "<="
]

Operator_Name = [
    "Equal Sign",
    "Addition Assignment",
    "Subtraction Assignment",
    "Multiplication Assignment",
    "Division Assignment",
    "Remainder Assignment",
    "Exponentiation Assignment",
    "Addition Operator",
    "Subtraction Operator",
    "Multiplication Operator",
    "Division Operator",
    "Remainder Operator",
    "Exponentiation Operator",
    "Increment Operator",
    "Decrement Operator",
    "Logical NOT Operator",
    "Logical AND Operator",
    "Logical OR Operator",
    "Equal To Operator",
    "Not Equal To Operator",
    "Greater Than Operator",
    "Less Than Operator",
    "Greater Than or Equal To Operator",
    "Less Than or Equal To Operator"
]

# 6. 
# 7. 
# 8. 
# 9. 
# 10. 

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
            elif token in Operator_Symbol:
                # Find the index of the token
                index = Operator_Symbol.index(token)
                # Append the corresponding name and token as a tuple
                items.append((Operator_Name[index], token))
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