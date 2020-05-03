from selenium import webdriver
from bs4 import BeautifulSoup as BS
from requests import get
from urllib.request import urlopen

def get_langs():
    soup = BS(get('https://www.churchofjesuschrist.org/languages?lang=eng').text, 'html.parser')
    # Sort all the langauages into dict with name and 3 char shorthand for url
    return {a.get('data-lang'): a.contents[0] for a in [li.findChild('a') for li in soup.findAll('li')]}

def get_testaments():
    soup = BS(get(f'https://www.churchofjesuschrist.org/study/scriptures').text, 'html.parser')
    # Get the testament name and url and img link for every testament
    return {a.get('href').split('?')[0]: a.text for a in elem_with_attr(soup, 'div', ('class', 'tileRow-3ETk4'))[0].findAll('a')}


#def get_testaments(lang='eng'):
#    soup = BS(get(f'https://www.churchofjesuschrist.org/study/scriptures?lang={lang}').text, 'html.parser')
#    # Get the testament name and url and img link for every testament
#    return {a.text: (a.get('href').split('?')[0], a.find('img').get('src')) for a in elem_with_attr(soup, 'div', ('class', 'tileRow-3ETk4'))[0].findAll('a')}

#def get_testaments2(lang, testament):
#    soup = BS(get(f'https://churchofjesuschrist.org{testament}?lang={lang}').text, 'html.parser')
#    # Get the book name and chapters names with url to each chapter
#    return {book.find('a').text: [(chptr.text, chptr.find('a').get('href')) for chptr in book.findAll('li')] for book in nav.elem_with_attr(soup, 'nav', ('class', 'tableOfContents-3u3H3'))[0].find('ul').findAll('li')}

def elem_with_attr(soup, elem, attr):
    return [elm for elm in soup.findAll(elem) if elm.has_attr(attr[0]) and attr[1] in elm.get(attr[0])]

def get_books_from_testament(testament,lang='eng'):

    options = webdriver.FirefoxOptions()
    options.binary_location = "/usr/bin/firefox"
    driver = webdriver.Firefox(options=options)
    driver.get(f'https://churchofjesuschrist.org{testament}?lang={lang}')
    svgs = [svg for svg in driver.find_elements_by_tag_name('svg') if svg.get_attribute('style') == 'width: 1em; height: 1em;']#[1:]
    [svg.click() for svg in svgs]

    soup = BS(driver.page_source, 'html.parser')
    nav = elem_with_attr(soup, 'nav', ('class', 'tableOfContents-3u3H3'))[0]
    books = {}

    for child in nav.find('ul').children:
        try:
            if child.name == 'li':
                if child.find('ul'):
                    chapters = child.find('ul').findAll('a')
                    books[child.find('a').text.strip()] = (chapters[0].get('href').split('?')[0].split('/')[-2], str(len(chapters)))
                else:
                    books[child.text.strip()] = (child.find('a').get('href').split('?')[0].split('/')[-1], '1')
        except:
            pass

        #        for chapter in a.find_next_sibling().findAll('a'):
        ###            print(chapter)
        #            if chapter.has_attr('href'):
        #                books[a.text].append(chapter.get('href').split('?')[0])

    return books

     #books = {a.text: [(chapter.text, chapter.get('href').split('?')[0]) for chapter in a.find_next_sibling().findAll('a')] for a in nav}

def get_chapter(testament, book, chapter, lang):
    try:
        url = f'https://churchofjesuschrist.org{testament}/{book}/{chapter}?lang={lang}'
        html = urlopen(url).read()
        soup = BS(html, 'html.parser')
        return [p.text for p in elem_with_attr(soup, 'div', ('class', 'body'))[0].findAll('p')]
    except:
        return ["Sorry, but we do not have that chapter in that language"]

if __name__ == "__main__":
    from info import testaments
    books = {}
    for testament, name in testaments.items():
        books[name] = get_books_from_testament(testament)
    print(books)
