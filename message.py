class ClientMessage:
    def __init__(self, msg_length, data):
        self.msg_length = msg_length
        self.data = data

    @classmethod
    def from_raw_bytes(cls, raw_message: bytes):
        raw_message = raw_message.decode('utf-8')
        msg_length = int(raw_message[0])
        data = raw_message[1:msg_length + 1]
        return cls(msg_length, data)

    def to_raw_bytes(self) -> bytes:
        strng = f'{self.msg_length}{self.data}'
        return strng.encode('utf-8')


class ServerMessage:
    def __init__(self, msg_flag: int, data: str, word_length: int = None, num_incorrect: int = None):
        self.msg_flag = msg_flag
        self.data = data
        self.word_length = word_length
        self.num_incorrect = num_incorrect

    @classmethod
    def from_raw_bytes(cls, raw_message: bytes):
        msg_flag = raw_message[0]
        if msg_flag == 0:
            word_length = raw_message[1]
            num_incorrect = raw_message[2]
            data = raw_message[3:].decode('utf-8')
        else:
            word_length = None
            num_incorrect = None
            data = raw_message[1:msg_flag + 1].decode('utf-8')

        return cls(msg_flag, data, word_length, num_incorrect)

    def to_raw_bytes(self) -> bytes:
        bytes_list = [self.msg_flag.to_bytes(1, 'big')]
        if self.msg_flag == 0:
            bytes_list.append(self.word_length.to_bytes(1, 'big'))
            bytes_list.append(self.num_incorrect.to_bytes(1, 'big'))

        bytes_list.append(self.data.encode('utf-8'))

        return b''.join(bytes_list)
