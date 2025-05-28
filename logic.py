import chess
import time
import pickle
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

# Constants for configuration
MAX_DEPTH = 4  # Maximum depth(alpha-beta ) 4 is somehow a sweet spot for me but try 8,10,16 (carefully)
TIME_LIMIT = 1.0  # Time limit(iterative deepening)
QTABLE_MAX_SIZE = 10000  # Max size of Q-table
LEARNING_RATE = 0.1  # Default Learning rate(Q-learning), You can Play with it :)

class QTable:
    """Manages Q-learning table for storing move values."""
    def __init__(self, filename='qtable.pkl', max_size=QTABLE_MAX_SIZE):
        self.filename = filename
        self.max_size = max_size
        self.q = {}
        self._load_qtable()

    def _load_qtable(self):
        """Load Q-table from file, handle missing or corrupted files."""
        try:
            with open(self.filename, 'rb') as f:
                self.q = pickle.load(f)
            print(f"Loaded Q-table from {self.filename}")
        except FileNotFoundError:
            print(f"No Q-table found at {self.filename}, starting fresh.")
        except Exception as e:
            print(f"Error loading Q-table: {e}, initializing empty table.")

    def get_q(self, fen, move):
        return self.q.get(fen, {}).get(move, 0)

    def update(self, fen, move, reward, alpha=LEARNING_RATE):
        if fen not in self.q:
            self.q[fen] = {}
        old_q = self.q[fen].get(move, 0.0)
        self.q[fen][move] = old_q + alpha * (reward - old_q)

    def save(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.q, f)

    def get_average_q(self):
        if not self.q:
            return 0.0
        total = sum(sum(values.values()) for values in self.q.values())
        count = sum(len(values) for values in self.q.values())
        return total / count if count > 0 else 0.0

class ChessAI:
    """Chess AI using alpha-beta pruning and Q-learning for move evaluation."""
    def __init__(self, qtable, max_depth=MAX_DEPTH, time_limit=TIME_LIMIT):
        self.qtable = qtable
        self.max_depth = max_depth
        self.time_limit = time_limit

    def evaluate_board(self, board):
        """Evaluate board based on material and position(due to almost infinite possible chess outcomes to predict we do it in this way)"""
        
        # terminal states (when to kill it)
        if board.is_checkmate():
            return -10000 if board.turn == chess.WHITE else 10000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        # materials
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 350,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }
        score = 0
        for piece_type, value in piece_values.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        # center control(bonus)
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        for square in center_squares:
            piece = board.piece_at(square)
            if piece:
                score += 20 if piece.color == chess.WHITE else -20
        return score
        # todo: add king saftey, pawn structure and ... 

    def get_ordered_moves(self, board):
        """Sort moves by Q-table values for better pruning"""
        moves = list(board.legal_moves)
        fen = board.fen()
        return sorted(moves, key=lambda m: self.qtable.get_q(fen, m.uci()), reverse=True)

    def alpha_beta(self, board, depth, alpha, beta, maximizing):
        """alpha-beta pruning to evaluate board positions"""
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        moves = self.get_ordered_moves(board)
        if not moves:
            return self.evaluate_board(board)

        if maximizing:
            value = -float('inf')
            for move in moves:
                board.push(move)
                value = max(value, self.alpha_beta(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # beta cut off
            return value
        else:
            value = float('inf')
            for move in moves:
                board.push(move)
                value = min(value, self.alpha_beta(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if alpha >= beta:
                    break  # alpha cut off
            return value

    def iterative_deepening(self, board):
        """Find best move using iterative deepening within time limit!"""
        start_time = time.time()
        best_move = None
        best_value = -float('inf')
        search_tree = {}
        legal_moves = self.get_ordered_moves(board)
        if not legal_moves:
            #print("No legal moves found, returning None.")
            return None, None

        for depth in range(1, self.max_depth + 1):
            if time.time() - start_time > self.time_limit:
                #print(f"Time limit ({self.time_limit}s) reached at depth {depth}.")
                break
            alpha, beta = -float('inf'), float('inf')
            current_best = best_move
            current_value = -float('inf')
            search_tree[depth] = {}
            for move in legal_moves:
                board.push(move)
                value = self.alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                search_tree[depth][move.uci()] = value
                if value > current_value:
                    current_value = value
                    current_best = move
                alpha = max(alpha, value)
            if current_best:
                best_move = current_best
                best_value = current_value
        return best_move, search_tree

    def compute_best_move(self, board):
        """Compute best move and update Q-table with reward"""
        fen = board.fen()
        prev_score = self.evaluate_board(board)
        best_move, search_tree = self.iterative_deepening(board)
        if best_move:
            board.push(best_move)
            new_score = self.evaluate_board(board)
            reward = (new_score - prev_score) / 100.0
            self.qtable.update(fen, best_move.uci(), reward)
            board.pop()
            print(f"[{datetime.now()}] Move: {best_move.uci()}, Q-reward: {reward:.2f}")
        else:
            print("No best move found.")
        return best_move, search_tree

    def goal_test(self, board):
        """Check game outcome"""
        if board.is_checkmate():
            return "Win" if board.turn != chess.WHITE else "Loss"
        if board.is_stalemate() or board.is_insufficient_material():
            return "Draw"
        return "Ongoing"

def visualize_tree(search_tree, board):
    """Visualize the tree"""
    if not search_tree or not any(search_tree.values()):
        print("No search tree!")
        return

    G = nx.DiGraph()
    labels = {}
    node_colors = []
    node_id = 0

    G.add_node(0)
    labels[0] = "Root"
    node_colors.append("lightblue")

    for depth in sorted(search_tree.keys()):
        best_move, best_value = max(search_tree[depth].items(), key=lambda x: x[1], default=(None, -float('inf')))
        for move, value in search_tree[depth].items():
            curr_id = node_id + 1
            node_id += 1
            G.add_node(curr_id)
            labels[curr_id] = f"{move}\nScore: {value:.2f}"
            node_colors.append("red" if move == best_move else "lightblue")
            G.add_edge(0, curr_id)

    try:
        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, labels=labels, node_color=node_colors,
                node_size=1500, font_size=8, edge_color="gray", arrows=True)
        plt.title("Alpha-Beta Search Tree")
        plt.savefig('search_tree.png')
        plt.close()
        print("Search tree saved as 'search_tree.png'")
    except Exception as e:
        print(f"Error visualizing tree: {e}")
