from lib.connect import search, note_info, update_note_field
from lib.dictionaryapi import DictionaryAPI, WordRef
from lib.anki_types import Note, Field
import re


def empty_audio_filter(note: Note) -> bool:
    field: Field
    for field in note.parsedFields:
        if field.name == 'Pronunciation':
            if field.value == '':
                return True
            elif re.search(r'\[.+\.ogg\]', field.value):
                # All entries with .ogg format will be included
                return True
            elif re.search(r'\[sound:.+\]', field.value) is None:
                # All entries with pronunciation but no audio will be included.
                return True
    return False


with open('dictionaryapi.key', 'r') as keyfile:
    key = keyfile.read()
    dictObj = DictionaryAPI(key)
    deck = "英语::考纲"
    ids = search('', deck)
    if len(ids) > 0:
        filter_words = note_info(ids, empty_audio_filter)
        total = len(filter_words)
        counter = 1
        unmatch_words = list[Note]()
        for word in filter_words:
            if not word.modelName == 'Language (words)':
                unmatch_words.append(word)
                continue
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

            query_result: [WordRef, None] = None
            try:
                query_result = dictObj.query(word_name)
                if query_result and not (query_result.pronunciation == '') and not (query_result.audio_file == ''):
                    update_note_field(deck, **{
                        'note': {
                            'id': word.noteId,
                            'fields': {
                                'Pronunciation': query_result.pronunciation,
                                'OriginalLang': word_name
                            },
                            'audio': [{
                                "url": query_result.audio_file,
                                "filename": f'audio_{word_name}.mp3',
                                "fields": [
                                    "Pronunciation"
                                ]
                            }]
                        }
                    })
                else:
                    print(f'  Unable to update {word_name} because no pronunciation found, skip')
            except:
                print(f'  Unable to update {word_name} because no entry found, skip')

        if len(unmatch_words) > 0:
            [print(i) for i in unmatch_words]
            print(f'{len(unmatch_words)} words with wrong card type.')
