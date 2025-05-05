# Lab 5 - Websockets HTTP Client Implementation

A custom HTTP client implementation built from scratch using TCP sockets without relying on built-in or third-party HTTP request libraries.

![Demo](assets/showcase.gif)

## Project Description

This project implements a command-line HTTP client called `go2web` that can make direct HTTP requests and search using a search engine. The application is built without using any built-in or third-party libraries for HTTP requests, implementing the HTTP protocol directly over TCP sockets.

## Features

- Make HTTP requests to specified URLs
- Search the web using a search engine
- Human-readable response formatting (strips HTML tags)
- HTTP redirects support
- Simple HTTP cache mechanism
- Content negotiation (supports both JSON and HTML content types)
- Interactive navigation through search results

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tum-web-lab5.git
cd tum-web-lab5

# Make sure you have uv installed
uv install

# Build the project
uv build

# install the package
uv add .

# run the project
uv run go2web -h
```

### Examples

```bash
# Make a request to example.com
uv run go2web -u https://example.com

# Search for "Moldova University"
uv run go2web -s 'Moldova University'

# Get help
uv run go2web -h
```

## Implementation Details

The application is built with [python] and implements:

- Custom TCP socket connections for HTTP requests
- HTTP/1.1 protocol implementation
- HTML parsing for human-readable output
- Search engine integration
- Command-line argument parsing

## Extra Features Implemented

- HTTP redirects following
- Interactive navigation through search results
- HTTP caching mechanism to improve performance
- Content negotiation for handling different response types (JSON/HTML)

## Project Structure

```
├── [Main source files]
├── [Additional modules]
├── assets/
│   └── showcase.gif
└── [Other project files]
```

## Development Notes

This project was developed as part of the Web Programming course at Technical University of Moldova.

The main goal behind the project was to understand the logic behind HTTP requests and responses, and how to implement them from scratch, not to write the cleanest code, in fact I would suggest to use this code as reference of dirty code.

Also here are some useful links I've used that helped me a lot:

https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Content_negotiation
https://docs.python.org/3/library/socket.html#socket.socket.settimeout
https://docs.python.org/3/library/argparse.html
https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages#anatomy_of_an_http_message
