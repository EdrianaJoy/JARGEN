from sys import *
from test123 import *

if __name__ == '__main__':
    # if len(argv) > 1:
    #     print("\n".join([str(item) for item in parse(argv[1])]))
    # else:
    #     print("No input provided.")

    code_sample = """
    flex x = 10;
    sus(x > 5){;
        x = 4
    ;}
    """

    print(parse(code_sample))