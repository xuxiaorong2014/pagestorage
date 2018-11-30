#encoding: utf-8
import os
def content_type_of(filename):
    file_ext = os.path.splitext(filename)[-1]
    if file_ext == ".ai":
        return "application/postscript"
    elif file_ext == ".aif":
        return "audio/aiff"
    elif file_ext == ".aifc":
        return "audio/aiff"
    elif file_ext == ".aiff":
        return "audio/aiff"
    elif file_ext == ".asp":
        return "text/asp"
    elif file_ext == ".bmp":
        return "application/x-bmp"
    elif file_ext == ".gif":
        return "image/gif"
    elif file_ext == ".htm":
        return "text/html"
    elif file_ext == ".html":
        return "text/html"
    elif file_ext == ".ico":
        return "image/x-icon"
    elif file_ext == ".jfif":
        return "image/jpeg"
    elif file_ext == ".jpeg":
        return "image/jpeg"
    elif file_ext == ".jpg":
        return "image/jpeg"
    elif file_ext == ".js":
        return "application/x-javascript"
    elif file_ext == ".js":
        return "application/x-javascript"
    elif file_ext == ".css":
        return "text/css"
    elif file_ext == ".svg":
        return "text/xml"
    else:
        return "application/octet-stream"
 
  