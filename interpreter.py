import re as regex
import string

# 1-5. OPERATOR SYMBOLS
Operator_Symbols = [
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

Operator_Names = [
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

Single_Operator_Symbols = [
    "=",
    "+", 
    "-", 
    "*", 
    "/", 
    "%", 
    "^", 
    ">", 
    "<",
    "!",
    "&",
    "|"
]

# 6. Keywords
Keywords = [
    "flex", # Inspired by let: Declares a mutable variable (JavaScript).
    "nocap", # Inspired by const: Declares an immutable variable (JavaScript).
    "bet", # Inspired by var: Declares a variable, function-scoped (JavaScript).
    "forreal", # Inspired by for: Creates a loop (JavaScript, Python).
    "sus", # Inspired by if: Executes code if a condition is true (JavaScript, Python).
    "else", # Inspired by else: Executes code if 'if' condition is false (JavaScript, Python).
    "tryme", # Inspired by try: Tests for errors in a block (JavaScript, Python).
    "mood", # Inspired by switch: Executes code based on a matching case (JavaScript).
    "ouchy", # Inspired by break: Exits a loop or switch (JavaScript, Python).
    "spill", # Inspired by print/log: Outputs info ('console.log()' for JavaScript, 'print()' for Python).
    "looptalk", # Inspired by do-while: Executes a loop at least once (JavaScript).
    "like", # Inspired by increment: Increases a value (++, JavaScript).
    "unlike", # Inspired by decrement: Decreases a value (--, JavaScript).
    "reply", # Inspired by return: Exits a function with a value (JavaScript, Python).
    "post", # Inspired by scan: Reads user input ('prompt()' for JavaScript, 'input()' for Python).
    "talk", # Inspired by while: Loops while a condition is true (JavaScript, Python).
    "scene" # Inspired by case: A condition in a switch (JavaScript).
]

# 7. Reserved Words
Reserved_Words = [
    "tru", # Inspired by boolean: Represents true values (JavaScript).
    "barbers", # Inspired by boolean: Represents false values (JavaScript).
    "cancel", # Inspired by null: Represents an intentional absence of value (JavaScript).
    "fresh", # Inspired by new: Creates an instance of an object (JavaScript).
    "stat", # Inspired by static: Declares a class-level method or property (JavaScript).
    "super", # Inspired by super: Refers to the parent class (JavaScript).
    "class", # Inspired by class: Declares a blueprint for objects (JavaScript, Python).
    "char", # Inspired by char: Represents a single character.
    "num", # Inspired by int: Represents an integer (used in Python as a type).
    "caption", # Inspired by string: Represents a sequence of characters (JavaScript, Python).
    "feed", # Inspired by array: Represents a collection of items (JavaScript, similar to lists in Python).
    "trend" # Inspired by function: Declares a reusable block of code (JavaScript).
]

# 8. Noise Words
Noise_Words = {
    "real",
    "me",
    "y",
}

# 9. Delimiters
Delimiters = [
    "=",
    ",",
    ";",
    "+",
    '""',
    "@"
]

Delimiter_Names = [
    "Equal Sign",
    "Comma",
    "Semi-colon"
    "Add Sign",
    "Open Close Quotation",
    "At Sign"
]

# 10.Brackets
Brackets = [
    "(",
    ")",
    "[",
    "]",
    "{",
    "}"
]

Bracket_Names = [
    "Open Parenthesis",
    "Close Parenthesis",
    "Open Bracket",
    "Close Bracket",
    "Open Curly Brace",
    "Close Curly Brace"
]

# Insert All Token Types of JARGEN
# Example: Assignment_Operator = {=, +=, -=, *=, /=, %=}
# You can use other techniques other than explicitly typing it if it is more efficient

def lexer(contents):
    lines = contents.split('\n')
    special_char = set(string.punctuation) - {'"', "'"}

    nLines = []

    for line in lines:
        chars = list(line)
        tokens = []

        i = 0
        while i < len(chars):
            char = chars[i]
            # print(char)
            
            # Handle numbers with decimals
            if char.isdigit() or (char == '.' and i + 1 < len(chars) and chars[i + 1].isdigit()):
                start_index = i
                while i < len(chars) and (chars[i].isdigit() or chars[i] == '.'):
                    # Prevent double decimal points in one token
                    if chars[i] == '.' and (i + 1 >= len(chars) or not chars[i + 1].isdigit()):
                        break
                    i += 1
                number = ''.join(chars[start_index:i])
                tokens.append(number)
            
            elif char.isalnum():
                start_index = i
                while i < len(chars) and chars[i].isalnum():
                    i += 1
                alphanumeric = ''.join(chars[start_index:i])
                tokens.append(alphanumeric)
            elif char in {'"', "'"}:
                start_delim = char
                strings = [char]
                i += 1
                while i < len(chars):
                    current_char = chars[i]
                    if current_char == start_delim:
                        strings.append(current_char)
                        i += 1
                        break
                    else:
                        strings.append(current_char)
                    i += 1
                string_literal = ''.join(strings)
                tokens.append(string_literal)
            elif char in Single_Operator_Symbols:
                next_char = chars[i + 1] if i + 1 < len(chars) else None
                if next_char and (char + next_char) in Operator_Symbols:
                    tokens.append(char + next_char)
                    i += 2
                else:
                    tokens.append(char)
                    i += 1
            elif char in Brackets:
                tokens.append(char)
                i += 1
            elif char.isspace():
                i += 1
            else:
                i += 1

        items = []

        for token in tokens:
            if token[0] == '"' or token[0] == "'":
                items.append(("String", token))
            elif token in Keywords:
                index = Keywords.index(token)
                items.append(("Keyword", token))
            elif token in Reserved_Words:
                index = Reserved_Words.index(token)
                items.append(("Reserved Word", token))
            elif token in Operator_Symbols:
                # Find the index of the token
                index = Operator_Symbols.index(token)
                # Append the corresponding name and token as a tuple
                items.append((Operator_Names[index], token))
            elif token in Delimiters:
                index = Delimiters.index(token)
                items.append((Delimiter_Names[index], token))
            elif token in Brackets:
                index = Brackets.index(token)
                items.append((Bracket_Names[index], token))
            elif regex.match(r"^\d+\.\d+$", token):  # Match decimals
                items.append(("Float Number", token))
            elif regex.match(r"^\d+$", token):  # Match integers
                items.append(("Integer", token))
            elif token not in Keywords and token not in Reserved_Words:
                items.append(("Identifier", token))

        nLines.append(items)
    return nLines

def parse(file):
    contents = open(file, "r").read()
    tokens = lexer(contents)
    return tokens

# FOR ERROR HANDLING
"""
def lexer(contents):
    if not contents.strip():
        raise ValueError("Error: Input content is empty.")

    lines = contents.split('\n')
    special_char = set(string.punctuation) - {'"', "'"}
    nLines = []

    for line_no, line in enumerate(lines, start=1):
        chars = list(line)
        tokens = []
        i = 0

        while i < len(chars):
            char = chars[i]

            # Handle numbers with decimals
            if char.isdigit() or (char == '.' and i + 1 < len(chars) and chars[i + 1].isdigit()):
                start_index = i
                dot_count = 0
                while i < len(chars) and (chars[i].isdigit() or chars[i] == '.'):
                    if chars[i] == '.':
                        dot_count += 1
                        if dot_count > 1:
                            raise ValueError(f"Error: Invalid number format at line {line_no}, position {i + 1}.")
                    i += 1
                number = ''.join(chars[start_index:i])
                tokens.append(("Float Number" if '.' in number else "Integer", number))

            # Handle alphanumeric identifiers
            elif char.isalnum():
                start_index = i
                while i < len(chars) and chars[i].isalnum():
                    i += 1
                alphanumeric = ''.join(chars[start_index:i])
                tokens.append(("Keyword" if alphanumeric in Keywords else "Identifier", alphanumeric))

            # Handle string literals
            elif char in {'"', "'"}:
                start_delim = char
                strings = [char]
                i += 1
                while i < len(chars):
                    current_char = chars[i]
                    if current_char == start_delim:
                        strings.append(current_char)
                        i += 1
                        break
                    strings.append(current_char)
                    i += 1
                else:
                    raise ValueError(f"Error: Unclosed string literal starting at line {line_no}, position {start_index + 1}.")
                string_literal = ''.join(strings)
                tokens.append(("String", string_literal))

            # Handle operators
            elif char in Single_Operator_Symbols:
                next_char = chars[i + 1] if i + 1 < len(chars) else None
                if next_char and (char + next_char) in Operator_Symbols:
                    tokens.append(("Operator", char + next_char))
                    i += 2
                else:
                    tokens.append(("Operator", char))
                    i += 1

            # Handle brackets
            elif char in Brackets:
                tokens.append(("Bracket", char))
                i += 1

            # Ignore whitespace
            elif char.isspace():
                i += 1

            # Invalid characters
            else:
                raise ValueError(f"Error: Invalid character '{char}' at line {line_no}, position {i + 1}.")

        nLines.append(tokens)
    return nLines

def parse(file):
    try:
        with open(file, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{file}' not found.")
    except IOError as e:
        raise IOError(f"Error: Unable to read the file. {e}")
    
    try:
        tokens = lexer(contents)
    except ValueError as e:
        print(e)
        return []
    
    return tokens
"""