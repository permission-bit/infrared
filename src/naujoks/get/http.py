import requests
from pathlib import Path

def make_url(parts):
    return "https://" + "/".join(parts)

url = make_url(["example.com", "login"])

print(url)

#############################

def get_html(domain:str):
    url = f"https://{domain}"

    response = requests.get(url)
    return response.text

#############################
def get_status_code(domain:str):
    url = f"https://{domain}"

    response = requests.get(url)
    return response

#############################
def download(domain:str, file:str, path:Path):
    url = f"https://{domain}/{file}"

    response = requests.get(url)
    with open(path, "wb") as f:
        f.write(response.content)

#############################



    
