from lib.connect import search, note_info, update_note_field
from lib.dictionaryapi import DictionaryAPI
from lib.anki_types import Note
import re


def empty_audio_filter(note: Note) -> bool:
    for field in note.parsedFields:
        if field.name == 'Pronunciation' and field.value == '':
            return True
    return False


with open('dictionaryapi.key', 'r') as keyfile:
    key = keyfile.read()
    dictObj = DictionaryAPI(key)
    deck = "英语::日常单词"
    ids = search('', deck)
    if len(ids) > 0:
        filter_words = note_info(ids, empty_audio_filter)
        total = len(filter_words)
        counter = 1
        for word in filter_words:
            word_name = ''
            try:
                word_name = word.get_field('OriginalLang').value.strip()
                word_name = word_name.replace('&nbsp;', '')
                if word_name.index('<') >= 0:
                    """This OriginalLang contains HTML label, should remove"""
                    word_name = re.search(r'(?:<[a-z_-]+>)([a-z\d_\s-]+)(?:</[a-z_-]+>)', word_name).group(1)
            except ValueError:
                pass
            except AttributeError:
                if word_name == '':
                    word_name = word
                print(f'Unable to extract word name for: {word_name}')
                quit(1)

            print(f"[{counter}/{total}]: updating {word_name}")
            counter += 1

            query_result = dictObj.query(word_name)
            if not (query_result.pronunciation == '') and not (query_result.audio_file == ''):
                update_note_field(deck, **{
                    'note': {
                        'id': word.noteId,
                        'fields': {
                            'Pronunciation': query_result.pronunciation,
                            'OriginalLang': word_name
                        },
                        'audio': [{
                            "url": query_result.audio_file,
                            "filename": f'audio_{word_name}.ogg',
                            "fields": [
                                "Pronunciation"
                            ]
                        }]
                    }
                })
            else:
                print(f'  Unable to update {word_name} because no pronunciation found, skip')
