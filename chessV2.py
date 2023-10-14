

class Board:
    def __init__(self, fen):
        self.board = []
        self.K = False
        self.Q = False
        self.k = False
        self.q = False
        self.ep_targetsq = None
        # use the FEN string input to generate the starting postion of the board
        fen = fen.split()
        # place the pieces
        for char in fen[0]:
            if char in "rnbqkpRNBQKP":
                self.board.append(char)
        # place the empty squares
            elif char in "12345678":
                for _ in range(int(char)):
                    self.board.append("-")
        # set black or white to move
        for char in fen[1]:
            if char == "w":
                self.white_to_move = True
            else:
                self.white_to_move = False
        # set castling rights
        for char in fen[2]:
            if char == "K":
                self.K = True
            elif char == "Q":
                self.Q = True
            elif char == "k":
                self.k = True
            elif char == "q":
                self.q = True
        # set en_passant target square and the full/half move numbers
        if not fen[3] == "-":
            self.ep_targetsq = fen[3]
        self.halfmove_num = int(fen[4])
        self.halfmove_nums = []
        self.fullmove_num = int(fen[5])
        # create an object for each position in the board in order to keep track of
        # position, color, and what pieces have moved
        self.obj_board = [["-"] for _ in range(64)]
        for pos, piece in enumerate(self.board):
            if piece == "-":
                self.obj_board[pos] = EmptySquare(pos)
            elif piece == "r":
                self.obj_board[pos] = Rook(pos, "black")
            elif piece == "n":
                self.obj_board[pos] = Knight(pos, "black")
            elif piece == "b":
                self.obj_board[pos] = Bishop(pos, "black")
            elif piece == "q":
                self.obj_board[pos] = Queen(pos, "black")
            elif piece == "k":
                self.obj_board[pos] = King(pos, "black")
            elif piece == "p":
                self.obj_board[pos] = Pawn(pos, "black")
            elif piece == "R":
                self.obj_board[pos] = Rook(pos, "white")
            elif piece == "N":
                self.obj_board[pos] = Knight(pos, "white")
            elif piece == "B":
                self.obj_board[pos] = Bishop(pos, "white")
            elif piece == "Q":
                self.obj_board[pos] = Queen(pos, "white")
            elif piece == "K":
                self.obj_board[pos] = King(pos, "white")
            elif piece == "P":
                self.obj_board[pos] = Pawn(pos, "white")
        # initialize all lists of moves and attacked squares
        self.legal_moves = []
        self.white_moves = []
        self.black_moves = []
        self.white_attacked_squares = []
        self.black_attacked_squares = []
        self.move_log = []
        self.captured_pieces = []
        self.captured_objects = []
        self.moved_bools = []
        self.promoted_pieces = []
        self.promoted_objects = []
        self.ep_log = []
        self.enpassanted_piece = []
        self.enpassanted_object = []
        self.white_castling = []
        self.black_castling = []
        self.previous_boards = []
        self.not_quiet = []

    def print_board(self):
        for row in range(0, 64, 8):
            for pos in range(row, row + 8):
                print(self.board[pos], end=" ")
            print()


    def get_legal_moves(self):
        self.legal_moves = []
        self.castling = []
        if self.white_to_move:
            self.get_white_moves()
            # check if moves are legal by making each move and seeing if the king is in check
            for move in self.white_moves:
                legal = True
                self.make_move(move)
                self.get_black_moves()
                for square in self.black_attacked_squares:
                    if self.board[square] == "K":
                        legal = False
                # castling rules
                if move in self.white_castling:
                    if move == (60, 62) and self.board[62] == "K":
                        if 60 in self.black_attacked_squares or 61 in self.black_attacked_squares or 62 in self.black_attacked_squares:
                            legal = False
                    elif move == (60, 58) and self.board[58] == "K":
                        if 60 in self.black_attacked_squares or 59 in self.black_attacked_squares or 58 in self.black_attacked_squares:
                            legal = False
                if legal:
                    self.legal_moves.append(move)
                self.unmake_move()
                    
        else:
            self.get_black_moves()
            for move in self.black_moves:
                legal = True
                self.make_move(move)
                self.get_white_moves()
                for square in self.white_attacked_squares:
                    if self.board[square] == "k":
                        legal = False
                # castling rules
                if move in self.black_castling:
                    if move == (4, 6) and self.board[6] == "k":
                        if 4 in self.white_attacked_squares or 5 in self.white_attacked_squares or 6 in self.white_attacked_squares:
                            legal = False
                    elif move == (4, 2) and self.board[2] == "k":
                        if 4 in self.white_attacked_squares or 3 in self.white_attacked_squares or 2 in self.white_attacked_squares:
                            legal = False
                if legal:
                    self.legal_moves.append(move)
                self.unmake_move()
            

    def get_white_moves(self):
        self.white_moves = []
        self.white_attacked_squares = []
        for pos, piece in enumerate(self.obj_board):
            if piece.color == "white":
                if type(piece) == Pawn:
                    # get moves for pawn moving two one or two squares forward
                    if 8 <= pos - 8 <= 63 and self.board[pos - 8] == "-":
                        self.white_moves.append((pos, pos - 8))
                        if 8 <= pos - 16 <= 63 and self.board[pos - 16] == "-" and piece.has_moved == False:
                            self.white_moves.append((pos, pos - 16))
                    elif 0 <= pos - 8 <= 7 and self.board[pos - 8] == "-":
                        self.white_moves.extend(((pos, pos-8, "q"), (pos, pos-8, "r"), (pos, pos-8, "n"), (pos, pos-8, "b")))
                    # get attacked squares and moves for diagonal
                    # (attacked square no matter what, valid move only if enemy piece on target_pos)
                    row = piece.pos // 8
                    col = piece.pos % 8
                    # to the left
                    target_pos = pos - 9
                    target_row = target_pos // 8
                    target_col = target_pos % 8
                    # check if target square is within board range
                    if 8 <= target_pos <= 63 and target_row == row - 1 and target_col == col - 1:
                        self.white_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "black":
                            self.white_moves.append((pos, target_pos))
                        elif target_pos == self.ep_targetsq:
                            self.white_moves.append((pos, target_pos))

                    # promotion logic
                    elif 0 <= target_pos <= 7 and target_row == row - 1 and target_col == col - 1:
                        self.white_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "black":
                            self.white_moves.extend(((pos, target_pos, "q"), (pos, target_pos, "r"), (pos, target_pos, "n"), (pos, target_pos, "b")))

                    # to the right
                    target_pos = pos - 7
                    target_row = target_pos // 8
                    target_col = target_pos % 8
                    # check if target square is within board range
                    if 8 <= target_pos <= 63 and target_row == row - 1 and target_col == col + 1:
                        self.white_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "black":
                            self.white_moves.append((pos, target_pos))
                        elif target_pos == self.ep_targetsq:
                            self.white_moves.append((pos, target_pos))

                    # promotion
                    elif 0 <= target_pos <= 7 and target_row == row - 1 and target_col == col + 1:
                        self.white_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "black":
                            self.white_moves.extend(((pos, target_pos, "q"), (pos, target_pos, "r"), (pos, target_pos, "n"), (pos, target_pos, "b")))

                    
                elif type(piece) == Knight:
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    possible_moves = [
                        (current_col + 1, current_row + 2),
                        (current_col + 2, current_row + 1),
                        (current_col + 2, current_row - 1),
                        (current_col + 1, current_row - 2),
                        (current_col - 1, current_row - 2),
                        (current_col - 2, current_row - 1),
                        (current_col - 2, current_row + 1),
                        (current_col - 1, current_row + 2),
                    ]

                    for move in possible_moves:
                        col, row = move
                        if 0 <= col < 8 and 0 <= row < 8:
                            target_pos = row * 8 + col
                            if self.obj_board[target_pos].color != "white":
                                self.white_moves.append((pos, target_pos))
                                self.white_attacked_squares.append(target_pos)

                elif type(piece) == Bishop:
                    # logic for bishop
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    # diagonal moves
                    directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
                    for dir_col, dir_row in directions:
                        col, row = current_col, current_row
                        while True:
                            col += dir_col
                            row += dir_row
                            if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "white":
                                    break  # stop sliding when hitting a friendly piece
                                self.white_moves.append((pos, target_pos))
                                self.white_attacked_squares.append(target_pos)
                                if self.obj_board[target_pos].color == "black":
                                    break  # stop sliding after capturing an enemy piece`
                            else:
                                break

                elif type(piece) == Rook:
                    # logic for Rook
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    # horizontal and vertical moves
                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dir_col, dir_row in directions:
                        col, row = current_col, current_row
                        while True:
                            col += dir_col
                            row += dir_row
                            if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "white":
                                    break  # stop sliding when hitting a friendly piece
                                self.white_moves.append((pos, target_pos))
                                self.white_attacked_squares.append(target_pos)
                                if self.obj_board[target_pos].color == "black":
                                    break  # stop sliding after capturing an enemy piece
                            else: break

                elif type(piece) == Queen:
                    # same as bishop and rook, just directions is extended
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dir_col, dir_row in directions:
                        col, row = current_col, current_row
                        while True:
                            col += dir_col
                            row += dir_row
                            if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "white":
                                    break  # stop sliding when hitting a friendly piece
                                self.white_moves.append((pos, target_pos))
                                self.white_attacked_squares.append(target_pos)
                                if self.obj_board[target_pos].color == "black":
                                    break  # stop sliding after capturing an enemy piece
                            else:
                                break

                elif type(piece) == King:
                    directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dir_col, dir_row in directions:
                        current_col = piece.pos % 8
                        current_row = piece.pos // 8
                        col = current_col + dir_col
                        row = current_row + dir_row
                        if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "white":
                                    continue
                                self.white_moves.append((pos, target_pos))
                                self.white_attacked_squares.append(target_pos)

                    
                    # white castling short
                    if piece.has_moved == False and self.K == True and self.obj_board[63].has_moved == False:
                        if self.board[61] == "-" and self.board[62] == "-":
                            self.white_moves.append((60, 62))
                            self.white_castling.append((60, 62))
                        
                    # white castling long  
                    if piece.has_moved == False and self.Q == True and self.obj_board[56].has_moved == False:
                        if self.board[57] == "-" and self.board[58] == "-" and self.board[59] == "-":
                            self.white_moves.append((60, 58))
                            self.white_castling.append((60, 58))

    def get_black_moves(self):
        self.black_moves = []
        self.black_attacked_squares = []
        for pos, piece in enumerate(self.obj_board):
            if piece.color == "black":
                if type(piece) == Pawn:
                    # get moves for pawn moving two one or two squares forward
                    if 0 <= pos + 8 <= 55 and self.board[pos + 8] == "-":
                        self.black_moves.append((pos, pos + 8))
                        if 0 <= pos + 16 <= 63 and self.board[pos + 16] == "-" and piece.has_moved == False:
                            self.black_moves.append((pos, pos + 16))
                    if 56 <= pos + 8 <= 63 and self.board[pos + 8] == "-":
                        self.black_moves.extend(((pos, pos+8, "q"), (pos, pos+8, "r"), (pos, pos+8, "n"), (pos, pos+8, "b")))
                    # get attacked squares and moves for diagonal
                    # (attacked square no matter what, valid move only if enemy piece on target_pos)
                    row = piece.pos // 8
                    col = piece.pos % 8
                    # to the left
                    target_pos = pos + 9
                    target_row = target_pos // 8
                    target_col = target_pos % 8
                    # check if target square is within board range
                    if 0 <= target_pos <= 55 and target_row == row + 1 and target_col == col + 1:
                        self.black_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "white":
                            self.black_moves.append((pos, target_pos))
                        elif target_pos == self.ep_targetsq:
                            self.black_moves.append((pos, target_pos))

                    # promotion
                    elif 56 <= target_pos <= 63 and target_row == row + 1 and target_col == col + 1:
                        self.black_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "white":
                            self.black_moves.extend(((pos, target_pos, "q"), (pos, target_pos, "r"), (pos, target_pos, "n"), (pos, target_pos, "b")))

                    # to the right
                    target_pos = pos + 7
                    target_row = target_pos // 8
                    target_col = target_pos % 8
                    # check if target square is within board range
                    if 0 <= target_pos <= 55 and target_row == row + 1 and target_col == col - 1:
                        self.black_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "white":
                            self.black_moves.append((pos, target_pos))
                        elif target_pos == self.ep_targetsq:
                            self.black_moves.append((pos, target_pos))

                    # promotion
                    elif 56 <= target_pos <= 63 and target_row == row + 1 and target_col == col - 1:
                        self.black_attacked_squares.append(target_pos)
                        if self.obj_board[target_pos].color == "white":
                            self.black_moves.extend(((pos, target_pos, "q"), (pos, target_pos, "r"), (pos, target_pos, "n"), (pos, target_pos, "b")))


                elif type(piece) == Knight:
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    possible_moves = [
                        (current_col + 1, current_row + 2),
                        (current_col + 2, current_row + 1),
                        (current_col + 2, current_row - 1),
                        (current_col + 1, current_row - 2),
                        (current_col - 1, current_row - 2),
                        (current_col - 2, current_row - 1),
                        (current_col - 2, current_row + 1),
                        (current_col - 1, current_row + 2),
                    ]

                    for move in possible_moves:
                        col, row = move
                        if 0 <= col < 8 and 0 <= row < 8:
                            target_pos = row * 8 + col
                            if self.obj_board[target_pos].color != "black":
                                self.black_moves.append((pos, target_pos))
                                self.black_attacked_squares.append(target_pos)
                
                elif type(piece) == Bishop:
                    # logic for bishop
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    # diagonal moves
                    directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
                    for dir_col, dir_row in directions:
                        col, row = current_col, current_row
                        while True:
                            col += dir_col
                            row += dir_row
                            if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "black":
                                    break  # stop sliding when hitting a friendly piece
                                self.black_moves.append((pos, target_pos))
                                self.black_attacked_squares.append(target_pos)
                                if self.obj_board[target_pos].color == "white":
                                    break  # stop sliding after capturing an enemy piece`
                            else:
                                break
                
                elif type(piece) == Rook:
                    # logic for Rook
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    # horizontal and vertical moves
                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dir_col, dir_row in directions:
                        col, row = current_col, current_row
                        while True:
                            col += dir_col
                            row += dir_row
                            if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "black":
                                    break  # stop sliding when hitting a friendly piece
                                self.black_moves.append((pos, target_pos))
                                self.black_attacked_squares.append(target_pos)
                                if self.obj_board[target_pos].color == "white":
                                    break  # stop sliding after capturing an enemy piece
                            else: break

                elif type(piece) == Queen:
                    # same as bishop and rook, just directions is extended
                    current_col = piece.pos % 8
                    current_row = piece.pos // 8
                    directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dir_col, dir_row in directions:
                        col, row = current_col, current_row
                        while True:
                            col += dir_col
                            row += dir_row
                            if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "black":
                                    break  # stop sliding when hitting a friendly piece
                                self.black_moves.append((pos, target_pos))
                                self.black_attacked_squares.append(target_pos)
                                if self.obj_board[target_pos].color == "white":
                                    break  # stop sliding after capturing an enemy piece`
                            else:
                                break

                elif type(piece) == King:
                    directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dir_col, dir_row in directions:
                        current_col = piece.pos % 8
                        current_row = piece.pos // 8
                        col = current_col + dir_col
                        row = current_row + dir_row
                        if 0 <= col < 8 and 0 <= row < 8:
                                target_pos = row * 8 + col
                                if self.obj_board[target_pos].color == "black":
                                    continue
                                self.black_moves.append((pos, target_pos))
                                self.black_attacked_squares.append(target_pos)

                    # black castling short
                    if piece.has_moved == False and self.k == True and self.obj_board[7].has_moved == False:
                        if self.board[5] == "-" and self.board[6] == "-":
                            self.black_moves.append((4, 6))
                            self.black_castling.append((4, 6))
                        
                    # black castling long  
                    if piece.has_moved == False and self.q == True and self.obj_board[0].has_moved == False:
                        if self.board[1] == "-" and self.board[2] == "-" and self.board[3] == "-":
                            self.black_moves.append((4, 2))
                            self.black_castling.append((4, 2))


    def move(self, algebraic_move):
        algebraic_move = list(algebraic_move)
        start_pos = chess_rows[algebraic_move[1]] * 8 + chess_columns[algebraic_move[0]]
        end_pos = chess_rows[algebraic_move[3]] * 8 + chess_columns[algebraic_move[2]]
        if len(algebraic_move) == 4:
            return((start_pos, end_pos))
        elif len(algebraic_move) == 5:
            return((start_pos, end_pos, algebraic_move[4]))


    def make_move(self, move):
        self.previous_boards.append(self.board[:])
        # get start_pos and end_pos of move
        self.move_log.append(move)
        start_pos = move[0]
        end_pos = move[1]
        # add captured pieces and objects to list
        self.captured_pieces.append(self.board[end_pos])
        self.captured_objects.append(self.obj_board[end_pos])
        self.moved_bools.append(self.obj_board[start_pos].has_moved)
        # add half-move count for fifty move rule
        self.halfmove_nums.append(self.halfmove_num)
        if self.board[end_pos] != "-":
            self.halfmove_num = 0
        else:
            self.halfmove_num += 1
        # change the board and object to reflect the move
        self.board[end_pos] = self.board[start_pos]
        self.board[start_pos] = "-"
        self.obj_board[end_pos] = self.obj_board[start_pos]
        self.obj_board[end_pos].pos = end_pos
        self.obj_board[start_pos] = EmptySquare(start_pos)
        # enpassant logic
        if type(self.obj_board[end_pos]) == Pawn and end_pos == self.ep_targetsq:
            if self.white_to_move:
                self.enpassanted_piece.append(self.board[self.ep_targetsq + 8])
                self.enpassanted_object.append(self.obj_board[self.ep_targetsq + 8])
                self.board[self.ep_targetsq + 8] = "-"
                self.obj_board[self.ep_targetsq + 8] = EmptySquare(self.ep_targetsq + 8)
            else:
                self.enpassanted_piece.append(self.board[self.ep_targetsq - 8])
                self.enpassanted_object.append(self.obj_board[self.ep_targetsq - 8])
                self.board[self.ep_targetsq - 8] = "-"
                self.obj_board[self.ep_targetsq - 8] = EmptySquare(self.ep_targetsq - 8)
            self.halfmove_num = 0

        self.ep_log.append(self.ep_targetsq)
        if abs(start_pos - end_pos) == 16 and type(self.obj_board[end_pos]) == Pawn:
            self.ep_targetsq = (start_pos + end_pos) // 2
        else:
            self.ep_targetsq = None
        # promotion logic
        if len(move) == 3:
            self.promoted_pieces.append(self.board[end_pos])
            self.promoted_objects.append(self.obj_board[end_pos])
            if self.obj_board[end_pos].color == "white":
                self.board[end_pos] = move[2].title()
                if move[2] == "q":
                    self.obj_board[end_pos] = Queen(end_pos, "white")
                elif move[2] == "n":
                    self.obj_board[end_pos] = Knight(end_pos, "white")
                elif move[2] == "b":
                    self.obj_board[end_pos] = Bishop(end_pos, "white")
                else:
                    self.obj_board[end_pos] = Rook(end_pos, "white")
            else:
                self.board[end_pos] = move[2]
                if move[2] == "q":
                    self.obj_board[end_pos] = Queen(end_pos, "black")
                elif move[2] == "n":
                    self.obj_board[end_pos] = Knight(end_pos, "black")
                elif move[2] == "b":
                    self.obj_board[end_pos] = Bishop(end_pos, "black")
                else:
                    self.obj_board[end_pos] = Rook(end_pos, "black")
        # castling logic

        if move in self.white_castling or move in self.black_castling:
            if move == (60, 62) and self.board[62] == "K":
                rook_start_pos = 63
                rook_end_pos = 61
                self.castling = True
            elif move == (60, 58) and self.board[58] == "K":
                rook_start_pos = 56
                rook_end_pos = 59
                self.castling = True
            elif move == (4, 6) and self.board[6] == "k":
                rook_start_pos = 7
                rook_end_pos = 5
                self.castling = True
            elif move == (4, 2) and self.board[2] == "k":
                rook_start_pos = 0
                rook_end_pos = 3
                self.castling = True
            else:
                self.castling = False

            if self.castling:
                self.board[rook_end_pos] = self.board[rook_start_pos]
                self.obj_board[rook_end_pos] = self.obj_board[rook_start_pos]
                self.obj_board[rook_end_pos].pos = rook_end_pos
                self.board[rook_start_pos] = "-"
                self.obj_board[rook_start_pos] = EmptySquare(start_pos)

        self.obj_board[end_pos].has_moved = True

        if not self.white_to_move:
            self.fullmove_num += 1
        self.white_to_move = not self.white_to_move
    

    def unmake_move(self):
        self.previous_boards.pop()
        move = self.move_log.pop()
        self.ep_targetsq = self.ep_log.pop()
        self.halfmove_num = self.halfmove_nums.pop()
        if self.white_to_move:
            self.fullmove_num -= 1
        self.white_to_move = not self.white_to_move
        # get start_pos and end_pos
        start_pos = move[0]
        end_pos = move[1]

        # unpromote before changing board state back
        if len(move) == 3:
            self.board[end_pos] = self.promoted_pieces.pop()
            self.obj_board[end_pos] = self.promoted_objects.pop()
        # change board state back
        self.obj_board[end_pos].has_moved = self.moved_bools.pop()
        self.board[start_pos] = self.board[end_pos]
        self.board[end_pos] = self.captured_pieces.pop()
        self.obj_board[start_pos] = self.obj_board[end_pos]
        self.obj_board[start_pos].pos = start_pos
        self.obj_board[end_pos] = self.captured_objects.pop()
        # un passant
        if end_pos == self.ep_targetsq and type(self.obj_board[start_pos]) == Pawn:
            if self.white_to_move:
                self.board[self.ep_targetsq + 8] = self.enpassanted_piece.pop()
                self.obj_board[self.ep_targetsq + 8] = self.enpassanted_object.pop()
            else:
                self.board[self.ep_targetsq - 8] = self.enpassanted_piece.pop()
                self.obj_board[self.ep_targetsq - 8] = self.enpassanted_object.pop()

        # un castle
        if move in self.white_castling or move in self.black_castling:
            if move == (60, 62) and self.board[60] == "K":
                rook_start_pos = 63
                rook_end_pos = 61
                self.castling = True
            elif move == (60, 58) and self.board[60] == "K":
                rook_start_pos = 56
                rook_end_pos = 59
                self.castling = True
            elif move == (4, 6) and self.board[4] == "k":
                rook_start_pos = 7
                rook_end_pos = 5
                self.castling = True
            elif move == (4, 2) and self.board[4] == "k":
                rook_start_pos = 0
                rook_end_pos = 3
                self.castling = True
            else:
                self.castling = False

            if self.castling:
                self.obj_board[rook_end_pos].pos = rook_start_pos
                self.board[rook_start_pos] = self.board[rook_end_pos]
                self.obj_board[rook_start_pos] = self.obj_board[rook_end_pos]
                self.board[rook_end_pos] = "-"
                self.obj_board[rook_end_pos] = EmptySquare(rook_end_pos)
        

class EmptySquare:
    def __init__(self, pos):
        self.pos = pos
        self.color = None
        self.has_moved = None


class Pawn:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.row = self.pos // 8
        if self.color == "white":
            if self.row == 6:
                self.has_moved = False
            else:
                self.has_moved = True
        else:
            if self.row == 1:
                self.has_moved = False
            else:
                self.has_moved = True


class Knight:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.has_moved = None


class Bishop:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.has_moved = None
        

class Rook:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.has_moved = False
        

class Queen:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.has_moved = None


class King:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        if self.color == "white":
            if self.pos == 60:
                self.has_moved = False
            else:
                self.has_moved = True
        else:
            if self.pos == 4:
                self.has_moved = False
            else:
                self.has_moved = True


class Game:
    def __init__(self, fen):
        self.board = Board(fen)
        self.repetition_list = []
    
    def checkmate(self):
        if self.board.legal_moves == []:
            if self.board.white_to_move:
                for square in self.board.black_attacked_squares:
                    if self.board.board[square] == "K":
                        return True
                return False
            else:
                for square in self.board.white_attacked_squares:
                    if self.board.board[square] == "k":
                        return True
                return False

    def stalemate(self):
        if self.board.legal_moves == []:
            return True

    def perft(self, depth):
        if depth == 0:
            return 1
        self.board.get_legal_moves()
        num_positions = 0
        for move in self.board.legal_moves:
            self.board.make_move(move)
            num_positions += self.perft(depth - 1)
            self.board.unmake_move()
        return num_positions


chess_rows = {"8": 0, "7": 1, "6": 2, "5": 3, "4": 4, "3": 5, "2": 6, "1": 7}
chess_columns = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}


def main():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    game = Game(fen)
    # print(game.perft(4))
    # command line chess game loop
    while True:
        if game.board.white_to_move:
            game.board.print_board()
            game.board.get_legal_moves()
            while True:
                move = game.board.move(input("White to Move: "))
                if move in game.board.legal_moves:
                    game.board.make_move(move)
                    break
                else:
                    print("Invalid move.")
                    continue
        if not game.board.white_to_move: 
            game.board.print_board()
            game.board.get_legal_moves()
            while True:
                move = game.board.move(input("Black to Move: "))
                if move in game.board.legal_moves:
                    game.board.make_move(move)
                    break
                else:
                    print("Invalid move.")
                    continue


if __name__ == "__main__":
    main()
