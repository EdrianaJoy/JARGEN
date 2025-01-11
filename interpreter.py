import re as regex

def lexer(contents):
    lines = contents.split('\n')
    for line in lines:
        chars = list(line)
        quote_count = 0
        tokens = []
        temp_str = ""
        for char in chars:
            # if not regex.match(r"[.a-zA-Z]+", char):
            #     tokens.append(temp_str)
            #     temp_str = ""

            if char == '"' or char == "'":
                quote_count += 1
            if quote_count % 2 == 0:
                in_quotes = False
            else:
                in_quotes = True

            if char == "(" or char == ")" or (char == " " and in_quotes == False):
                tokens.append(temp_str)
                temp_str = ""
                temp_str += char
                if temp_str == "(":
                    tokens.append(temp_str)
                    temp_str = ""
                # if char == " " and in_quotes == False:
                #     tokens.append(temp_str)
            else:
                temp_str += char
                
            # if char == " " and in_quotes == False:
            #     tokens.append(temp_str)
            #     temp_str = ""
            # else:
            #     temp_str += char
        tokens.append(temp_str)
        # items = []
        # for token in tokens:
        #     if regex.match(r"[.a-zA-Z]+", token):
        #         items.append(("string", token))

        print(tokens)

def parse(file):
    contents = open(file, "r").read()
    tokens = lexer(contents)
    return tokens