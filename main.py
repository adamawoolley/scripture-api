from flask import Flask, render_template, request
from scraper import get_chapter
from info import *
import requests

app = Flask('app')

@app.route('/')
def hello_world():
    return render_template('home.html', langs=langs, testaments=testaments, books=books)

@app.route('/get_chapter', methods=["GET"])
def chapter():
    testament = request.args.get("testament")
    book = request.args.get("book")
    chapter = request.args.get("chapter")
    lang = request.args.get("lang")
    gotted_chapter = get_chapter(testament, book, chapter, lang)
    print(gotted_chapter)
    print(dir(gotted_chapter[0]))
    return "".join([f"<p>{p}</p>" for p in get_chapter(testament, book, chapter, lang)])

@app.route('/b')
def b():
    return requests.get('https://www.churchofjesuschrist.org/study/scriptures/ot/gen/1?lang=por').text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
