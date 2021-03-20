import json
import urllib.request
import re


class WordRef:
    def __init__(self):
        self.word = ''
        self.function_label = ''
        self.audio_file = ''
        self.uuid = ''

    def __str__(self):
        return f'Word: {self.word}\n' \
               f'Function Label: {self.function_label}\n' \
               f'Audio File: {self.audio_file}\n' \
               f'UUID: {self.uuid}\n'


class DictionaryAPI:

    def __init__(self, key: str):
        self._COLLEGIATE_URL = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/$WORD?key={key}'
        self._AUDIO_URL = f'https://media.merriam-webster.com/audio/prons/' \
                          f'en/us/ogg/$subdirectory/$audio.ogg'

    def query(self, word: str):
        url = self._COLLEGIATE_URL.replace('$WORD', word)
        response = json.load(urllib.request.urlopen(urllib.request.Request(url, method='GET')))
        if response is None or len(response) == 0:
            return None

        if len(response) > 1:
            result = WordRef()
            _temp_func_labels = set()
            for r in response:
                if re.match(r'^' + word + r':\d+', r['meta']['id']):
                    parsed = self._parse(r, word)
                    if result.audio_file == '':
                        result.audio_file = parsed.audio_file
                    if result.uuid == '':
                        result.uuid = parsed.uuid
                    result.word = word
                    _temp_func_labels.add(parsed.function_label)
            result.function_label = ' / '.join(_temp_func_labels)
            return result
        else:
            return self._parse(response[0], word)

    def _parse(self, res: dict, word: str):
        if not res:
            return None

        parsed_word = WordRef()
        parsed_word.word = re.search(r'^(' + word + r'):\d+', res['meta']['id']).group(1)
        parsed_word.uuid = res['meta']['uuid']
        parsed_word.function_label = res['fl']
        if 'prs' in res['hwi']:
            _audio: str = res['hwi']['prs'][0]['sound']['audio']
            _subdirectory = ''
            if _audio.startswith('bix'):
                _subdirectory = 'bix'
            elif _audio.startswith('gg'):
                _subdirectory = 'gg'
            elif re.match(r'^[\d,_:\-?!\'].+', _audio):
                _subdirectory = 'number'
            else:
                _subdirectory = _audio[0]
            parsed_word.audio_file = self._AUDIO_URL.replace('$subdirectory', _subdirectory).replace('$audio', _audio)

        return parsed_word
