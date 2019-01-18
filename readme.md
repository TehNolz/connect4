Readme for Connect4 v2;

Features;
* Singleplayer, with up to 8 players.
* Online multiplayer, with up to 8 players.
	Designed for local networks only. 
	Internet play is theoretically possible (if the host port-forwards port 12345), but has not been tested and is not officially supported.
* Board sizes up to 10x18
* Spectator Mode, allowing you to watch other people play.
* A dumb-as-rocks AI.
* Automatic win detection
* An undo mechanism, allowing players to undo every move till the beginning of the game.
* A configurable winning sequence length.
* Mouse controls
* Incorrect input handling

These issues have not been fixed because they are either very complicated, would require a lot of changes (thus introducing even more bugs), or are caused by witchcraft/black magic.
None of the issues listed below prevent the game from being played from beginning to end.
Known issues;
Server;
* If, for whatever reason, the server hangs, the game will become unplayable until the server process is manually terminated.
	The server will show an error message if it can't start because of another server process.
* The server hangs when a client disconnects while the server is waiting for clients to connect.
* If a player disconnects while the game is ongoing (without using the Quit button), the server (and in turn, every client) will throw an exception and hang.

Client;
* The current player indicator doesn't update its color when playing on multiplayer.
	For some reason, it works fine when playing singleplayer, even though its the exact same code.
* While a client is waiting for its turn, Windows will often think that the client is not responding.
* Due to the above; players using Spectator mode will always have Windows think that their clients aren't responding.
	These issues are caused because the sockets are in blocking mode, which causes them to stall the script until their operation completes.
* Players cannot quit, undo the last move, or reset the game if its not their turn.
	Because the sockets are in blocking mode, clients have no way of sending commands to the server, as they're waiting for the server to respond.

AI;
* If the server hangs, any AI processes may hang as well. They will also have to be manually terminated.
* The game may hang when certain amount of AIs are used. Because of this, a game must always have at least 1 player.

Spectator;
* It's impossible to join an ongoing game as Spectator. Spectators must join before all players have joined the game.