import os
import html
import random

from flask import Flask, render_template, request
from google.cloud import translate_v2 as translate

app = Flask(__name__)

def get_client():
  return translate.Client.from_service_account_json(os.path.expanduser("~/service_account.json"))


def translate_text(translate_client, source, target, text):
  result = translate_client.translate(text, target_language=target, source_language=source)
  return html.unescape(result["translatedText"])


@app.route('/')
def form():
  return render_template('bad_translator.html')


@app.route('/bad_translator/', methods=['POST', 'GET'])
def data():
  if request.method == 'POST':
    input = request.form["inputText"]

    # Get the list of languages that Google Translate supports
    translate_client = get_client()
    results = translate_client.get_languages()
    supported_languages = [lang["language"] for lang in results]
    supported_languages.remove("en")

    # Random chain of languages
    targets = list(random.choices(supported_languages, k=9)) + ["en"]
    print(f"Translating to {targets}")

    # Translate
    curr = input
    source = "en"
    for target in targets:
        curr = translate_text(translate_client, source, target, curr)
        source = target

    return render_template('bad_translator.html', input=input, output=curr)


if __name__ == '__main__':
  app.run(debug=True)
