import sys
from .basic_pp import Basic1PrettyPrinter


def main():
    lc = Basic1PrettyPrinter()
    for file in sys.argv[1:]:
        with open(file) as f:
            lines = f.readlines()
        for line in lines:
            print(lc.makePretty(line.strip()))


if __name__ == "__main__":
    main()
