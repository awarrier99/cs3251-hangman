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

## Starting a game
The first prompt will ask whether you want to play in multiplayer mode or not. Respond `y` for yes and `n` for single-player mode. If in single-player mode, continue as normal.

## Test cases
The dictionary of words used is included in this repository as [words.txt](words.txt)

The server (in every scenario) was run with the following command: `python server.py 3000 words.txt`
The client (in every scenario) was run with the following command: `python client.py 127.0.0.1 3000`

### Single-player mode
Server output (for both the win and loss scenarios)
```
Accepted connection from 127.0.0.1:64521
Client 127.0.0.1:64521 playing in single-player mode
Terminated connection from 127.0.0.1:64521
Accepted connection from 127.0.0.1:64531
Client 127.0.0.1:64531 playing in single-player mode
Terminated connection from 127.0.0.1:64531
```

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

### Multiplayer mode

Server output (for both the win and loss scenarios)
```
Accepted connection from 127.0.0.1:65423
Client 127.0.0.1:65423 playing in multiplayer mode
Accepted connection from 127.0.0.1:65424
Client 127.0.0.1:65424 playing in multiplayer mode
Terminated connection from 127.0.0.1:65423
Terminated connection from 127.0.0.1:65424
Accepted connection from 127.0.0.1:65426
Client 127.0.0.1:65426 playing in multiplayer mode
Accepted connection from 127.0.0.1:65428
Client 127.0.0.1:65428 playing in multiplayer mode
Terminated connection from 127.0.0.1:65428
Terminated connection from 127.0.0.1:65426
^CShutting down server
Terminated connection from 127.0.0.1:65426
Terminated connection from 127.0.0.1:65428
```

Client 1 win output
```
Two Player? (y/n): y
Waiting for other player!
Game Starting!
Waiting on Player 1...
Your Turn!
_ _ _ _
Incorrect Guesses:

Letter to guess:
a
Waiting on Player 2...
Your Turn!
_ _ _ e
Incorrect Guesses: a

Letter to guess:
s
Waiting on Player 2...
Your Turn!
m _ _ e
Incorrect Guesses: a s

Letter to guess:
i
Waiting on Player 2...
You Win! The word was mine
```

Client 2 win output
```
Two Player? (y/n): y
Game Starting!
Waiting on Player 1...
Your Turn!
_ _ _ _
Incorrect Guesses: a

Letter to guess:
e
Waiting on Player 1...
Your Turn!
_ _ _ e
Incorrect Guesses: a s

Letter to guess:
m
Waiting on Player 1...
Your Turn!
m i _ e
Incorrect Guesses: a s

Letter to guess:
i
Error! Letter i has been guessed before, please guess another letter.

Letter to guess:
n
You Win!
```

Client 1 loss output
```
Two Player? (y/n): y
Waiting for other player!
Game Starting!
Your Turn!
_ _ _ _
Incorrect Guesses:

Letter to guess:
a
Waiting on Player 2...
Your Turn!
_ _ _ a
Incorrect Guesses: q

Letter to guess:
w
Waiting on Player 2...
Your Turn!
_ _ _ a
Incorrect Guesses: q w z

Letter to guess:
x
Waiting on Player 2...
Your Turn!
_ _ _ a
Incorrect Guesses: q w z x l

Letter to guess:
y
You Lose: coma
```

Client 2 loss output
```
Two Player? (y/n): y
Game Starting!
Waiting on Player 1...
Your Turn!
_ _ _ a
Incorrect Guesses:

Letter to guess:
q
Waiting on Player 1...
Your Turn!
_ _ _ a
Incorrect Guesses: q w

Letter to guess:
z
Waiting on Player 1...
Your Turn!
_ _ _ a
Incorrect Guesses: q w z x

Letter to guess:
l
Waiting on Player 1...
You Lose: coma
```