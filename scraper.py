from selenium import webdriver
from bs4 import BeautifulSoup as BS
from requests import get
from urllib.request import urlopen

class scriptureScraper():

    rootURL = 'https://www.churchofjesuschrist.org/study/scriptures'
    langURL = 'https://www.churchofjesuschrist.org/languages'
    data = {}

    def __init__(self):

        langs = self.get_langs()

        for lang in langs:
            self.data[lang] = {'name': langs[lang]}

            books = self.get_books(lang)
            for book in books:
                self.data[lang][book] = {'name': books[book]}

                gospels = self.get_gospels(lang, book)
                for gospel in gospels:
                    self.data[lang][book][gospel] = {'name': gospels[gospel]}

                    chapters = gospels[gospel][1] if len(gospels[gospel] == 2) else '1'
                    for chapter in range(int(chapters)):
                        self.data[lang][book][gospel][str(chapter)] = self.get_chapter(lang, book, gospel, str(chapter))

    def get_langs(self):
        soup = BS(urlopen(self.langURL), 'html.parser')
        langs = [li.find('a') for li in soup.findAll('li')]
        return {a.get('data-lang') : a.text for a in langs}

    def get_books(self, lang):
        soup = BS(urlopen(self.rootURL+f'?lang={lang}'), 'html.parser')
        books = [ a for a in soup.find('section').find('section').findAll('a') ] 
        return { a.get('href').split('/')[-1].split('?')[0] : a.find('span').text for a in books}

    #def get_gospels(self, lang, book):
    #    soup = BS(urlopen(self.rootURL+f'/{book}?lang={lang}'), 'html.parser')
    #    As = [a for a in soup.find('nav', {'class': 'manifest'}).findAll('a')]
    #    gospels = {}
    #    for a in As:
    #        try:
    #            int(a.get('href').split('/')[-1].split('?')[0])
    #            gospels[a.get('href').split('/')[-2]] = a.text
    #        except ValueError:
    #            gospels[a.get('href').split('/')[-1].split('?')[0]] = a.text
    #    return gospels

    def get_gospels(self, lang, book):

        try:
            options = webdriver.FirefoxOptions()
            options.binary_location = '/usr/bin/firefox'
            options.headless = True
            driver = webdriver.Firefox(options=options)
            driver.get(self.rootURL+f'/{book}?lang={lang}')
            svgs = [svg for svg in driver.find_elements_by_tag_name('svg') if svg.get_attribute('style') == 'width: 1em; height: 1em;']#[1:]
            [svg.click() for svg in svgs]

            soup = BS(driver.page_source, 'html.parser')
            nav = soup.find('nav', {'class': 'tableOfContents-3u3H3'})
            gospels = {}

            for child in nav.find('ul').children:
                try:
                    if child.name == 'li':
                        if child.find('ul'):
                            chapters = child.find('ul').findAll('a')
                            gospels[chapters[0].get('href').split('?')[0].split('/')[-2]] = (child.find('a').text.strip(), str(len(chapters)))
                        else:
                            gospels[child.find('a').get('href').split('?')[0].split('/')[-1]] = (child.text.strip(),)
                except:
                    pass

            driver.close()
            return {gospel : gospels[gospel] for gospel in list(gospels.keys())[1:]}

        except AttributeError:
            driver.close()
            return False

        

    def get_chapter(self, lang, book, gospel, chapter):

        soup = BS(urlopen(self.rootURL+f'/{book}/{gospel}/{chapter}?lang={lang}'), 'html.parser')

        intro = soup.find('p', {'id': 'intro1'}).text if soup.find('p', {'id': 'intro1'}) else None
        comprising = soup.find('p', {'id': 'study_intro1'}).text if soup.find('p', {'id': 'study_intro1'}) else None
        summary = soup.find('p', {'id': 'study_summary1'}).text
        verses = []

        raw_verses = soup.find('div', {'class': 'body-block'}).findAll('p')
        
        for p in raw_verses:
            verse = ''
            references = [] # {'sup', 'word', 'scriptures': []}
            for child in p.children:
                if child.name != 'a':
                    try:
                        verse += child.text
                    except AttributeError:
                        verse += str(child)
                else:
                    references.append(
                        {
                            'sup': child.find('sup').text,
                            'word': len(verse.split()),
                            'len': len(child.text.split())
                        })
                    # exclude the superscript
                    verse += child.text[1:]
            verses.append({'verse': verse, 'references': references})

        # get the references
        raw_refs = list(soup.find('section', {'class': 'panelGridLayout-3J74n'}).children)
        references = [ (raw_refs[i].text, raw_refs[i+1].text) for i in range(0, len(raw_refs), 2)]
        
        for ref in references:
            sup = ref[0][-1]
            verse = ref[0][:-1]
            for i, reference in enumerate(verses[int(verse)-1]['references']):
                if reference['sup'] == sup:
                    verses[int(verse)-1]['references'][i]['scriptures'] = [ r  if r[-1] != '.' else r[:-1]  for r in ref[1].split(';') ]

        return {
            'intro': intro,
            'comprising': comprising,
            'summary': summary,
            'verses': verses
        }

if __name__ == "__main__":

    scraper = scriptureScraper()
    a = scraper.get_gospels('fra', 'ot')