import argparse 


def fetch_url(url):
    return "URL Fetched"


def main():
    parser = argparse.ArgumentParser(
        prog="Go2Web",
        description="Command Line Program for HTTP requests",
        epilog="use the -h anytime you need some help",
    )
    parser.add_argument(
        "-u",
        "--url",
        help="URL to fetch",
    )
    parser.add_argument(
        "-s",
        "--search-term",
        help="Term to search for",
    )

    args = parser.parse_args()

    if args.url:
        fetch_url(args.url)
    elif args.search_term:
        print("--search-term is not yet available")
    else:
        parser.print_help()


if __name__=="__main__":
    main()
