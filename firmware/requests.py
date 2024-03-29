from machine import Timer
import socket
from request_utils import code_string
import json
from sys import platform

if platform == "esp32":
  import _thread as thread
else:
  thread = None


class WebServer:
  def __init__(self):
    """
    WebServer
    Decorates routes functions as @obj_name.route("route")
    """
    self.routes_register = {}
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind(('', 80))
    self.socket.listen(5)

  def route(self, name):
    """
    Used as a decorator to register routes.
    """

    def func_wrapper(func):
      self.routes_register[name] = func
      return func

    return func_wrapper

  def run(self, debug=True, threaded=True):
    """
    :debug: Boolean | Log the connections 
    :asynchronous: Boolean | 
    """
    if threaded:
      if thread:
        thread.start_new_thread(self.run, (debug, False))
        return

    while True:
      # Waiting for client connection
      client, addr = self.socket.accept()
      if debug:
        print('[WebServer] Got a connection from {}'.format(addr))

      # Receiving a full request. May lead to memory error if request to large
      try:
        buffer = client.recv(1024)
      except Exception as err:
        print("[WebServer] Exception: {}".format(err))
        client.close()

        # Try to parse received requests.
      try:
        r = HTTPRequestParser(buffer)
      except:
        print("[WebServer] Improperly formatted request : {}".format(buffer))
        client.sendall('Connection: close\n\n')
        client.close()
        continue

      feeded = False

      # Looking for a route
      for route in self.routes_register:
        if r.path == route:
          # Executing route if found a match
          try:
            response = self.routes_register[route](r)
          # If route failed to be executed, returning error 500
          except:
            response = Response(code=500,
                                content="<h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request.</p>")

          # Sending response
          response.feed(client, addr)
          feeded = True
          break

      # Feeding client with a 404 response if couldn't find any matching response
      if not feeded:
        try:
          Response(code=404, content="<h1>Not Found</h1><p>Ressources could not be located or doesn't exists</p>",
                   feed=client)
        except:
          print("[WebServer] Connection error")


class HTTPRequestParser:
  def __init__(self, r):
    """
    HTTP Request class. All elements callables
    :r: bytes | raw http request
    """
    # Splitting Lines
    r = r.decode()
    r = r.split("\r\n")

    # Getting Method, Path and Protocol from first header
    self.method, self.path, self.protocol = r.pop(0).split()

    try:
      self.raw_params = self.path.split("?")[1]
    except:
      self.raw_params = None

    # Parsing URL parameters
    self.parameters = self.parse_parameters()
    self.path = self.path.split("?")[0]
    # Parsing other headers as Name: Value
    self.headers = self.parse_headers(r)

  def parse_headers(self, header_list):
    """
    :header_list: list, Http request without method/path/protocol, splitted by lines
    :return: Dict ; headers by name: value
    """
    headers = {}
    for header in header_list:
      try:
        # Seperating header strings as name: value
        slices = header.split(": ", 1)
        headers[slices[0]] = slices[1]
      except:
        # Some headers may be improperly formatted. Ignoring them.
        pass
    return headers

  def parse_parameters(self):
    """
    Returns: List of tuples. Key of value may be empty
    """
    formatted_parameters = []

    parameters = self.path.split("?")

    # Checking if parameters are present
    if len(parameters) > 1:
      parameters = parameters[1]
      # Splitting parameters into fragments 
      fragments = parameters.split("&")
      # Adding fragments to the returned list
      for frag in fragments:
        key_value = frag.split("=", 1)
        # Parameters doesn't have value
        if len(key_value) == 1:
          formatted_parameters.append((key_value[0], ''))
        # Parameters has value
        else:
          formatted_parameters.append((key_value[0], key_value[1]))
    return formatted_parameters

  def params_dict(self):
    return {k: v for k, v in self.parameters}


class Response:
  def __init__(self, code=200, content_type="auto", content="Hello world", feed=None):
    """
    Response object. can be used to build HTTP responses
    :code: Int ; Status code
    :content_type: Str ; content type
    :content: Str (html/text) or Dict (json/applications)
    """
    self._code = code
    self._content_type = content_type
    self._content = content

    if feed:
      self.feed(feed)

  @property
  def code(self):
    """
    Ready to use code header
    """
    return 'HTTP/1.1 {} {}\n'.format(self._code, code_string(self._code))

  @property
  def content_type(self):
    """
    Ready to use content-type header
    """
    if self._content_type == "auto":
      if isinstance(self._content, dict):
        return 'Content-Type: application/json\n'
      else:
        return 'Content-Type: text/html\n'

  @property
  def content(self):
    """
    Ready to use content header
    """
    if isinstance(self._content, dict):
      return json.dumps(self._content)
    else:
      return self._content

  def feed(self, client, addr="Unknown"):
    """
    Sends a response to specified client then close it
    """
    try:
      client.send(self.code)
      client.send(self.content_type)
      client.send('Connection: close\n\n')
      client.sendall(self.content)
    except Exception as e:
      print("[WebServer] Error ({})".format(e))
    else:
      print("[WebServer] Ended connection with {}".format(addr))
    finally:
      client.close()
