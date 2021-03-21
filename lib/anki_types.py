class Field:
    def __init__(self, name: str, value: str, order=0):
        self.name = name
        self.value = value
        self.order = order

    def __str__(self):
        return f"""Filed Name: {self.name}
Field Value: {self.value}
Field Order: {self.order}
"""

    def to_str(self, char=''):
        return f"""{char}Filed Name: {self.name}
{char}Field Value: {self.value}
{char}Field Order: {self.order}
"""


class Note:
    def __init__(self):
        """Initialize an empty Note object"""
        self.noteId = -1
        self.tags = list[str]()
        self.fields = dict[str, dict]()
        self.parsedFields = list[Field]()
        self.modelName = ""
        self.cards = list[int]()

    def get_field(self, name: str) -> Field:
        for f in self.parsedFields:
            if f.name == name:
                return f
        return None

    def parse_note(self, obj: dict):
        if obj is None:
            raise ValueError("Anki note expected")

        self.noteId = obj['noteId']
        self.tags = obj['tags']
        self.fields = obj['fields']
        for k in self.fields:
            f = Field(k, self.fields[k]['value'], self.fields[k]['order'])
            self.parsedFields.append(f)

        self.modelName = obj['modelName']
        self.cards = obj['cards']

    def __str__(self):
        _str = f"""Note ID: {self.noteId}
Note Tags: {self.tags}
Note Fields: 
"""
        for f in self.parsedFields:
            _str += f.to_str('  ')
        _str += f"""Note Type: {self.modelName}
Note Card IDs: {self.cards}
"""
        return _str
