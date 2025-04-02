import argparse

parser = argparse.ArgumentParser(
    prog="Go2Web",
    description="Command Line Program for HTTP requests",
    epilog="use the -h anytime you need some help",
)

parser.add_argument(
    "-u",
    "--url",
)

parser.add_argument(
    "-s",
    "--search-term",
)