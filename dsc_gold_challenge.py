from flask import Flask, request, jsonify
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from
from unidecode import unidecode
import re
import pandas as pd
import sqlite3

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
    input_text = request.get_json()
    output_text = cleansing(input_text['text'])
    
    db1 =  sqlite3.connect('gold_challenge_text_input.db', check_same_thread=False)
    db1.execute("CREATE TABLE IF NOT EXISTS clean_text (input_text, output_text)")
    query_text = "INSERT INTO clean_text (input_text, output_text) values(?, ? )"
    val = (input_text['text'], output_text)
    db1.execute(query_text, val)
    clean_text_file = pd.read_sql_query("SELECT * FROM clean_text", db1)
    clean_text_file.to_csv("Clean_Text_Input.csv")
    db1.commit()
    db1.close()

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
    df_dirty = (pd.read_csv(file, encoding="latin-1"))

    db2 =  sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)

    df_dirty.to_sql("dirty_tweet", con=db2, index=False, if_exists='append')

    dirty_tweet_file = pd.read_sql_query("SELECT * FROM dirty_tweet", db2)
    dirty_tweet_file.to_csv("Dirty_Tweet.csv")

    df_clean = df_dirty.copy()
    df_clean['new_tweet'] = df_clean['Tweet'].apply(cleansing)

    db2 =  sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)
    df_clean.to_sql("clean_tweet", con=db2, index=False, if_exists='append')

    clean_tweet_file = pd.read_sql_query("SELECT * FROM clean_tweet", db2)
    clean_tweet_file.to_csv("Clean_Tweet.csv")

    db2.close()

    Tweet = df_clean.Tweet.to_list()
    new_tweet = df_clean.new_tweet.to_list()

    return_file = {
        "result":"Selamat, data bersih anda berhasil diupload ke database.",
        "tweet": Tweet,
        "new_tweet": new_tweet
    }

    return jsonify(return_file)

if __name__ == "__main__":
    app.run(port=1234, debug=True)