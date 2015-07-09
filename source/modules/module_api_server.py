#!/usr/bin/python

from time import sleep
import logging
import SocketServer
from utilities import debug_print
import config


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

class ModuleAPIRequestHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('ModuleAPIRequestHandler')
        self.logger.debug('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug('handle')

        # Echo the back to the client
        data = self.request.recv(1024)
        self.logger.debug('recv()->"%s"', data)
        self.request.send(data)
        return

    def finish(self):
        self.logger.debug('finish')
        return SocketServer.BaseRequestHandler.finish(self)

class ModuleAPIServer(SocketServer.TCPServer):
    
    def __init__(self, server_address, handler_class=ModuleAPIRequestHandler):
        self.logger = logging.getLogger('ModuleAPIServer')
        self.logger.debug('__init__')
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug('server_activate')
        SocketServer.TCPServer.server_activate(self)
        return

    def serve_forever(self, queue):
        debug_print("Warm Hello from module_api_server! :)")
        self.logger.debug('waiting for request')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        while True:
            if config.SHUT_DOWN == 1:
                debug_print("module_api_server: going to exit")
                break
        
            debug_print("module_api_server: going to sleep for a bit (SHUT_DOWN = %d)" % config.SHUT_DOWN)
            sleep(2)
            self.handle_request()
    
        debug_print("module_api_server: exiting")
        result = (True, None)
        queue.put(result)
            
        return

    def handle_request(self):
        self.logger.debug('handle_request')
        return SocketServer.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug('server_close')
        return SocketServer.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        return SocketServer.TCPServer.close_request(self, request_address)

if __name__ == '__main__':
    import socket
    from threading import Thread
    from Queue import Queue

    queue = Queue()
    address = (config.HOSTNAME, config.PORT)
    server = ModuleAPIServer(address, ModuleAPIRequestHandler)

    t = Thread(target=server.serve_forever, args=(queue, ))
    t.setDaemon(True) # don't hang on exit
    t.start()

    logger = logging.getLogger('client')
    logger.info('Server on %s:%s', config.HOSTNAME, config.PORT)

    # Connect to the server
    logger.debug('creating socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug('connecting to server')
    s.connect((config.HOSTNAME, config.PORT))

    # Send the data
    message = 'Hello, world'
    logger.debug('sending data: "%s"', message)
    len_sent = s.send(message)

    # Receive a response
    logger.debug('waiting for response')
    response = s.recv(len_sent)
    logger.debug('response from server: "%s"', response)

    # Clean up
    logger.debug('closing socket')
    s.close()
    logger.debug('done')
    server.socket.close()