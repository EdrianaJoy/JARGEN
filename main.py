from sys import *
from interpreter import *

if __name__ == '__main__':
    if len(argv) > 1:
        print("\n".join([str(item) for item in parse(argv[1])]))  # Output the result of parse
    else:
        print("No input provided.")


# source .venv/Scripts/activate
# django-admin startproject myproject
# cd myproject
# py manage.py runserver