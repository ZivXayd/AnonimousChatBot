import requests


class Translator:
    def __init__(self):
        print('# модуль переводчика инициализирован.')

    def translate(self, text: str) -> str:
        url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"

        querystring = {"langpair": "en|ru", "q": text, "mt": "1", "onlyprivate": "0", "de": "a@b.c"}

        headers = {
            "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com",
            "X-RapidAPI-Key": "e02535a854mshb0b4836483cbeeep130114jsnd568d7dbee6c"
        }

        response = requests.request("GET", url, headers=headers, params=querystring).json()

        return response['responseData']['translatedText']
