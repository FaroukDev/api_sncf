
class Completer:
    def __init__(self, words):
        self._words = words

    def complete(self, text, state):
        matches = [w for w in self._words if w.startswith(text)]
        return matches[state]