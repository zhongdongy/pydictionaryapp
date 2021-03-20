from lib.connect import search, noteInfo
from lib.dictionaryapi import DictionaryAPI
import pprint

with open('dictionaryapi.key', 'r') as keyfile:
    key = keyfile.read()
    dict = DictionaryAPI(key)
    # ids = search('hello','英语::考纲')
    # if ids:
    #     id = ids[0]
    query_result = dict.query('share')

    print(query_result)
