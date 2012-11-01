from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import socket

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        resp = """<?xml version="1.0" encoding="utf-8"?>
            <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
                <channel>
                    <title>Feed Title</title>
                    <link>Feed Link</link>
                    <description>Feed descrition</description>
                    <item>
                        <title>Item 1 title<</title>
                        <link>Item 1 link</link>
                        <description>Item 1 description</description>
                    </item>
                </channel>
            </rss>
        """
        self.send_response(200)
        self.end_headers()
        self.wfile.write(resp)
        self.wfile.write('\n')

    def log_message(self, *args):
        pass

class TestProxy(Thread):

    def __init__(self, routes, address):
        Thread.__init__(self)
        self.daemon = True
        self.routes = routes
        self.httpd = HTTPServer(address, ProxyHandler)
        self.httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        while True:
            self.httpd.handle_request()
