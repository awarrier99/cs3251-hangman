import argparse
import socket

from message import ClientMessage, ServerMessage
from game import GameData


sock: socket.socket


def connect_server(ip, port) -> bytes:
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock.recv(1024)


def cleanup():
    data = 'Terminate'
    message = ClientMessage(len(data), data)
    sock.sendall(message.to_raw_bytes())


def display_prompt(game_data: GameData):
    for idx, letter in enumerate(game_data.word):
        print(letter, end='')
        if idx != len(game_data.word) - 1:
            print(' ', end='')

    print('\nIncorrect Guesses:', end='')
    for guess in game_data.incorrect:
        print(f' {guess}', end='')

    print('\n\nLetter to guess:')


def guess_letter(game_data: GameData):
    while True:
        c = input().lower()

        if len(c) > 1:
            print('Error! Please guess ONE letter.\n')
            print('Letter to guess:')
            continue

        if not c.isalpha():
            print('Error! Please guess one LETTER.\n')
            print('Letter to guess:')
            continue

        if c in game_data.incorrect or c in game_data.word:
            print(f'Error! Letter {c} has been guessed before, please guess another letter.\n')
            print('Letter to guess:')
            continue

        break

    message = ClientMessage(1, c)
    sock.sendall(message.to_raw_bytes())


def create_1p_game():
    data = sock.recv(1024)
    if data == b'':
        print('Terminated by server')
        return

    response = ServerMessage.from_raw_bytes(data)

    option = input(response.data)
    if option == 'y':
        message = ClientMessage(1, 'y')
    elif option == 'n':
        message = ClientMessage(1, 'n')
    else:
        try:
            message = ClientMessage(1, int(option))
        except ValueError:
            print('Invalid option. Exiting')
            return

    sock.sendall(message.to_raw_bytes())
    while True:
        data = sock.recv(1024)
        if data == b'':
            print('Terminated by server')
            break

        response = ServerMessage.from_raw_bytes(data)
        if response.msg_flag == 0:
            game_data = GameData.from_message(response)
            display_prompt(game_data)
            guess_letter(game_data)
        else:
            print(response.data)
            return cleanup()


def create_2p_game():
    data = sock.recv(1024)
    if data == b'':
        print('Terminated by server')
        return

    response = ServerMessage.from_raw_bytes(data)
    print(response.data)

    while True:
        data = sock.recv(1024)
        if data == b'':
            print('Terminated by server')
            break

        response = ServerMessage.from_raw_bytes(data)
        if response.msg_flag == 0:
            game_data = GameData.from_message(response)
            display_prompt(game_data)
            guess_letter(game_data)
        else:
            print(response.data)
            if 'You Win' in response.data or 'You Lose' in response.data:
                return cleanup()


def create_game(data: bytes):
    response = ServerMessage.from_raw_bytes(data)
    if response.data == 'Server overloaded':
        print(response.data)
        return

    option = input(response.data)
    if option == 'y':
        message = ClientMessage(1, 'y')
        sock.sendall(message.to_raw_bytes())
        create_2p_game()
    elif option == 'n':
        message = ClientMessage(1, 'n')
        sock.sendall(message.to_raw_bytes())
        create_1p_game()
    else:
        print('Invalid option. Exiting')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start a Hangman client')
    parser.add_argument('ip', help='The server IP address')
    parser.add_argument('port', help='The server port', type=int)
    args = parser.parse_args()

    try:
        create_game(connect_server(args.ip, args.port))
    except KeyboardInterrupt:
        cleanup()
    finally:
        sock.close()
