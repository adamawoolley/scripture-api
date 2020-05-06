from selenium import webdriver
from bs4 import BeautifulSoup as BS
from requests import get
from urllib.request import urlopen

class scriptureScraper():

    rootURL = 'https://www.churchofjesuschrist.org/study/scriptures'
    langURL = 'https://www.churchofjesuschrist.org/languages'

    def __init__(self):
        pass

    def get_langs(self):
        soup = BS(urlopen(self.langURL).read(), 'html.parser')
        langs = [li.find('a') for li in soup.findAll('li')]
        return {a.get('data-lang') : a.text for a in langs}

    def get_books(self, lang):
        soup = BS(urlopen(self.rootURL+f'?lang={lang}'), 'html.parser')
        books = [ a for a in soup.find('section').find('section').findAll('a') ] 
        return { a.get('href').split('/')[-1].split('?')[0] : a.find('span').text for a in books}

    def get_gospels(self, lang, book):
        soup = BS(urlopen(self.rootURL+f'/{book}?lang={lang}'), 'html.parser')
        As = [a for a in soup.find('nav', {'class': 'manifest'}).findAll('a')]
        gospels = {}
        for a in As:
            try:
                int(a.get('href').split('/')[-1].split('?')[0])
                gospels[a.get('href').split('/')[-2]] = a.text
            except ValueError:
                gospels[a.get('href').split('/')[-1].split('?')[0]] = a.text
        return gospels

    def get_gospels(self, lang, book):

        options = webdriver.FirefoxOptions()
        options.binary_location = "/usr/bin/firefox"
        driver = webdriver.Firefox(options=options)
        driver.get(self.rootURL+f'/{book}?lang={lang}')
        svgs = [svg for svg in driver.find_elements_by_tag_name('svg') if svg.get_attribute('style') == 'width: 1em; height: 1em;']#[1:]
        [svg.click() for svg in svgs]

        soup = BS(driver.page_source, 'html.parser')
        nav = soup.find('nav', {'class': 'tableOfContents-3u3H3'})
        books = {}

        for child in nav.find('ul').children:
            try:
                if child.name == 'li':
                    if child.find('ul'):
                        chapters = child.find('ul').findAll('a')
                        books[child.find('a').text.strip()] = (chapters[0].get('href').split('?')[0].split('/')[-2], str(len(chapters)))
                    else:
                        books[child.text.strip()] = (child.find('a').get('href').split('?')[0].split('/')[-1],)
            except:
                pass

        driver.close()

        return {book : books[book] for book in list(books.keys())[1:]}

    def get_chapters(self, lang, book, gospel, chapter):
        soup = BS(urlopen(self.rootURL+f'/{book}/{gospel}/{chapter}?lang={lang}'), 'html.parser')
        summary = soup.find('p', {'id': 'study_summary1'}).text
        intro = soup.find('p', {'id': 'intro1'}).text if soup.find('p', {'id': 'intro1'}) else None
        comprising = soup.find('p', {'id': 'study_intro1'}).text if soup.find('p', {'id': 'study_intro1'}) else None
        verses = [p.text for p in soup.find('div', {'class': 'body-block'}).findAll('p')]
        chapter = {'intro': intro,
                    'comprinsing': comprising,
                    'summary': summary,
                    'veres': verses}
        return chapter

if __name__ == "__main__":
    scraper = scriptureScraper()
    print(scraper.get_chapters('eng', 'bofm', 'alma', '9'))