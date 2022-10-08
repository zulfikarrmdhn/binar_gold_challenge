from flask import Flask, request, jsonify
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from
from unidecode import unidecode
import re
import pandas as pd

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Gold Challenge Data Science Binar Academy'),
    'version': LazyString(lambda: '1'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

def replace_ascii(s):
    return unidecode(s)

def remove_ascii2(s):
    return re.sub(r'\\x[A-Za-z0-9./]+', ' ', unidecode(s))

def remove_n(s):
    return re.sub(r'\n', ' ', s)

def remove_punct(s):
    return re.sub(r'[^\w\d\s]+', ' ',s)

def remove_whitespace(s):
    return re.sub(r' +', ' ', s)

def cleansing(s):
    s = remove_ascii2(s)
    s = remove_n(s)
    s = remove_punct(s)
    s = remove_whitespace(s)
    return s

@swag_from("text_input.yml", methods=['POST'])
@app.route("/text_input", methods=['POST'])
def get_text():
    input_text = str(request.form["text"])
    output_text = cleansing(input_text)

    return_text = {
        "result":"Selamat, text anda sudah dibersihkan.",
        "input": input_text,
        "output": output_text
    }
    
    return jsonify(return_text)

@swag_from("upload_file.yml", methods=['POST'])
@app.route("/upload_file", methods=['POST'])
def upload_file():
    file = request.files["file"]
    df_csv = (pd.read_csv(file, encoding="latin-1"))
    df_csv['new_tweet'] = df_csv['Tweet'].apply(cleansing)

    Tweet = df_csv.Tweet.to_list()
    new_tweet = df_csv.new_tweet.to_list()

    return_file = {
        "result":"selamat, data anda berhasil diupload ke database.",
        "tweet": Tweet,
        "new_tweet": new_tweet
    }

    return jsonify(return_file)

if __name__ == "__main__":
    app.run(port=1234, debug=True)