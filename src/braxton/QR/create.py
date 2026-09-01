import qrcode

def generate_QR_code(domain:str):

    qr = qrcode.QRCode(border=1)
    qr.add_data("https://"+domain)
    qr.make()

    qr.print_ascii(invert=True)

"""
generate_QR_code("example.com")
"""