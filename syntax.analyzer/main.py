from sys import *
from interpreter import *
from syntax_analyzer import *

def syntax_analyze(source_code):
    # 1) Call parse() function which wraps the lexer
    token_lines = parse(source_code)  
    if not token_lines:
        print("Lexical analysis encountered errors or returned no tokens.")
        return None

    # 2) Create the syntax analyzer
    analyzer = SyntaxAnalyzer(token_lines)
    parse_tree = analyzer.parse_program()

    # 3) Check for errors
    if analyzer.error_count > 0:
        print(f"Syntax analysis encountered {analyzer.error_count} error(s).")
        return None
    else:
        # print("Syntax analysis completed successfully!")
        return parse_tree

def print_parse_tree(node, indent=0):
    if not node:
        return
    prefix = "  " * indent

    if node.value:
        print(f"{prefix}{node.node_type}({node.value})")
    else:
        print(f"{prefix}{node.node_type}")
    for child in node.children:
        print_parse_tree(child, indent + 1)

if __name__ == "__main__":

    if len(argv) > 1:
        # print("\n=== PARSE TREE ===")
        print(print_parse_tree(syntax_analyze(argv[1])))
    else:
        print("No input provided.")