# cs3251-hangman

## Environment
This project was developed using Python 3.8.2 on macOS 11 (Big Sur). If possible, this project will run best on a macOS/Unix computer, but should work fine on Linux as well

This project does not require any non-builtin Python libraries

## Overview
This project uses the Python [sockets](https://docs.python.org/3/library/socket.html) library to implement server-client functionality. The server and the client communicate using a standard binary message format; for this project I built classes to serve as wrappers (`ServerMessage` and `ClientMessage` in [message.py](message.py)) around these messages, with convenience methods to convert to and from the standard message format

Additionally, the server and client frequently exchange game data, such as the number of incorrect guesses as well as the letters which have been revealed so far. I defined a class (`GameData` in [game.py](game.py)) as a wrapper around this data, with convenience methods to convert to and from `ServerMessage`s

## Running the code
For help running either the `server.py` or `client.py` files, you can specify the option `-h` or `--help` for more information. Respectively, that command displays the following information:

Server
```
% python server.py -h                                                                                                                                                           11/26/20 08:45:10 PM
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
% python client.py -h                                                                                                                                                           11/26/20 08:52:03 PM
usage: client.py [-h] ip port

Start a Hangman client

positional arguments:
  ip          The server IP address
  port        The server port

optional arguments:
  -h, --help  show this help message and exit
```
