# cs3251-hangman

## Environment
This project was developed using Python 3.8.2 on macOS 11 (Big Sur). If possible, this project will run best on a macOS/Unix computer, but should work fine on Linux as well

This project does not require any non-builtin Python libraries. However, in my development I set up a virtual environment such that `python` points to my Python 3.8.2 binary. If a virtual environment isn't being used, then `python` should be replaced with `python3` (or the corresponding command) in all instances.

## Overview
This project uses the Python [socket](https://docs.python.org/3/library/socket.html) library to implement server-client functionality with native TCP sockets. The server and the client communicate using a standard binary message format; for this project I built classes to serve as wrappers (`ServerMessage` and `ClientMessage` in [message.py](message.py)) around these messages, with convenience methods to convert to and from the standard message format

Additionally, the server and client frequently exchange game data, such as the number of incorrect guesses as well as the letters which have been revealed so far. I defined a class (`GameData` in [game.py](game.py)) as a wrapper around this data, with convenience methods to convert to and from `ServerMessage`s

The server supports multiple concurrent connections, through the use of the Python [threading](https://docs.python.org/3/library/threading.html) library and the custom `GameThread` class (defined in [server.py](server.py)). As the main thread accepts a connection from a new client socket, it spins up a new thread to handle the game logic with that client while continuing to listen for more clients. These threads and the associated client sockets are stored in a dictionary for graceful shutdown upon various conditions, such as a keyboard interrupt, and all of their game data is kept separate. If the number of concurrent connections reaches 3, then no new connections are allowed until one of the connected clients drops.

## Running the code
For help running either the `server.py` or `client.py` files, you can specify the option `-h` or `--help` for more information. Respectively, that command displays the following information:

Server
```
% python server.py -h
usage: server.py [-h] port [dictionary]

Start the Hangman server

positional arguments:
  port        The port to bind to
  dictionary  Optional filename of dictionary to use

optional arguments:
  -h, --help  show this help message and exit

```

Client
```
% python client.py -h
usage: client.py [-h] ip port

Start a Hangman client

positional arguments:
  ip          The server IP address
  port        The server port

optional arguments:
  -h, --help  show this help message and exit
```

## Test Cases
The dictionary of words used is included in this repository as [words.txt](words.txt)

The server was run with the following command: `python server.py 3000 words.txt`

Server output (for both the win and loss scenarios)
```
Accepted connection from 127.0.0.1:64521
Terminated connection from 127.0.0.1:64521
Accepted connection from 127.0.0.1:64531
Terminated connection from 127.0.0.1:64531
```

The client was run (for both the win and loss scenarios) with the following command: `python client.py 127.0.0.1 3000`

Client win output
```
Two Player? (y/n): n
Ready to start game? (y/n): 3
_ _ _ _
Incorrect Guesses:

Letter to guess:
e
_ _ e _
Incorrect Guesses:

Letter to guess:
a
_ _ e _
Incorrect Guesses: a

Letter to guess:
a
Error! Letter a has been guessed before, please guess another letter.

Letter to guess:
?
Error! Please guess one LETTER.

Letter to guess:
asd
Error! Please guess ONE letter.

Letter to guess:
p
p _ e _
Incorrect Guesses: a

Letter to guess:
r
p r e _
Incorrect Guesses: a

Letter to guess:
y
You Win!
```

Client loss output
```
Two Player? (y/n): n
Ready to start game? (y/n): 3
_ _ _ _
Incorrect Guesses:

Letter to guess:
a
_ _ _ _
Incorrect Guesses: a

Letter to guess:
e
_ _ e _
Incorrect Guesses: a

Letter to guess:
i
_ _ e _
Incorrect Guesses: a i

Letter to guess:
o
_ _ e _
Incorrect Guesses: a i o

Letter to guess:
d
_ _ e _
Incorrect Guesses: a i o d

Letter to guess:
d
Error! Letter d has been guessed before, please guess another letter.

Letter to guess:
s
_ _ e _
Incorrect Guesses: a i o d s

Letter to guess:
p
p _ e _
Incorrect Guesses: a i o d s

Letter to guess:
l
You Lose: prey
```