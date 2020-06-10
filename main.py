from flask import Flask, request, jsonify, url_for, render_template
from scraper import scriptures
from json import dumps

script = scriptures(['bofm'], False)
app = Flask('app')

@app.route('/', methods=['GET'])
def hello_world():
    print('Home requested\n\n\n\n')
    return render_template('home.html')
    #return render_template('home.html', langs=langs, testaments=testaments, books=books)

@app.route('/api/<book>/<int:chapter>', methods=['GET'])
def get_chapter(book, chapter):

    langs = request.args.get('langs').split()
    response = []

    for lang in langs:
        response.append({'name': script.langs[lang], 'short': lang, 'chapter': script.get_chapter(lang, book, chapter)})

    # I have to use json.dumps instead of flask.jsonify because jsonify doesn't support serializing arrays
    # because it is a secruity vunerability in ECMAScript4 that was fixed in ECMAScript5
    return dumps(response)

#@app.route('/api/<lang>/')
#@app.route('/api/<lang>/<vol>/')
#@app.route('/api/<lang>/<vol>/<testament>/')
#@app.route('/api/<lang>/<vol>/<testament>/<int:chapter>/')
#def get_chapter(lang, vol, testament, chapter):
#    return jsonify(script.get_chapter(lang, vol, testament, chapter))
#@app.route('/api/<lang>/<vol>/<testament>/<int:chapter>/<int:verse>/')
#def get_verse(lang, vol, testament, chapter, verse):
#    return jsonify(script.get_verse(lang, vol, testament, chapter, verse))

#@app.route('/get_chapter', methods=["GET"])
#def chapter():
#    testament = request.args.get("testament")
#    book = request.args.get("book")
#    chapter = request.args.get("chapter")
#    lang = request.args.get("lang")
#    gotted_chapter = get_chapter(testament, book, chapter, lang)
#    print(gotted_chapter)
#    print(dir(gotted_chapter[0]))
#    return "".join([f"<p>{p}</p>" for p in get_chapter(testament, book, chapter, lang)])
#
#@app.route('/b')
#def b():
#    return requests.get('https://www.churchofjesuschrist.org/study/scriptures/ot/gen/1?lang=por').text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080', debug=True)
