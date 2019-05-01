import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

class SearchDict:
    def __init__(self, search_url, get_url):
        self.search_url = search_url
        self.get_url = get_url
    
    def search(self, params):
        p = urllib.parse.urlencode(params)
        req_url = self.search_url + '?' + p
        req = urllib.request.Request(req_url)

        with urllib.request.urlopen(req) as response:
            xml_string = response.read()
            root = ET.fromstring(xml_string)
            hits = int(root[1].text)
            l = []

            if hits > 0:
                ItemID = root[3][0][0].text
                word = root[3][0][2][0].text
                l.append({'ItemID' : ItemID, 'word' : word})

            return [hits, l]
    
    def get(self, params):
        p = urllib.parse.urlencode(params)
        req_url = self.get_url + '?' + p
        req = urllib.request.Request(req_url)

        with urllib.request.urlopen(req) as response:
            xml_string = response.read()
            root = ET.fromstring(xml_string)
            meaning = root[2][0][0].text
            return meaning
    
    def search_and_get(self, word):

        params = {
            'Dic': 'EJdict',
            'Word': word,
            'Scope': 'HEADWORD',
            'Match': 'EXACT',
            'Merge': 'AND',
            'Prof': 'XHTML',
            'PageSize': 20,
            'PageIndex': 0
        }

        result = self.search(params)[1]

        params2 = {
            'Dic': 'EJdict',
            'Item': result[0]['ItemID'],
            'Loc': '',
            'Prof': 'XHTML'
        }

        meaning = self.get(params2)

        return meaning
