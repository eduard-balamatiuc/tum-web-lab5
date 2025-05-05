import argparse 
import socket

from bs4 import BeautifulSoup


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
        request += "Connection: close\r\n"

        # For this specific exercise I'm not actually using the headers when sending the request
        # but for the sake of completeness of the function will leave it here
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

        header_end = response.find(b'\r\n\r\n')
        
        if header_end == -1:
            # No header/body separator found
            return None, None, None
            
        headers_data = response[:header_end]
        body_data = response[header_end + 4:]
        
        # Decode headers safely
        headers_text = headers_data.decode('utf-8', errors='replace')
        headers = headers_text.split("\r\n")
        
        # Parse status code
        status_line = headers[0]
        status_parts = status_line.split(" ", 2)
        if len(status_parts) >= 2:
            status_code = int(status_parts[1])
        else:
            status_code = None
            
        # Parse headers into dictionary
        header_dict = {}
        for header in headers[1:]:
            if ": " in header:
                key, value = header.split(": ", 1)
                header_dict[key] = value
        
        # Try to decode the body - handle potential errors
        try:
            body_text = body_data.decode('utf-8', errors='replace')
        except Exception as e:
            body_text = f"[Error decoding body: {str(e)}]"
            
        return status_code, header_dict, body_text

    finally:
        s.close()

def get_protocol_host_port_path_from_url(url):
    if "://" in url:
        protocol, rest = url.split("://", 1)
    else:
        protocol, rest = "http", url
        
    if "/" in rest:
        host, path = rest.split("/", 1)
        path = "/" + path
    else:
        host = rest
        path = "/"
    
    port = 80
    if ":" in host:
        host, port_str = host.split(":", 1)
        port = int(port_str)

    return protocol, host, port, path


def postprocess_request_body(body):
    soup = BeautifulSoup(body, "html.parser")

    text = soup.get_text(separator=" ", strip=True)

    return text

def fetch_url(url):
        
    protocol, host, port, path = get_protocol_host_port_path_from_url(url)
    
    status_code, headers, body = make_request(
        host=host,
        port=port,
        path=path
    )
    
    if status_code is None:
        print("Failed to get a valid response")
        return
        
    print(f"Status Code: {status_code}")
    print("Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")
    
    postprocessed_body = postprocess_request_body(body)
    print("Body:")
    print(postprocessed_body)


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