import uos

def read(filename, default=None):
  """
  Read a file.
  :filename: Name of the file
  :return: str if file exists else None
  """
  try:
      uos.mkdir("flash")
      uos.mkdir("flash2")
  except:
      pass
  try:
      filename = "{}/{}".format("flash", filename)
      f = open(filename, "r")
      content = f.read()
      f.close()
      return content
  except:
      return default

def write(filename, content):
  """
  Write a file
  :filename: Name of the file
  :content: Content to write
  """
  filename = "{}/{}".format("flash", filename)
  f = open(filename, "w")
  f.write(str(content))
  f.close()
  
def erase_flash():
    uos.rmdir("flash")