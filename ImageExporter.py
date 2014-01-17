import os
from base64 import b64encode as encode

filename = raw_input("filename: ")
name = os.path.dirname(filename) + os.path.split(filename)[0] + ".py"
print "saving as <" + name + ">"

print "reading image"
with open(filename, "rb") as file:
    out = "image = \"\"\"" + encode(file.read().strip()) + "\"\"\""

print "saving file"
with open(name, "w") as file:
    file.write(out)

print "done"