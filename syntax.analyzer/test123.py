import re as regex
from flatten import *

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
    "loop", # Inspired by do-while: Executes a loop at least once. Used with talk Keyword (JavaScript).
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
Noise_Words = [
    "real",
    "me",
    "y",
]

# 9. Delimiters
Delimiters = [
    ",",
    ";",
    "@"
]

Delimiter_Names = [
    "Comma",
    "Semi-colon",
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

def lexer(contents):
    if not contents.strip():
        raise ValueError("Error: Input content is empty.")

    lines = contents.split('\n')
    nLines = []

    try:
        for line_no, line in enumerate(lines, start=1):
            chars = list(line)
            tokens = []
            i = 0

            while i < len(chars):
                char = chars[i]

                # Handle numbers
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
                    if alphanumeric in Keywords:
                        tokens.append(("Keyword", alphanumeric))
                    elif alphanumeric in Reserved_Words:
                        tokens.append(("Reserved Word", alphanumeric))
                    elif i < len(chars) and chars[i] == "(":
                        tokens.append(("Function", alphanumeric))
                    else:
                        tokens.append(("Identifier", alphanumeric))

                # Handle string literals
                elif char in {'"', "'"}:
                    start_index = i
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
                        operator = char + next_char
                        operator_name = Operator_Names[Operator_Symbols.index(operator)]
                        tokens.append((operator_name, char + next_char))
                        i += 2
                    else:
                        operator_name = Operator_Names[Operator_Symbols.index(char)]
                        tokens.append((operator_name, char))
                        i += 1

                # Handle brackets
                elif char in Brackets:
                    bracket_name = Bracket_Names[Brackets.index(char)]
                    tokens.append((bracket_name, char))
                    i += 1
                
                # Handle delimiters
                elif char in Delimiters:
                    delimeter_name = Delimiter_Names[Delimiters.index(char)]
                    tokens.append((delimeter_name, char))
                    i += 1

                # Ignore whitespace
                elif char.isspace():
                    i += 1

                # Invalid characters
                else:
                    raise ValueError(f"Error: Invalid character '{char}' at line {line_no}, position {i + 1}.")
        
            nLines.append(tokens)

        for line_index, nLine in enumerate(nLines, start=1):
            for i, token in enumerate(nLine): 
                token_type, token_value = token  

                if token_value in {"spill", "post", "sus", "forreal", "mood", "talk"}:
                    if i + 1 < len(nLine) and nLine[i + 1][1] == '(':
                        j = i + 2
                        params = []
                        while j < len(nLine) and nLine[j][1] != ')':
                            params.append(nLine[j])
                            j += 1
                        
                        if j < len(nLine) and nLine[j][1] == ')':
                            if token_value in {"sus", "forreal", "mood", "talk"} and j != i + 2:
                                if j + 1 < len(nLine):
                                    if nLine[j + 1][1] == '{':
                                        line_pointer = line_index - 1
                                        token_pointer = 0
                                        statements = []
                                        while line_pointer < len(nLines):
                                            while token_pointer < len(nLines[line_pointer]):
                                                statements.append(nLines[line_pointer][token_pointer][1])
                                                if nLines[line_pointer][token_pointer][1] == '}':
                                                    has_Closing = True
                                                    if statements[-2] != '{':
                                                        has_Statement = True
                                                    else:
                                                        has_Statement = False
                                                else:
                                                    has_Closing = False
                                                    
                                                token_pointer += 1
                                            
                                            line_pointer += 1
                                            token_pointer = 0
                                        
                                        if has_Closing == False:
                                            raise ValueError(f"Error: Missing closing bracket for block starting at line {line_no}.")

                                        if has_Statement == False:
                                            raise ValueError(f"Error: Empty block at line {line_index}.")

                                    
                                    if token_value == "sus":
                                        if len(params) != 3:
                                            raise ValueError(f"Error: Invalid parameters inside parentheses for 'sus' at line {line_no}.")
                                        para1, para2, para3 = params
                                        if para1[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'sus' at line {line_no}.")
                                        if para2[0] not in {"Logical NOT Operator", "Logical AND Operator", "Logical OR Operator", "Equal To Operator", "Not Equal To Operator", "Greater Than Operator", "Less Than Operator", "Greater Than or Equal To Operator", "Less Than or Equal To Operator"}:
                                            raise ValueError(f"Error: Invalid operator in 'sus' at line {line_no}.")
                                        if para3[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'sus' at line {line_no}.")
                                    
                                    elif token_value == "mood":
                                        if len(params) != 1:
                                            raise ValueError(f"Error: Invalid parameters inside parentheses for 'sus' at line {line_no}.")
                                        para1 = params[0][0]
                                        if para1 not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'mood' at line {line_no}.")
                                    
                                    elif token_value == "forreal":
                                        if len(params) != 10:
                                            raise ValueError(f"Error: Invalid parameters inside parentheses for 'forreal' at line {line_no}.")
                                        para1, para2, para3, para4, para5, para6, para7, para8, para9, para10 = params
                                        if para1[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'forreal' at line {line_no}.")
                                        if para2[0] not in {"Equal Sign", "Addition Assignment", "Subtraction Assignment", "Multiplication Assignment", "Division Assignment", "Remainder Assignment", "Exponentiation Assignment"}:
                                            raise ValueError(f"Error: Invalid operator in 'forreal' at line {line_no}.")
                                        if para3[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'forreal' at line {line_no}.")
                                        if para4[0] != "Semi-colon":
                                            raise ValueError(f"Error: Missing semi-colon in 'forreal' at line {line_no}.")
                                        if para5[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'forreal' at line {line_no}.")
                                        if para6[0] not in {"Logical NOT Operator", "Logical AND Operator", "Logical OR Operator", "Equal To Operator", "Not Equal To Operator", "Greater Than Operator", "Less Than Operator", "Greater Than or Equal To Operator", "Less Than or Equal To Operator"}:
                                            raise ValueError(f"Error: Invalid operator in 'forreal' at line {line_no}.")
                                        if para7[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'forreal' at line {line_no}.")
                                        if para8[0] != "Semi-colon":
                                            raise ValueError(f"Error: Missing semi-colon in 'forreal' at line {line_no}.")
                                        if para9[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'forreal' at line {line_no}.")
                                        if para10[0] not in {"Increment Operator", "Decrement Operator"}:
                                            raise ValueError(f"Error: Invalid operator in 'forreal' at line {line_no}.")
                                    
                                    elif token_value == "talk":
                                        if len(params) != 3:
                                            raise ValueError(f"Error: Invalid parameters inside parentheses for 'talk' at line {line_no}.")
                                        para1, para2, para3 = params
                                        if para1[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'talk' at line {line_no}.")
                                        if para2[0] not in {"Logical NOT Operator", "Logical AND Operator", "Logical OR Operator", "Equal To Operator", "Not Equal To Operator", "Greater Than Operator", "Less Than Operator", "Greater Than or Equal To Operator", "Less Than or Equal To Operator"}:
                                            raise ValueError(f"Error: Invalid operator in 'talk' at line {line_no}.")
                                        if para3[0] not in {"Integer", "Float Number", "Identifier"}:
                                            raise ValueError(f"Error: Invalid parameter in 'talk' at line {line_no}.")
                            

                                else:
                                    raise ValueError(f"Error: Expected statement after '{token_value}' at line {line_no}.")
                            elif token_value in {"spill", "post"}:
                                continue
                            else:
                                raise ValueError(f"Error: Missing parameters for '{token_value}' at line {line_index}.")
                        else:
                            raise ValueError(f"Error: Missing closing parenthesis after '{token_value}' at line {line_index}.")
                    else:
                        raise ValueError(f"Error: Invalid format at line {line_no}. Expected '(' after '{token_value}'.")
                        
                elif token_value == "else":
                    if i + 1 < len(nLine):
                        if nLine[i + 1][1] == '{':
                            line_pointer = line_index - 1
                            token_pointer = 0
                            statements = []
                            while line_pointer < len(nLines):
                                while token_pointer < len(nLines[line_pointer]):
                                    statements.append(nLines[line_pointer][token_pointer][1])
                                    if nLines[line_pointer][token_pointer][1] == '}':
                                        has_Closing = True
                                        if statements[-2] != '{':
                                            has_Statement = True
                                        else:
                                            has_Statement = False
                                    else:
                                        has_Closing = False
                                        
                                    token_pointer += 1
                                
                                line_pointer += 1
                                token_pointer = 0
                            
                            if has_Closing == False:
                                raise ValueError(f"Error: Missing closing bracket for block starting at line {line_no}.")

                            if has_Statement == False:
                                raise ValueError(f"Error: Empty block after '{token_value}' at line {line_no}.")
                    else:
                        raise ValueError(f"Error: Expected statement after '{token_value}' at line {line_no}.")

                elif token_type == "Function":
                    
                    j = i + 2 
                    params = []
                    while j < len(nLine) and nLine[j][1] != ')':
                        params.append(nLine[j])
                        j += 1
                    
                    if j < len(nLine) and nLine[j][1] == ')':
                        if j + 1 < len(nLine):
                            if nLine[j + 1][1] == '{':
                                line_pointer = line_index - 1
                                token_pointer = 0
                                statements = []
                                while line_pointer < len(nLines):
                                    while token_pointer < len(nLines[line_pointer]):
                                        statements.append(nLines[line_pointer][token_pointer][1])
                                        if nLines[line_pointer][token_pointer][1] == '}':
                                            has_Closing = True
                                            if statements[-2] != '{':
                                                has_Statement = True
                                            else:
                                                has_Statement = False
                                        else:
                                            has_Closing = False
                                            
                                        token_pointer += 1
                                    
                                    line_pointer += 1
                                    token_pointer = 0
                                
                                if has_Closing == False:
                                    raise ValueError(f"Error: Missing closing bracket for block starting at line {line_no}.")

                                if has_Statement == False:
                                    raise ValueError(f"Error: Empty block after '{token_value}' at line {line_no}.")
                                
                        else:
                            raise ValueError(f"Error: Expected statement after '{token_value}' at line {line_no}.")
                        
                        if i + 1 < len(nLine) and nLine[i - 1][1] in {"[", ","}:
                            continue
                        elif i + 1 < len(nLine) and nLine[i - 1][1] != "trend":
                            raise ValueError(f"Error: Invalid format of function at line {line_no}.")
                    else:
                        raise ValueError(f"Error: Missing closing parenthesis after '{token_value}' at line {line_no}.")

                    k = 0
                    while k < len(params):
                        if params[k][0] not in {"Identifier", "Comma", "Reserved Word", "Integer", "Float Number"}:
                            raise ValueError(f"Error: Invalid parameter in '{token_value}' at line {line_no}.")
                        k += 1
                
                elif token_value == "trend":
                    if i + 1 < len(nLine) and nLine[i + 1][0] != "Function":
                        raise ValueError(f"Error: Invalid use of keyword '{token_value}' at line {line_no}.")

    except ValueError as e:
        print(f"Exception caught: {e}")
        return []

    return nLines


def parse(contents):
    """
    Example parse function that first lexes the input, 
    then runs the Parser on the flattened tokens.
    """
    # Step 1: Lexical Analysis
    lexer_output = lexer(contents)  # from your provided lexical analyzer
    if not lexer_output:
        return []

    # Step 2: Flatten the tokens into a single list
    token_list = flatten_and_convert(lexer_output)

    # Step 3: Syntax Analysis
    parser = Parser(token_list)
    try:
        ast = parser.parse_program()
        return ast
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return []