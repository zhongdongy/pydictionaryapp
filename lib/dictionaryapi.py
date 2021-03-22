import json
import urllib.request
import re
import logging

logging.basicConfig(filename='dictionary.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


class WordRef:
    def __init__(self):
        self.word = ''
        self.function_label = ''
        self.audio_file = ''
        self.uuid = ''
        self.pronunciation = ''

    def __str__(self):
        return f'''Word: {self.word}
Pronunciation: {self.pronunciation}
Function Label: {self.function_label}
Audio File: {self.audio_file}
UUID: {self.uuid}
'''


class DictionaryAPI:

    def __init__(self, key: str):
        self._COLLEGIATE_URL = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/$WORD?key={key}'
        self._AUDIO_URL = f'https://media.merriam-webster.com/audio/prons/' \
                          f'en/us/mp3/$subdirectory/$audio.mp3'

    def query(self, word: str):
        url = self._COLLEGIATE_URL.replace('$WORD', word)
        response = json.load(urllib.request.urlopen(urllib.request.Request(url, method='GET')))
        logging.info(json.dumps(response))
        if response is None or len(response) == 0:
            return None

        if len(response) > 1:
            result = WordRef()
            _temp_func_labels = set()
            for r in response:
                if re.match(r'^' + word + r'(?::.+)?', r['meta']['id'], flags=re.IGNORECASE) or \
                        ('stems' in r['meta'] and word in r['meta']['stems']):
                    parsed = self._parse(r, word)
                    if result.audio_file == '':
                        result.audio_file = parsed.audio_file
                    if result.uuid == '':
                        result.uuid = parsed.uuid
                    result.word = word
                    _temp_func_labels.add(parsed.function_label)
                    if result.pronunciation == '':
                        result.pronunciation = parsed.pronunciation
            result.function_label = ' / '.join(_temp_func_labels)
            return result
        else:
            return self._parse(response[0], word)

    def _parse(self, res: dict, word: str):
        if not res:
            return None

        parsed_word = WordRef()
        parsed_word.word = word
        parsed_word.uuid = res['meta']['uuid']
        parsed_word.function_label = res['fl'] if 'fl' in res else ''

        if 'prs' in res['hwi']:
            for prsObj in res['hwi']['prs']:
                if 'mw' in prsObj:
                    if parsed_word.pronunciation == '':
                        parsed_word.pronunciation = f"/{prsObj['mw']}/".replace('-', '')
                if 'sound' in prsObj:
                    _audio: str = prsObj['sound']['audio']
                    _subdirectory = ''
                    if _audio.startswith('bix'):
                        _subdirectory = 'bix'
                    elif _audio.startswith('gg'):
                        _subdirectory = 'gg'
                    elif re.match(r'^[\d,_:\-?!\'].+', _audio):
                        _subdirectory = 'number'
                    else:
                        _subdirectory = _audio[0]
                    if parsed_word.audio_file == '':
                        parsed_word.audio_file = self._AUDIO_URL.replace('$subdirectory', _subdirectory) \
                            .replace('$audio', _audio)
        else:
            if 'cxs' in res:
                for cxs in res['cxs']:
                    if 'cxl' in cxs and cxs['cxl'] == 'British spelling of':
                        return self.query(cxs['cxtis'][0]['cxt'])
        return parsed_word
