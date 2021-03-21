import json
from collections.abc import Callable
import urllib.request
from . import anki_types


def _request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def _invoke(action, **params) -> list:
    request_json = json.dumps(_request(action, **params)).encode('utf-8')
    response = json.load(
        urllib.request.urlopen(
            urllib.request.Request('http://localhost:8765', request_json)
        )
    )
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def note_info(
        ids: list[str],
        filter_func: Callable[[anki_types.Note], bool]
) -> list[anki_types.Note]:
    _temp_res = _invoke('notesInfo', notes=ids)
    # _temp_res = [_temp_res[0]]
    result = list[anki_types.Note]()
    for raw_note in _temp_res:
        parsed = anki_types.Note()
        parsed.parse_note(raw_note)
        if filter_func is not None and not filter_func(parsed):
            continue
        result.append(parsed)

    return result


def search(query: str, deck=""):
    return _invoke(
        'findNotes',
        query=f'{f"deck:{deck} " if deck is not None else ""}{query}'
    )


def update_note_field(deck: str, **param):
    return _invoke(
        'updateNoteFields',
        **param
    )
