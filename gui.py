import chess
import pygame
import sys
from logic import ChessAI, QTable, visualize_tree

# gui config
WHITE = (245, 222, 179)
BLACK = (139, 69, 19)
HIGHLIGHT = (152, 251, 152)
MOVE_COLOR = (135, 206, 250)
BACKGROUND = (40, 40, 40)
SQUARE_SIZE = 80
FPS = 30

def load_pieces():
    pieces = {}
    names = {'P': 'P', 'N': 'N', 'B': 'B', 'R': 'R', 'Q': 'Q', 'K': 'K',
             'p': 'bp', 'n': 'bn', 'b': 'bb', 'r': 'br', 'q': 'bq', 'k': 'bk'}
    for key, name in names.items():
        pieces[key] = pygame.transform.scale(pygame.image.load(f"pieces/{name}.png"), (SQUARE_SIZE, SQUARE_SIZE))
    return pieces

def draw(screen, board, pieces, selected=None, moves=None, hint=None, status_text=""):
    screen.fill(BACKGROUND)
    board_size = SQUARE_SIZE * 8
    offset_x = (screen.get_width() - board_size) // 2
    offset_y = (screen.get_height() - board_size) // 2

    # Draw squares
    for rank in range(8):
        for file in range(8):
            rect = pygame.Rect(offset_x + file * SQUARE_SIZE, offset_y + rank * SQUARE_SIZE,
                              SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, WHITE if (rank + file) % 2 == 0 else BLACK, rect)

    # Draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            file = chess.square_file(square)
            rank = 7 - chess.square_rank(square)
            screen.blit(pieces[piece.symbol()], (offset_x + file * SQUARE_SIZE,
                                                offset_y + rank * SQUARE_SIZE))

    # Highlight selected square
    if selected:
        file, rank = selected
        pygame.draw.rect(screen, HIGHLIGHT,
                         (offset_x + file * SQUARE_SIZE, offset_y + rank * SQUARE_SIZE,
                          SQUARE_SIZE, SQUARE_SIZE), 3)

    # Highlight possible moves
    if moves:
        for file, rank in moves:
            pygame.draw.rect(screen, MOVE_COLOR,
                             (offset_x + file * SQUARE_SIZE, offset_y + rank * SQUARE_SIZE,
                              SQUARE_SIZE, SQUARE_SIZE), 3)

    # Highlight hint move
    if hint:
        from_sq = (chess.square_file(hint.from_square), 7 - chess.square_rank(hint.from_square))
        to_sq = (chess.square_file(hint.to_square), 7 - chess.square_rank(hint.to_square))
        pygame.draw.rect(screen, MOVE_COLOR,
                         (offset_x + from_sq[0] * SQUARE_SIZE, offset_y + from_sq[1] * SQUARE_SIZE,
                          SQUARE_SIZE, SQUARE_SIZE), 5)
        pygame.draw.rect(screen, MOVE_COLOR,
                         (offset_x + to_sq[0] * SQUARE_SIZE, offset_y + to_sq[1] * SQUARE_SIZE,
                          SQUARE_SIZE, SQUARE_SIZE), 5)

    # Display status
    font = pygame.font.SysFont("Arial", 20)
    status = font.render(status_text, True, (255, 255, 255))
    screen.blit(status, (10, offset_y + board_size + 10))

def get_valid_moves(board, sq):
    return [(chess.square_file(m.to_square), 7 - chess.square_rank(m.to_square)) for m in board.legal_moves if m.from_square == sq]

def menu(screen):
    font = pygame.font.SysFont("Arial", 36)
    screen.fill(BACKGROUND)
    menu_options = ["Chess AI Menu", "P: Play as Human (White)", "S: Self-Play Mode"]
    y_pos = 50
    for option in menu_options:
        text = font.render(option, True, (255, 255, 255))
        screen.blit(text, (50, y_pos))
        y_pos += 50
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.unicode.lower() == 'p':
                    return chess.WHITE, False
                if event.unicode.lower() == 's':
                    return None, True
        pygame.time.delay(100)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Chess AI")
    clock = pygame.time.Clock()

    # Initialize game state
    player_side, self_play = menu(screen)
    board = chess.Board()
    qtable1 = QTable('q1.pkl')
    ai1 = ChessAI(qtable1)
    qtable2 = QTable('q2.pkl') if self_play else None
    ai2 = ChessAI(qtable2) if self_play else None
    pieces = load_pieces()
    selected_square = None
    valid_moves = []
    hint_move = None
    last_search_tree = None
    move_history = []
    move_count = 0
    status = "Your move" if player_side == chess.WHITE else "AI is thinking..."

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                qtable1.save()
                if qtable2:
                    qtable2.save()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h and not self_play and board.turn == player_side:
                    hint_move, last_search_tree = ai1.compute_best_move(board)
                    status = f"Hint: {hint_move.uci() if hint_move else 'None'}"
                if event.key == pygame.K_v and last_search_tree:
                    visualize_tree(last_search_tree, board)
            elif event.type == pygame.MOUSEBUTTONDOWN and not self_play and board.turn == player_side:
                x, y = pygame.mouse.get_pos()
                board_size = SQUARE_SIZE * 8
                offset_x = (screen.get_width() - board_size) // 2
                offset_y = (screen.get_height() - board_size) // 2
                file = (x - offset_x) // SQUARE_SIZE
                rank = (y - offset_y) // SQUARE_SIZE
                if 0 <= file < 8 and 0 <= rank < 8:
                    square = chess.square(file, 7 - rank)
                    if selected_square is None:
                        piece = board.piece_at(square)
                        if piece and piece.color == player_side:
                            selected_square = (file, rank)
                            valid_moves = get_valid_moves(board, square)
                    else:
                        move = chess.Move(chess.square(selected_square[0], 7 - selected_square[1]), square)
                        if move in board.legal_moves:
                            board.push(move)
                            move_history.append((board.fen(), move.uci()))
                            selected_square = None
                            valid_moves = []
                            hint_move = None
                            status = "AI thinking..."
                            move_count += 1
                        else:
                            selected_square = None
                            valid_moves = []

        # AI move
        if not board.is_game_over():
            if self_play or (not self_play and board.turn != player_side):
                ai = ai1 if board.turn == chess.WHITE else (ai2 if self_play else ai1)
                move, last_search_tree = ai.compute_best_move(board)
                if move:
                    board.push(move)
                    move_history.append((board.fen(), move.uci()))
                    move_count += 1
                    hint_move = None
                    status = "Your move" if not self_play else "Self-play"

        if board.is_game_over():
            result = ai1.goal_test(board)
            reward = 1 if result == "Win" else -1 if result == "Loss" else 0
            for fen, move in move_history:
                qtable1.update(fen, move, reward)
                if qtable2:
                    qtable2.update(fen, move, -reward)
            qtable1.save()
            if qtable2:
                qtable2.save()
            board.reset()
            move_history.clear()
            move_count = 0
            status = "New game started."

        draw(screen, board, pieces, selected_square, valid_moves, hint_move, status)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Test cases
if __name__ == "__main__":
    main()
