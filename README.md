# Liar's Dice Variation
#### Video Demo: https://youtu.be/fMKVerkGD3U
#### Description:
##### In summary
This is my rendition of the popular dice game "Liar's dice".
The game written in Python, and is played at the command-line. It allows one user to play a game against up to 4 bots.

The game is implemented in `project.py` and it uses classes, defined in `liarsdice.py`.

Unit tests are implemented in the `pytest` frame work, and can be found in files `test_liarsdice.py` and `test_project.py`
##### Setup & running the game
- Be sure to first run `$ pip install -r requirements.txt`!
- To start the game, simply run `$ python project.py`.
- Simply follow the prompts at the command line (if no specific prompt - just press `Enter`).
- Quit the game at any time with `Ctrl + C` or `Ctrl + D`
##### Rules
Each player starts the game with 5 dice, that have 6 faces each.

The game is played in rounds. At the beginning of each round the players throw their dice, and keep the results (called here a 'hand') to themselves.

The player, whose turn it is, starts the round by making an assumption about how many occurences of a certain die (single for 'dice') there are in the results of all the players' hands. This assumption is called here a 'bid'. After the initial bid is made, the turn is passed to the next player, in clock-wise order.

Each next player now has two choices:
1. Either, to 'raise' the bid; or
2. To call 'Liar', thereby challenging the 'active bid' (the bid made by the player before them).

Raising the bid means providing a new bid where:
- Either, they claim more occurences of the same die face; or
- Claim any occurences of a higher die face.
If the bid is raised, the turn is again passed to the next player.

On the other hand, challenging the 'active bid' means that all dice are revealed (in the classic version of this game, the dice are thrown and kept hidden under a cup, so that other players may not see the player's hand). If there are at least as many dice of the face the bidder is claiming, then the challenger loses the round. Otherwise, the active bidder loses. It's important to note here that the game has a "'wild' ones" mode - this means that when that dice are revealed, die face 1 is counted as 1 ocurrence of the die in the active bid.

The loser of the round also loses one of their dice, and gets to make the first bid in the new round. If the loser is now all out of dice, they leave the game, and the next player in line makes the first bid.

Rounds keep getting played until only one player has any dice left. At that point, he gets pronounced as the winner.
##### Some notes on the usage
- There is no technical reason for limiting the number of players to five, but it was decided to do so because having more players than that makes for very long games.
- Although the dice in players' hands are represented with ASCII-art/pseudo graphics, the actual bids are made by typing-in integers (input like `......` for die face 6 is not supported).
- When accepting a bid, the program will keep reprompting if:
    - the inputed face for the bid is less than 1 and greater than 6;
    - the inputed count of occurences is larger than the number of all dice currently in play.
- The bots will awlays challenge a bid with face of 6 and count of all dice in play.
- Refusing to bid when asked, means you will be challenging the active bid.
##### Basic design
A game like "Liar's dice" has quite a few 'moving parts' that can be tricky to implement.

To represent all the main building blocks of the game, the following classes are defined in `liarsdice.py`:
- `Game` - An instance a of Game represents a game of "Liar's dice".
- `Round` - A Round instance represents one of the rounds in a game of "Liar's dice".
- `Player` - Holds the main properties & methods that a player needs. Has two sub-classes - Bot, and Human.
    - `Bot` - An instance of Bot represents one of the oponents that the user plays against.
    - `Human` - A sub class of Player that represents the user. Doesn't implement any methods as of now, but is used to differentiate between players.
- `Die` - A Die instance represents a single die (one of the players' dice)
- `Bid` - An instance of Bid represents a guess that at least as many occurences (count) of a die face are present within the concealed hands of all players

In particular, handling the interactions between players, and the round & turn rotations were (as expected) some of the main challenges.
The file `project.py` makes the whole thing work together. It acts as a controller, using instances of the classes defined in `liarsdice.py` in a way that closely follows the ruleset. The flow of `project.py` is as follows:
1. Greet user
2. Get number of players
3. Instantiate game & players
4. Start the game
    - Add & setup each round
    - Show hand to human player
    - Play turns
        - Player whose turn it is makes a bid or challenge
            - If a challenge is issued, it gets evaluated, and a loser of the round is declared
            - Else the bid is raised and the turn is passed to the next player
        - An announcement is made if the loser of the round leaves the game
5. When only a single player has any dice left, he is prounced the winner and the game closes
##### Limitations
When playing, you will notice that the bot players aren't particularly smart. This is because I consider the algorithm they use to 'make decisions' an implementation detail. One that can always be changed.

Currently, unless they're forced by the rules, the bots make their decision whether to challenge randomly, with an 80% bias towards raising the bid.

And speaking of raising - that is also done somewhat randomly. So long as there is no constraint from the rules, the bots will randomly decide whether to raise by face or by count.
- If they raise by face, they'll bid the closest higher face they have in their hand (or face + 1, if they don't have a higher face in their hand), for 1 occurences.
- And when they raise by count, they simply randomly choose between current count + 1, and the number of all dice in play.
