# GarryKasPyrov
This is a chess engine and bot that I created completely from scratch in Python. The chessV2.py contains all the code I used for gathering every legal move
in a given chess positions, and when run, produces a command line version of chess that can be played using long algebraic notation (e2e4, d7d5, etc;). The file 
chessai.py contains code for both minimax and quiescence search algorithms along with alpha-beta pruning for the engines move search. The evalation of each node in 
the tree search is determined by the pieces value and its positional value based upon the very popular piece square tables by Tomasz Michniewski which can be found
here: https://www.chessprogramming.org/Simplified_Evaluation_Function. The garrykasparov.py file utilizes the chessai.py file for its move search, and implements
a very simple UCI protocol for chess engine communication. The entirety of the chessV2 engine system was perft tested in various positions and compared to stockfish's 
perft results, indicating that the move generation and move making was completely bug free. I used pyinstaller to turn garrykasparov.py into an executable file and then 
used the lichess-bot repository as a bridge to the Lichess API. 
