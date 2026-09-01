import base64

class Encoder:

    @staticmethod
    def encode_text(text):
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def decode_text(data):
        return base64.b64decode(data).decode()

    @staticmethod
    def encode_file(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @staticmethod
    def decode_file(data, output):
        with open(output, "wb") as f:
            f.write(base64.b64decode(data))