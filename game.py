from message import ServerMessage


class GameData:
    def __init__(self, word_length: int, num_incorrect: int, word: str, incorrect: list):
        self.word_length = word_length
        self.num_incorrect = num_incorrect
        self.word = word
        self.incorrect = incorrect

    @classmethod
    def from_message(cls, message: ServerMessage):
        word = message.data[:message.word_length]
        if message.num_incorrect == 0:
            incorrect = []
        else:
            incorrect = list(message.data[message.word_length:message.word_length + message.num_incorrect])

        return cls(message.word_length, message.num_incorrect, word, incorrect)

    def __str__(self):
        incorrect_string = ''.join(self.incorrect)
        return f'{self.word}{incorrect_string}'

    def copy(self):
        return GameData(self.word_length, self.num_incorrect, self.word, self.incorrect[:])

    def to_message(self):
        return ServerMessage(0, str(self), self.word_length, self.num_incorrect)
