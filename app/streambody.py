#encoding: utf-8
class StreamBody():
    def __init__(self, rt):
        self._rt = rt

    def get_raw_stream(self):
        return self._rt.raw

    def get_stream(self, chunk_size=1024):
        return self._rt.iter_content(chunk_size=chunk_size)

    def get_stream_to_file(self, file_name, auto_decompress=False):
        use_chunked = False
        if 'Content-Length' in self._rt.headers:
            content_len = int(self._rt.headers['Content-Length'])
        elif 'Transfer-Encoding' in self._rt.headers and self._rt.headers['Transfer-Encoding'] == "chunked":
            use_chunked = True
        else:
            raise IOError("download failed without Content-Length header or Transfer-Encoding header")
        use_encoding = False
        if 'Content-Encoding' in self._rt.headers:
            use_encoding = True

        file_len = 0
        with open(file_name, 'wb') as fp:
            if use_encoding and not auto_decompress:
                chunk = self._rt.raw.read(1024)
                while chunk:
                    file_len += len(chunk)
                    fp.write(chunk)
                    chunk = self._rt.raw.read(1024)
            else:
                for chunk in self._rt.iter_content(chunk_size=1024):
                    if chunk:
                        file_len += len(chunk)
                        fp.write(chunk)
        if not use_chunked and not (use_encoding and auto_decompress) and file_len != content_len:
            raise IOError("download failed with incomplete file")
if __name__ == "__main__":
    pass