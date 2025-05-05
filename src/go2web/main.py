import argparse 
import os
import socket
import time
import json
import urllib.parse
from bs4 import BeautifulSoup

if not os.path.exists("cache.json"):
    with open("cache.json", "w") as f:
        json.dump({}, f)
with open("cache.json", "r") as f:
    CACHE = json.load(f)

def make_request(
    host,
    port=80,
    path="/",
    method="GET",
    headers=None,
    body=None,
    timeout=10,
    accept=None,
):
    s = socket.socket()
    s.settimeout(timeout)

    try:
        s.connect((host, port))

        # Creating the Request structure
        request = f"{method} {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Connection: close\r\n"
        if accept:
            request += f"Accept: {accept}\r\n"
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

def follow_redirects(host, port, path, max_redirects=5, accept=None):
    redirect_count = 0
    
    while redirect_count < max_redirects:
        status_code, headers, body = make_request(host=host, port=port, path=path, accept=accept)
        
        # Check if response is a redirect
        if status_code in (301, 302, 303, 307) and 'Location' in headers:
            redirect_url = headers['Location']
            print(f"Following redirect to: {redirect_url}")
            
            # Parse the new URL
            protocol, host, port, path = get_protocol_host_port_path_from_url(redirect_url)
            redirect_count += 1
        else:
            # Not a redirect, return the response
            return status_code, headers, body
    
    print(f"Warning: Maximum number of redirects ({max_redirects}) followed.")
    return status_code, headers, body


def postprocess_request_body(body, content_type=None):
    # Check if we have JSON content
    if content_type and 'application/json' in content_type:
        try:
            # Parse JSON content
            data = json.loads(body)
            return data  # Return the parsed JSON object
        except json.JSONDecodeError:
            print("Warning: Content-Type indicates JSON but couldn't parse it")
    
    # Default HTML processing
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text

def store_in_cache(url, status_code, headers, body):
    CACHE[url] = (time.time(), status_code, headers, body)
    with open("cache.json", "w") as f:
        json.dump(CACHE, f)

def fetch_default(url, accept=None):
    print(f"Fetching URL: {url}")
    protocol, host, port, path = get_protocol_host_port_path_from_url(url)
    status_code, headers, body = follow_redirects(host=host, port=port, path=path, accept=accept)
    
    store_in_cache(url, status_code, headers, body)
    return status_code, headers, body

def try_fetch_from_cache(url, accept=None):
    # Check if the URL is in the cache
    if url in CACHE:
        print("Fetching from cache...")
        cache_timeout, status_code, headers, body = CACHE[url]
        if time.time() - cache_timeout < 60:
            return status_code, headers, body
        else:
            print("Cache expired.")
            status_code, headers, body = fetch_default(url, accept)
    else:
        print("URL not found in cache.")
        status_code, headers, body = fetch_default(url, accept)

    return status_code, headers, body


def fetch_url(url, accept="text/html,application/json;q=0.9"):
    # Check if the URL is in the cache
    status_code, headers, body = try_fetch_from_cache(url, accept)

    if status_code is None:
        print("Failed to get a valid response")
        return
        
    print(f"Status Code: {status_code}")
    print("Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")
    
    # Get content type from headers
    content_type = headers.get('Content-Type', '')
    
    # Process based on content type
    processed_body = postprocess_request_body(body, content_type)
    
    print("Body:")
    if isinstance(processed_body, (dict, list)):
        # Pretty print JSON data
        print(json.dumps(processed_body, indent=2))
    else:
        # Print text as usual
        print(processed_body)

def parse_search_results(body, result_count=10):
    soup = BeautifulSoup(body, "html.parser")
    results = []
    
    # Look for result links in DuckDuckGo Lite format
    for i, a in enumerate(soup.select('a.result-link')):
        if i >= result_count:
            break
            
        # Get the link and title
        link = a.get('href')
        title = a.get_text(strip=True)

        # Extract the actual URL from DuckDuckGo's redirect link
        if link.startswith("//duckduckgo.com/l/?uddg="):
            # Remove the leading //duckduckgo.com/l/?uddg=
            encoded_url = link.split("uddg=")[1]
            if "&" in encoded_url:
                encoded_url = encoded_url.split("&")[0]
            # URL-decode the actual destination
            actual_url = urllib.parse.unquote(encoded_url)
            link = actual_url
        
        # Try to find the snippet
        snippet = ""
        snippet_elem = a.find_next('td', class_='result-snippet')
        if snippet_elem:
            snippet = snippet_elem.get_text(strip=True)
        
        results.append({
            'title': title,
            'link': link,
            'snippet': snippet
        })
    
    return results

def search_term(term):
    # I tried duckduckgo.com but I found it that using the lite version would be easier
    search_url = f"https://lite.duckduckgo.com/lite/?q={term.replace(' ', '+')}"
    
    status_code, headers, body = try_fetch_from_cache(search_url)
    
    if status_code is None:
        print("Failed to get a valid response")
        return []
    
    results = parse_search_results(body)
    
    print(f"Search Results for '{term}':")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Link: {result['link']}")
        if 'snippet' in result and result['snippet']:
            print(f"   {result['snippet']}")
        print()
    
    return results



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
    parser.add_argument(
        "-a",
        "--accept",
        help="Accepted content types (e.g. 'application/json,text/html')",
        default="text/html,application/json;q=0.9",
    )

    args = parser.parse_args()

    if args.url and args.search_term:
        fetch_url(args.url, accept=args.accept)
        search_term(args.search_term)
    elif args.url:
        fetch_url(args.url, accept=args.accept)
    elif args.search_term:
        search_term(args.search_term)
    else:
        parser.print_help()


if __name__=="__main__":
    main()