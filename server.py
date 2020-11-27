import argparse
import socket
import threading
import random
import time

from message import ClientMessage, ServerMessage
from game import GameData


# picked from random word generator
dictionary = ['cause', 'shoot', 'swing', 'rider', 'bring', 'shock', 'minor', 'deter', 'heart', 'tense']
word_len = 5

sock: socket.socket

connections = {}

mp_game_data = None
mp_word = None
multiplayer_queue = {}
priority = {}
turn = 1
mp_game_over = False
mp_message = None


class GameThread(threading.Thread):
    def __init__(self, csock: socket.socket):
        super().__init__()
        self.sock = csock
        self.word = None
        self._signal_stop = False

    def run(self):
        try:
            self.start_game()
        except OSError:
            pass

    def check_guess(self, game_data: GameData, response: ClientMessage):
        new_game_data = game_data.copy()
        guess = response.data
        match = False

        for idx, c in enumerate(self.word):
            if c == guess:
                match = True
                new_game_data.word = new_game_data.word[:idx] + guess + new_game_data.word[idx + 1:]

                if new_game_data.word == self.word:
                    data = 'You Win!'
                    message = ServerMessage(len(data), data)
                    self.stop()
                    self.sock.sendall(message.to_raw_bytes())
                    return new_game_data

        if not match:
            new_game_data.num_incorrect += 1
            new_game_data.incorrect.append(guess)

            if new_game_data.num_incorrect == 6:
                data = f'You Lose: {self.word}'
                message = ServerMessage(len(data), data)
                self.stop()
                self.sock.sendall(message.to_raw_bytes())
                return new_game_data

        self.sock.sendall(new_game_data.to_message().to_raw_bytes())

        return new_game_data

    def start_1p_game(self):
        conn = connections[self]
        print(f'Client {conn.addr[0]}:{conn.addr[1]} playing in single-player mode')

        data = 'Ready to start game? (y/n): '
        message = ServerMessage(len(data), data)
        self.sock.sendall(message.to_raw_bytes())

        data = self.sock.recv(1024)
        if data == b'':
            return self.cleanup()

        response = ClientMessage.from_raw_bytes(data)
        if response.data == 'n' or response.data == 'Terminate':
            return self.cleanup()

        if response.data == 'y':
            [self.word] = random.sample(dictionary, 1)
        else:
            self.word = dictionary[int(response.data) - 1]

        game_word = '_' * len(self.word)
        game_data = GameData(word_len, 0, game_word, [])
        self.sock.sendall(game_data.to_message().to_raw_bytes())

        while not self._signal_stop:
            data = self.sock.recv(1024)
            if data == b'':
                return

            response = ClientMessage.from_raw_bytes(data)
            if response.data == 'Terminate':
                return self.cleanup()

            game_data = self.check_guess(game_data, response)

    def check_guess_2p(self, game_data: GameData, response: ClientMessage):
        global mp_game_over, mp_message

        new_game_data = game_data.copy()
        guess = response.data
        match = False

        for idx, c in enumerate(self.word):
            if c == guess:
                match = True
                new_game_data.word = new_game_data.word[:idx] + guess + new_game_data.word[idx + 1:]

                if new_game_data.word == self.word:
                    data = f'You Win!'
                    message = ServerMessage(len(data), data)
                    data = f'You Win! The word was {self.word}'
                    mp_message = ServerMessage(len(data), data)
                    mp_game_over = True
                    time.sleep(0.5)  # let flag change before being read by other thread
                    self.stop()
                    self.sock.sendall(message.to_raw_bytes())
                    return new_game_data

        if not match:
            new_game_data.num_incorrect += 1
            new_game_data.incorrect.append(guess)

            if new_game_data.num_incorrect == 6:
                data = f'You Lose: {self.word}'
                mp_message = ServerMessage(len(data), data)
                mp_game_over = True
                time.sleep(0.5)  # let flag change before being read by other thread
                self.stop()
                self.sock.sendall(mp_message.to_raw_bytes())
                return new_game_data

        return new_game_data

    def play_2p_game(self):
        global mp_game_data, turn

        count = 0
        while not self._signal_stop:
            if mp_game_over:
                self.sock.sendall(mp_message.to_raw_bytes())
                return

            if not self.word:
                self.word = mp_word

            if len(multiplayer_queue) == 0:
                continue

            is_player_turn = priority[self] == turn

            if is_player_turn and self.word:
                count = 0
                data = 'Your Turn!'
                message = ServerMessage(len(data), data)
                self.sock.sendall(message.to_raw_bytes())
                time.sleep(0.5)  # prevent weird error where second message wouldn't send
                self.sock.sendall(mp_game_data.to_message().to_raw_bytes())

                data = self.sock.recv(1024)
                if data == b'':
                    return

                response = ClientMessage.from_raw_bytes(data)
                if response.data == 'Terminate':
                    return self.cleanup()

                mp_game_data = self.check_guess_2p(mp_game_data, response)
                if turn == 1:
                    turn = 2
                else:
                    turn = 1
            else:
                if count < 1:
                    data = f'Waiting on Player {turn}...'
                    message = ServerMessage(len(data), data)
                    self.sock.sendall(message.to_raw_bytes())
                    count += 1

    def start_2p_game(self):
        global mp_game_data, mp_word

        if len(connections) == 3:
            conn = connections[self]
            print(f'Client {conn.addr[0]}:{conn.addr[1]} multiplayer mode request rejected due to limited connections')

            data = 'There are not enough connections available to set up a multiplayer game. Please try again later or play a single-player game'
            message = ServerMessage(len(data), data)
            self.sock.sendall(message.to_raw_bytes())
            return self.cleanup()
        if len(multiplayer_queue) == 0:
            conn = connections[self]
            multiplayer_queue[self] = conn
            priority[self] = 1
            print(f'Client {conn.addr[0]}:{conn.addr[1]} playing in multiplayer mode')

            data = 'Waiting for other player!'
            message = ServerMessage(len(data), data)
            self.sock.sendall(message.to_raw_bytes())
        elif len(multiplayer_queue) == 1:
            data = 'Game Starting!'
            message = ServerMessage(len(data), data)
            self.sock.sendall(message.to_raw_bytes())

            key = next(iter(multiplayer_queue))
            multiplayer_queue[key].sock.sendall(message.to_raw_bytes())

            conn = connections[self]
            multiplayer_queue[self] = conn
            priority[self] = 2
            print(f'Client {conn.addr[0]}:{conn.addr[1]} playing in multiplayer mode')

            [self.word] = random.sample(dictionary, 1)
            game_word = '_' * len(self.word)
            mp_game_data = GameData(word_len, 0, game_word, [])
            mp_word = self.word
            self.play_2p_game()
        else:
            conn = connections[self]
            print(f'Client {conn.addr[0]}:{conn.addr[1]} multiplayer mode request rejected due to existing game')

            data = 'A multiplayer game is already being played on this server. Please try again later or play a single-player game'
            message = ServerMessage(len(data), data)
            self.sock.sendall(message.to_raw_bytes())
            return self.cleanup()

        while not self._signal_stop:
            if len(multiplayer_queue) == 2:
                return self.play_2p_game()

    def start_game(self):
        data = 'Two Player? (y/n): '
        message = ServerMessage(len(data), data)
        self.sock.sendall(message.to_raw_bytes())

        data = self.sock.recv(1024)
        if data == b'':
            return self.cleanup()

        response = ClientMessage.from_raw_bytes(data)
        if response.data == 'y':
            self.start_2p_game()
        else:
            self.start_1p_game()

        data = self.sock.recv(1024)
        if data == b'':
            return

        response = ClientMessage.from_raw_bytes(data)
        if response.data == 'Terminate':
            return self.cleanup()

    def cleanup(self):
        global mp_game_data, mp_word, multiplayer_queue, priority, turn, mp_game_over, mp_message

        self.sock.close()
        conn = connections[self]
        if self in multiplayer_queue:
            del multiplayer_queue[self]
            del priority[self]

        if len(multiplayer_queue) == 0:
            mp_game_data = None
            mp_word = None
            turn = 1
            mp_game_over = False
            mp_message = None

        print(f'Terminated connection from {conn.addr[0]}:{conn.addr[1]}')
        conn.signal_close = True

    def stop(self):
        self._signal_stop = True


class Connection:
    def __init__(self, thread: GameThread, csock: socket.socket, addr):
        self.thread = thread
        self.sock = csock
        self.addr = addr
        self.signal_close = False

    def close(self):
        self.thread.stop()
        self.thread.join(timeout=1)


def start_server(port):
    global sock, connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', port))
    sock.listen()

    while True:
        csock, addr = sock.accept()
        print(f'Accepted connection from {addr[0]}:{addr[1]}')

        deletes = []
        for thread, conn in connections.items():
            if conn.signal_close:
                conn.close()
                deletes.append(thread)

        for t in deletes:
            del connections[t]

        if len(connections) == 3:
            data = 'Server overloaded'
            message = ServerMessage(len(data), data)
            csock.sendall(message.to_raw_bytes())
            csock.close()
            print(f'Terminated connection from {addr[0]}:{addr[1]}')
            continue

        thread = GameThread(csock)
        conn = Connection(thread, csock, addr)
        thread.start()
        connections[thread] = conn


def cleanup():
    print('Shutting down server')
    for thread, conn in connections.items():
        thread.cleanup()
        conn.close()

    sock.close()


def initialize_dictionary(file):
    global word_len, dictionary
    dictionary.clear()
    with open(file) as f:
        file_info_line = f.readline().strip()
        word_len, num_words = tuple(map(int, file_info_line.split()))
        for i in range(num_words):
            dictionary.append(f.readline().strip())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the Hangman server')
    parser.add_argument('port', help='The port to bind to', type=int)
    parser.add_argument('dictionary', nargs='?', help='Optional filename of dictionary to use')
    args = parser.parse_args()

    if args.dictionary:
        initialize_dictionary(args.dictionary)

    try:
        start_server(args.port)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
