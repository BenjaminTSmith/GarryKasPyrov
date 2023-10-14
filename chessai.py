import chessV2
from piece_heatmaps import positional_value


# if middle game, gather heuristic of future positions
material_values = {
    "P": 100, "N": 320, "B": 330, "R": 500, "Q": 900
}


def heuristics(board):
    black_material = 0
    white_material = 0
    for pos, piece in enumerate(board):
        if piece in "pnbrq":
            black_material += material_values[piece.title()]
            black_material += positional_value(pos, piece)
        elif piece in "PNBRQ":
            white_material += material_values[piece]
            white_material += positional_value(pos, piece)
        elif piece == "k":
            black_material += positional_value(pos, piece)
        elif piece == "K":
            white_material += positional_value(pos, piece)

    return white_material - black_material


def evaluate_board(game):

    if game.checkmate():
        if game.board.white_to_move:
            return float('-inf')
        else:
            return float('inf')
    elif game.stalemate():
        return 0
    output = heuristics(game.board.board)

    return output


def minimax(game, depth, alpha, beta, maximizing_player):
    game.board.get_legal_moves()
    
    if game.board.legal_moves == []:
        return evaluate_board(game), None
    
    elif depth == 0:
        if is_quiet(game):
            return evaluate_board(game), None
        else:
            return quiescence(game, 1, alpha, beta, maximizing_player)
        
    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in game.board.legal_moves:
            game.board.make_move(move)
            eval_score, _ = minimax(game, depth - 1, alpha, beta, False)
            game.board.unmake_move()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in game.board.legal_moves:
            game.board.make_move(move)
            eval_score, _ = minimax(game, depth - 1, alpha, beta, True)
            game.board.unmake_move()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move


def quiescence(game, depth, alpha, beta, maximizing_player):
    game.board.get_legal_moves()
    if depth == 0 or game.board.legal_moves == [] or is_quiet(game):
        return evaluate_board(game), None
    else:
        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in game.board.not_quiet:
                game.board.make_move(move)
                eval_score, _ = quiescence(game, depth - 1, alpha, beta, False)
                game.board.unmake_move()
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in game.board.not_quiet:
                game.board.make_move(move)
                eval_score, _ = quiescence(game, depth - 1, alpha, beta, True)
                game.board.unmake_move()
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move
        

def is_quiet(game):
    game.board.not_quiet = []
    for move in game.board.legal_moves:
        if game.board.board[move[1]] in "nbrqNBRQ":
            game.board.not_quiet.append(move)
    if game.board.not_quiet == []:
        return True
    else:
        return False
    

def main():
    game = chessV2.Game("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    game.board.get_legal_moves()
    while True:
        if not game.board.white_to_move:
            game.board.print_board()
            game.board.get_legal_moves()
            if game.checkmate():
                print("Black wins by checkmate")
                break
            elif game.stalemate():
                print("Draw by stalemate.")
                break
            while True:
                move = game.board.move(input("White to Move: "))
                if move in game.board.legal_moves:
                    game.board.make_move(move)
                    break
                else:
                    print("Invalid move.")
                    continue
        if game.board.white_to_move: 
            game.board.get_legal_moves()
            if game.checkmate():
                print("White wins by checkmate")
                break
            elif game.stalemate():
                print("Draw by stalemate.")
                break
            eval, best_move = minimax(game, 2, float('-inf'), float('inf'), True)
            print(f"Eval: {eval/100}")
            game.board.make_move(best_move)


if __name__ == "__main__":
    main()
