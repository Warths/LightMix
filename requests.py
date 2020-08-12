



from machine import Timer
import socket
from requests_utils import code_string
import json

class WebServer:
  def __init__(self):
    """
    WebServer
    Decorates routes functions as @obj_name.route("route")
    """
    self.routes_register = {}
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    
  def run(self, debug=True):
    """
    :debug: Boolean | Log the connections 
    :asynchronous: Boolean | 
    """

    while True:
      # Waiting for client connection
      client, addr = self.socket.accept()
      if debug:
        print('Got a connection from %s' % str(addr))
    
      # Receiving a full request. May lead to memory error if request to large

      buffer = client.recv(1024)
      
      # Try to parse received requests.
      try:
        r = HTTPRequestParser(buffer)
      except:
        print("Improperly formatted request : {}".format(buffer))
        client.sendall('Connection: close\n\n')
        client.close()
        continue
        
      feeded = False
      
      for route in self.routes_register:
        if r.path == route:
          response = self.routes_register[route](r)
          response.feed(client)
          feeded = True

      if not feeded:
        try:
          Response(code=404, content="<h1>Not Found</h1><p>Ressources could not be located or doesn't exists</p>", feed=client)
        except:
          print("Connection error")



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
    return {k:v for k, v in self.parameters}

    


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
      
      
  def feed(self, client):
    """
    Sends a response to specified client then close it
    """
    try:
      client.send(self.code)
      client.send(self.content_type)
      client.send('Connection: close\n\n')  
      client.sendall(self.content)
    except:
      print("Error.")
    finally:
      client.close()      











