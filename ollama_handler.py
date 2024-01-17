from langchain.llms import Ollama
import requests
import variables

def initialize_ollama():
    url = variables.url
    try:
        response = requests.get(url)
    except:
        url = variables.url2
    return Ollama(base_url=url,model=variables.model_name)


