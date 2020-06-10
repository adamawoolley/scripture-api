from selenium import webdriver
from bs4 import BeautifulSoup as BS
from requests import get
from urllib.request import urlopen

class scriptures():

    rootURL = 'https://www.churchofjesuschrist.org/study/scriptures'
    langURL = 'https://www.churchofjesuschrist.org/languages'
    books = {'1-nephi': {'short': '1-ne', 'chapters': 22, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, '2-nephi': {'short': '2-ne', 'chapters': 33, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'jacob': {'short': 'jacob', 'chapters': 7, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'enos': {'short': 'enos', 'chapters': 1, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'jarom': {'short': 'jarom', 'chapters': 1, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'omni': {'short': 'omni', 'chapters': 1, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'words-of-mormon': {'short': 'w-of-m', 'chapters': 1, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'mosiah': {'short': 'mosiah', 'chapters': 29, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'alma': {'short': 'alma', 'chapters': 63, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'helaman': {'short': 'hel', 'chapters': 16, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, '3-nephi': {'short': '3-ne', 'chapters': 30, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, '4-nephi': {'short': '4-ne', 'chapters': 1, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'mormon': {'short': 'morm', 'chapters': 9, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'ether': {'short': 'ether', 'chapters': 15, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}, 'moroni': {'short': 'moro', 'chapters': 10, 'volume': {'name': 'book-of-mormon', 'short': 'bofm'}}}
    scriptures = {}

    def __init__(self, volumes=['bofm'], errors=False):
        self.langs = self.get_langs()
        #self.books = self.get_books(volumes)
        self.errors = errors

    def get_langs(self):
        soup = BS(urlopen(self.langURL), 'html.parser')
        langs = [li.find('a') for li in soup.find('div', {'id': 'content'}).findAll('li')]
        return { a.get('data-lang') : '-'.join(a.text.lower().split('-')) for a in langs}

    def get_books_from_volume(self, vol='bofm', lang='eng'):

        options = webdriver.FirefoxOptions()
        options.binary_location = '/usr/bin/firefox'
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(self.rootURL+f'/{vol}?lang={lang}')

        # expand all of the tabs
        svgs = [svg for svg in driver.find_elements_by_tag_name('svg') if svg.get_attribute('style') == 'width: 1em; height: 1em;']#[1:]
        [svg.click() for svg in svgs]

        soup = BS(driver.page_source, 'html.parser')
        nav = soup.find('nav', {'class': 'tableOfContents-3u3H3'})

        books = {}
        vol_name = '-'.join(soup.find('h1').getText().lower().split())
        vol_data = {'name': vol_name, 'short': vol}

        for child in nav.find('ul').children:
            if child.name == 'li':
                name = '-'.join(child.find('span').getText().lower().split())
                if child.find('ul'):
                    children = child.find('ul').findAll('a')
                    chapters = len(children)
                    short = children[0].get('href').split('?')[0].split('/')[-2]
                    #gospels[chapters[0].get('href').split('?')[0].split('/')[-2]] = (child.find('a').text.strip(), str(len(chapters)))
                else:
                    chapters = 1
                    short = child.find('a').get('href').split('?')[0].split('/')[-2]
                    #gospels[child.find('a').get('href').split('?')[0].split('/')[-1]] = (child.text.strip(),)
            books[name] = {'short': short, 'chapters': chapters, 'volume': vol_data}

        driver.close()

        info = {
            'bofm': {'start': 2, 'end': -2},
            'ot': {'start': 3, 'end': 0},
            'nt': {'start': 2, 'end': 0},
            'dc-testament': {'start': 4, 'end': 0},
            'pgp': {'start': 3, 'end': 0}
        }

        if info[vol]['end']:
            return {book : books[book] for book in list(books.keys())[info[vol]['start']:info[vol]['end']]}
        return {book : books[book] for book in list(books.keys())[info[vol]['start']:]}

    def get_books(self, volumes=['bofm']):
        books = {}
        for vol in volumes:
            books = dict(books, **self.get_books_from_volume(vol))
        return books

    def fetch_chapter(self, lang='eng', volume='bofm', book='1-ne', chapter=1):

        url = self.rootURL+f'/{volume}/{book}/{str(chapter)}?lang={lang}'
        soup = BS(urlopen(url), 'html.parser')
        
        try:
            intro = soup.find('p', {'id': 'intro1'}).text if soup.find('p', {'id': 'intro1'}) else None
            comprising = soup.find('p', {'id': 'study_intro1'}).text if soup.find('p', {'id': 'study_intro1'}) else None
            summary = soup.find('p', {'id': 'study_summary1'}).text
            verses = []
            raw_verses = soup.find('div', {'class': 'body-block'}).findAll('p')

            for p in raw_verses:
                verse = ''
                for child in p.children:
                    if child.name != 'a' and child.name != 'span':
                        verse += child
                    elif child.name =='a':
                        # exclude the superscript
                        verse += child.text[1:]
                verses.append(verse)

            return {
                'intro': intro,
                'comprising': comprising,
                'summary': summary,
                'verses': verses
            }
        except AttributeError:
            raise NameError('No chapter matches the given parameters')

    def get_chapter(self, lang='eng', book_long='1-nephi', chapter=1):

        try:
            book = self.books[book_long]['short']
            volume = self.books[book_long]['volume']['short']
        except:
            raise NameError('This book does not exist')

        if chapter > self.books[book_long]['chapters']:
            raise NameError('That chapter does not exist')

        if lang in self.langs:
            # If the chapter is already saved
            try:
                return self.scriptures[lang][volume][book][chapter]
            except KeyError:
                try:
                    chapt = self.fetch_chapter(lang, volume, book, chapter)
                    if self.scriptures.get(volume):
                        if self.scriptures.get(volume):
                            if self.scriptures.get(book):
                                self.scriptures[lang][volume][book][chapter] = chapt
                            else:
                                self.scriptures[lang][volume][book] = {chapter: chapt}
                        else:
                            self.scriptures[lang][volume] = {book: {chapter: chapt}}
                    else:
                        self.scriptures[lang] = {volume: {book: {chapter: chapt}}}
                    #self.scriptures[lang][volume][book][chapter] = chapt
                   # self.scriptures[lang][volume][book][chapter] = chapt
                    return chapt
                except:
                    if self.errors:
                        raise NameError('That language is not supported')
                    else:
                        return {'error': 'This is not the chapter you are looking for'}

#    def get_verse(self, lang='eng', volume='bofm', book='1-ne', chapter=1, verse=1):
#        chapter = self.get_chapter(lang, volume, book, chapter)
#        if chapter.get('error'):
#            return chapter
#        try:
#            return {'verse': chapter.get('verses')[verse-1]}
#        except IndexError:
#            return {'error': 'This is not the verse you are looking for'}

if __name__ == "__main__":
    script = scriptures(['bofm', 'dc-testament'])

#class scriptureScraper():
#
#    rootURL = 'https://www.churchofjesuschrist.org/study/scriptures'
#    langURL = 'https://www.churchofjesuschrist.org/languages'
#    data = {}
#
#    def __init__(self):
#        pass
#
#        langs = self.get_langs()
#        langs = {'eng': 'English', 'fra': 'Français'} #, 'spa': 'Español', 'por': 'Português', 'rus': 'Русский', 'ita': 'Italiano', 'deu': 'Deutsch'}
#
#        for lang in langs:
#            print(langs[lang])
#            self.data[lang] = {'name': langs[lang]}
#
#            books = self.get_books(lang)
#            for book in books:
#                print(books[book])
#                self.data[lang][book] = {'name': books[book]}
#
#                gospels = self.get_gospels(lang, book)
#
#                if gospels:
#                    for gospel in gospels:
#
#                        print(gospels[gospel][0])
#
#                        self.data[lang][book][gospel] = {'name': gospels[gospel][0]}
#
#                        chapters = gospels[gospel][1] if len(gospels[gospel]) == 2 else '1'
#                        for chapter in range(1, int(chapters)+1):
#
#                            print(chapter)
#
#                            cha = self.get_chapter(lang, book, gospel, str(chapter))
#                            if cha:
#                                self.data[lang][book][gospel][str(chapter)] = cha #self.get_chapter(lang, book, gospel, str(chapter))
#
#    def get_books(self, lang):
#        return {'bofm': 'Book of Mormon'}
#
#    def get_langs(self):
#        soup = BS(urlopen(self.langURL), 'html.parser')
#        langs = [li.find('a') for li in soup.find('div', {'id': 'content'}).findAll('li')]
#        return {a.get('data-lang') : a.text for a in langs}
#
#    def get_gospels(self, lang, book='bofm'):
#
#        options = webdriver.FirefoxOptions()
#        options.binary_location = '/usr/bin/firefox'
#        options.headless = True
#        driver = webdriver.Firefox(options=options)
#        driver.get(self.rootURL+f'/{book}?lang={lang}')
#
#        try:
#            svgs = [svg for svg in driver.find_elements_by_tag_name('svg') if svg.get_attribute('style') == 'width: 1em; height: 1em;']#[1:]
#            [svg.click() for svg in svgs]
#
#            soup = BS(driver.page_source, 'html.parser')
#            nav = soup.find('nav', {'class': 'tableOfContents-3u3H3'})
#            gospels = {}
#
#            for child in nav.find('ul').children:
#                try:
#                    if child.name == 'li':
#                        if child.find('ul'):
#                            chapters = child.find('ul').findAll('a')
#                            gospels[chapters[0].get('href').split('?')[0].split('/')[-2]] = (child.find('a').text.strip(), str(len(chapters)))
#                        else:
#                            gospels[child.find('a').get('href').split('?')[0].split('/')[-1]] = (child.text.strip(),)
#                except:
#                    pass
#
#            driver.close()
#            return {gospel : gospels[gospel] for gospel in list(gospels.keys())[1:]}
#
#        except:
#            driver.close()
#            return False
#
#    def get_chapter(self, lang, book, gospel, chapter):
#
#        soup = BS(urlopen(self.rootURL+f'/{book}/{gospel}/{chapter}?lang={lang}'), 'html.parser')
#
#        try:
#            intro = soup.find('p', {'id': 'intro1'}).text if soup.find('p', {'id': 'intro1'}) else None
#            comprising = soup.find('p', {'id': 'study_intro1'}).text if soup.find('p', {'id': 'study_intro1'}) else None
#            summary = soup.find('p', {'id': 'study_summary1'}).text
#            verses = []
#
#            raw_verses = soup.find('div', {'class': 'body-block'}).findAll('p')
#
#            for p in raw_verses:
#                verse = ''
#                references = [] # {'sup', 'word', 'scriptures': []}
#                for child in p.children:
#                    if child.name != 'a':
#                        try:
#                            verse += child.text
#                        except AttributeError:
#                            verse += str(child)
#                    else:
#                        references.append(
#                            {
#                                'sup': child.find('sup').text,
#                                'word': len(verse.split()),
#                                'len': len(child.text.split())
#                            })
#                        # exclude the superscript
#                        verse += child.text[1:]
#                verses.append({'verse': verse, 'references': references})
#
#            # get the references
#            raw_refs = []
#            for child in soup.find('section', {'class': 'panelGridLayout-3J74n'}).children:
#                for child in child.children:
#                    if child.name == 'aside':
#                        break
#                    raw_refs.append(child)
#                    #[child for child in soup.find('section', {'class': 'panelGridLayout-3J74n'}).children if list(child.children)[0].name != 'aside']
#            references = [ (raw_refs[i].text, raw_refs[i+1].text) for i in range(0, len(raw_refs), 2)]
#
#            for ref in references:
#                print(ref)
#                sup = ref[0][-1]
#                verse = ref[0][:-1]
#                for i, reference in enumerate(verses[int(verse)-1]['references']):
#                    if reference['sup'] == sup:
#                        verses[int(verse)-1]['references'][i]['scriptures'] = [ r  if r[-1] != '.' else r[:-1]  for r in ref[1].split(';') ]
#
#            return {
#                'intro': intro,
#                'comprising': comprising,
#                'summary': summary,
#                'verses': verses
#            }
#        except AttributeError:
#            return False

#class scriptureScraper():
#
#    rootURL = 'https://www.churchofjesuschrist.org/study/scriptures'
#    langURL = 'https://www.churchofjesuschrist.org/languages'
#    data = {}
#
#    def __init__(self):
#
#        langs = self.get_langs()
#        langs = {'eng': 'English', 'fra': 'Français'} #, 'spa': 'Español', 'por': 'Português', 'rus': 'Русский', 'ita': 'Italiano', 'deu': 'Deutsch'}
#
#        for lang in langs:
#            print(langs[lang])
#            self.data[lang] = {'name': langs[lang]}
#
#            books = self.get_books(lang)
#            for book in books:
#                print(books[book])
#                self.data[lang][book] = {'name': books[book]}
#
#                gospels = self.get_gospels(lang, book)
#
#                if gospels:
#                    for gospel in gospels:
#
#                        print(gospels[gospel][0])
#
#                        self.data[lang][book][gospel] = {'name': gospels[gospel][0]}
#
#                        chapters = gospels[gospel][1] if len(gospels[gospel]) == 2 else '1'
#                        for chapter in range(1, int(chapters)+1):
#
#                            print(chapter)
#
#                            cha = self.get_chapter(lang, book, gospel, str(chapter))
#                            if cha:
#                                self.data[lang][book][gospel][str(chapter)] = cha #self.get_chapter(lang, book, gospel, str(chapter))
#
#    def get_langs(self):
#        soup = BS(urlopen(self.langURL), 'html.parser')
#        langs = [li.find('a') for li in soup.find('div', {'id': 'content'}).findAll('li')]
#        return {a.get('data-lang') : a.text for a in langs}
#
#    def get_books(self, lang):
#        soup = BS(urlopen(self.rootURL+f'?lang={lang}'), 'html.parser')
#        books = [ a for a in soup.find('section').find('section').findAll('a') ]
#        return { a.get('href').split('/')[-1].split('?')[0] : a.find('span').text for a in books}
#
#    #def get_gospels(self, lang, book):
#    #    soup = BS(urlopen(self.rootURL+f'/{book}?lang={lang}'), 'html.parser')
#    #    As = [a for a in soup.find('nav', {'class': 'manifest'}).findAll('a')]
#    #    gospels = {}
#    #    for a in As:
#    #        try:
#    #            int(a.get('href').split('/')[-1].split('?')[0])
#    #            gospels[a.get('href').split('/')[-2]] = a.text
#    #        except ValueError:
#    #            gospels[a.get('href').split('/')[-1].split('?')[0]] = a.text
#    #    return gospels
#
#    def get_gospels(self, lang, book):
#
#        options = webdriver.FirefoxOptions()
#        options.binary_location = '/usr/bin/firefox'
#        options.headless = True
#        driver = webdriver.Firefox(options=options)
#        driver.get(self.rootURL+f'/{book}?lang={lang}')
#
#        try:
#            svgs = [svg for svg in driver.find_elements_by_tag_name('svg') if svg.get_attribute('style') == 'width: 1em; height: 1em;']#[1:]
#            [svg.click() for svg in svgs]
#
#            soup = BS(driver.page_source, 'html.parser')
#            nav = soup.find('nav', {'class': 'tableOfContents-3u3H3'})
#            gospels = {}
#
#            for child in nav.find('ul').children:
#                try:
#                    if child.name == 'li':
#                        if child.find('ul'):
#                            chapters = child.find('ul').findAll('a')
#                            gospels[chapters[0].get('href').split('?')[0].split('/')[-2]] = (child.find('a').text.strip(), str(len(chapters)))
#                        else:
#                            gospels[child.find('a').get('href').split('?')[0].split('/')[-1]] = (child.text.strip(),)
#                except:
#                    pass
#
#            driver.close()
#            return {gospel : gospels[gospel] for gospel in list(gospels.keys())[1:]}
#
#        except:
#            driver.close()
#            return False
#
#
#
#    def get_chapter(self, lang, book, gospel, chapter):
#
#        soup = BS(urlopen(self.rootURL+f'/{book}/{gospel}/{chapter}?lang={lang}'), 'html.parser')
#
#        try:
#            intro = soup.find('p', {'id': 'intro1'}).text if soup.find('p', {'id': 'intro1'}) else None
#            comprising = soup.find('p', {'id': 'study_intro1'}).text if soup.find('p', {'id': 'study_intro1'}) else None
#            summary = soup.find('p', {'id': 'study_summary1'}).text
#            verses = []
#
#            raw_verses = soup.find('div', {'class': 'body-block'}).findAll('p')
#
#            for p in raw_verses:
#                verse = ''
#                references = [] # {'sup', 'word', 'scriptures': []}
#                for child in p.children:
#                    if child.name != 'a':
#                        try:
#                            verse += child.text
#                        except AttributeError:
#                            verse += str(child)
#                    else:
#                        references.append(
#                            {
#                                'sup': child.find('sup').text,
#                                'word': len(verse.split()),
#                                'len': len(child.text.split())
#                            })
#                        # exclude the superscript
#                        verse += child.text[1:]
#                verses.append({'verse': verse, 'references': references})
#
#            # get the references
#            raw_refs = []
#            for child in soup.find('section', {'class': 'panelGridLayout-3J74n'}).children:
#                for child in child.children:
#                    if child.name == 'aside':
#                        break
#                    raw_refs.append(child)
#                    #[child for child in soup.find('section', {'class': 'panelGridLayout-3J74n'}).children if list(child.children)[0].name != 'aside']
#            references = [ (raw_refs[i].text, raw_refs[i+1].text) for i in range(0, len(raw_refs), 2)]
#
#            for ref in references:
#                print(ref)
#                sup = ref[0][-1]
#                verse = ref[0][:-1]
#                for i, reference in enumerate(verses[int(verse)-1]['references']):
#                    if reference['sup'] == sup:
#                        verses[int(verse)-1]['references'][i]['scriptures'] = [ r  if r[-1] != '.' else r[:-1]  for r in ref[1].split(';') ]
#
#            return {
#                'intro': intro,
#                'comprising': comprising,
#                'summary': summary,
#                'verses': verses
#            }
#        except AttributeError:
#            return False
#if __name__ == "__main__":
#
#    scraper = scriptureScraper()
#    #a = scraper.get_gospels('fra', 'ot')
