import argparse 
import socket


def make_request(
    host,
    port=80,
    path="/",
    method="GET",
    headers=None,
    body=None,
    timeout=10,
):
    s = socket.socket()
    s.settimeout(timeout)

    try:
        s.connect((host, port))

        # Creating the Request structure
        request = f"{method} {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        if headers:
            for key, value in headers.items():
                request += f"{key}: {value}\r\n"
        if body:
            request += f"Content-Length: {len(body)}\r\n"
            request += "\r\n"
            request += body
        else:
            request += "\r\n"

        s.sendall(request.encode())

        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        decoded_response = response.decode()

        headers, body = decoded_response.split("\r\n\r\n", 1)
        headers = headers.split("\r\n")
        status_code = int(headers[0].split(" ")[1])

        header_dict = {}
        for header in headers[1:]:
            key, value = header.split(": ", 1)
            header_dict[key] = value
        return status_code, header_dict, body

    finally:
        s.close()


def fetch_url(url):
    status_code, headers, body = make_request(
        host=url,
    )
    print(f"Status Code: {status_code}")
    print("Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")
    print("Body:")
    print(body[:1000])  # Print only the first 1000 characters of the body



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
