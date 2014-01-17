import os
import platform
import requests
import zipfile
import tempfile
from base64 import b64decode as decode

class Icon():
    def __init__(self, data):
        path = tempfile.mkstemp()[1]
        with open(path, "wb") as file:
            file.write(decode(data))
        self.file = path
        self.data = data

class Unzip():
    def __init__(self, file):
        self.zipfile = zipfile.ZipFile(file, "r")
        self.files = self.zipfile.infolist()
        self.current_file = ""
        
        self.progress = 0
        self.size = os.path.getsize(file)
        self.done = False
    
    def update(self):
        if len(self.files) == 0:
            self.stop()
            return
        
        file = self.files.pop()
        
        if os.path.isabs(file.filename):
            return
        self.current_file = file.filename
        dirname = os.path.dirname(file.filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        
        self.zipfile.extract(file)
        self.progress += file.compress_size
        return file.filename
    
    def stop(self):
        self.zipfile.close()
        self.done = True
    __del__ = stop

class Stream():
    def __init__(self, url, chunk_size=2**12):
        self.request = request = requests.get(url, stream=True, verify=False)
        self.stream = self.request.iter_content(chunk_size)
        
        self.size = int(request.headers["content-length"].strip())
        self.chunk_size = chunk_size
        
        self.progress = 0
        self.result = ""
        
        self.done = False
    
    def update(self):
        try:
            chunk = self.stream.next()
        except StopIteration:
            self.stop()
            return
        
        if chunk:
            self.result += chunk
            self.progress += self.chunk_size
        return chunk
    
    def stop(self):
        self.request.close()
        self.done = True
    __del__ = stop

class Download(Stream):
    def __init__(self, url, target, chunk_size=2**12):
        Stream.__init__(self, url, chunk_size)
        self.file = open(target, "wb")
    
    def update(self):
        chunk = Stream.update(self)
        if chunk:
            self.file.write(chunk)
        return chunk
    
    def stop(self):
        Stream.stop(self)
        self.file.close()
    __del__ = stop

class parse():
    def __init__(self, text):
        self.is_error = text[0] == "e"
        
        if self.is_error:
            self.error = text[1:]
        else:
            self.values = text[1:].split(";")
    
    def __bool__(self):
        return not self.is_error
    
    def __getitem__(self, key):
        return self.values[key]

def write_version(version):
    with open("version", "w") as file:
        file.write(version)

def read_version():
    version = None
    try:
        with open("version", "r") as file:
            version = file.readline()
    except:
        pass
    if not version:
        version = "0.0"
    return version

def get_platform_name():
    platforms = {"Windows":"Win32",
                 "Darwin":"Mac",
                 "Linux":"Linux"}
    return platforms[platform.system()]