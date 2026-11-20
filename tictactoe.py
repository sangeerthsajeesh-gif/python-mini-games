"""
Tic-Tac-Toe - a mini project using only Python's standard library (tkinter).

Features:
  - Two modes: 2 Players, or play against the computer
  - Winning line is highlighted
  - Scoreboard that survives between rounds
  - Buttons: New Round (keeps score) and Reset Score

Run:  python tictactoe.py
"""

import random
import tkinter as tk

# All 8 ways to win, as board positions 0-8:
#   0 | 1 | 2
#   3 | 4 | 5
#   6 | 7 | 8
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]

COLORS = {"X": "#d9534f", "O": "#2b7bb9"}
WIN_BG = "#b7e4a7"
NORMAL_BG = "#f4f4f4"


# -------------------------------------------------------------- game logic --
def find_winner(board):
    """Return (symbol, line) if someone has won, otherwise (None, None)."""
    for a, b, c in WIN_LINES:
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None


def computer_move(board, me="O", opponent="X"):
    """A simple (not unbeatable) computer player.

    Priority: 1) win if possible  2) block the opponent's win
              3) take the centre  4) take a random free square
    """
    free = [i for i, v in enumerate(board) if v == ""]

    # Try to win first, then try to block.
    for player in (me, opponent):
        for spot in free:
            test = board[:]
            test[spot] = player
            if find_winner(test)[0] == player:
                return spot

    if 4 in free:
        return 4
    return random.choice(free)


# --------------------------------------------------------------------- GUI --
class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.root.configure(bg="white")
        self.root.resizable(False, False)

        self.mode = tk.StringVar(value="2p")      # "2p" or "cpu"
        self.score = {"X": 0, "O": 0, "Draws": 0}
        self.buttons = []

        self._build_ui()
        self.new_round()

    # ---- building the interface ------------------------------------------
    def _build_ui(self):
        tk.Label(
            self.root, text="TIC-TAC-TOE", font=("Helvetica", 22, "bold"), bg="white"
        ).pack(pady=(12, 4))

        # Mode selection
        mode_frame = tk.Frame(self.root, bg="white")
        mode_frame.pack()
        for text, value in (("2 Players", "2p"), ("vs Computer", "cpu")):
            tk.Radiobutton(
                mode_frame,
                text=text,
                value=value,
                variable=self.mode,
                bg="white",
                font=("Helvetica", 11),
                command=self.on_mode_change,
            ).pack(side="left", padx=8)

        self.status = tk.Label(self.root, text="", font=("Helvetica", 13), bg="white", height=2)
        self.status.pack()

        # 3x3 board
        board_frame = tk.Frame(self.root, bg="white")
        board_frame.pack(padx=20)
        for i in range(9):
            btn = tk.Button(
                board_frame,
                text="",
                width=4,
                height=1,
                font=("Helvetica", 32, "bold"),
                bg=NORMAL_BG,
                activebackground="#e0e0e0",
                command=lambda idx=i: self.on_click(idx),
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.buttons.append(btn)

        # Scoreboard
        self.score_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg="white")
        self.score_label.pack(pady=(12, 4))

        controls = tk.Frame(self.root, bg="white")
        controls.pack(pady=(0, 14))
        tk.Button(controls, text="New Round", command=self.new_round).pack(side="left", padx=5)
        tk.Button(controls, text="Reset Score", command=self.reset_score).pack(side="left", padx=5)

    # ---- game flow ---------------------------------------------------------
    def new_round(self):
        self.board = [""] * 9
        self.turn = "X"
        self.game_over = False
        for btn in self.buttons:
            btn.config(text="", bg=NORMAL_BG, state="normal")
        self.update_status()
        self.update_score()

    def reset_score(self):
        self.score = {"X": 0, "O": 0, "Draws": 0}
        self.new_round()

    def on_mode_change(self):
        # Changing mode mid-game would be confusing, so start fresh.
        self.reset_score()

    def on_click(self, index):
        # Validation: ignore clicks on filled squares, or after the game ends,
        # or while it's the computer's turn.
        if self.game_over or self.board[index] != "":
            return
        if self.mode.get() == "cpu" and self.turn == "O":
            return

        self.place(index)

        # Computer replies after a short pause so it feels natural.
        if not self.game_over and self.mode.get() == "cpu" and self.turn == "O":
            self.root.after(400, self.computer_turn)

    def computer_turn(self):
        if self.game_over:
            return
        self.place(computer_move(self.board))

    def place(self, index):
        self.board[index] = self.turn
        self.buttons[index].config(text=self.turn, fg=COLORS[self.turn], disabledforeground=COLORS[self.turn])

        winner, line = find_winner(self.board)
        if winner:
            self.finish_round(winner, line)
        elif all(self.board):
            self.finish_round(None, None)
        else:
            self.turn = "O" if self.turn == "X" else "X"
            self.update_status()

    def finish_round(self, winner, line):
        self.game_over = True
        if winner:
            self.score[winner] += 1
            for i in line:
                self.buttons[i].config(bg=WIN_BG)
            self.status.config(text=f"{self.player_name(winner)} wins! 🎉", fg="#2e7d32")
        else:
            self.score["Draws"] += 1
            self.status.config(text="It's a draw!", fg="#555")
        self.update_score()

    # ---- text updates ------------------------------------------------------
    def player_name(self, symbol):
        if self.mode.get() == "cpu":
            return "You" if symbol == "X" else "Computer"
        return f"Player {symbol}"

    def update_status(self):
        self.status.config(text=f"{self.player_name(self.turn)}'s turn ({self.turn})", fg="#333")

    def update_score(self):
        s = self.score
        self.score_label.config(
            text=f"{self.player_name('X')} (X): {s['X']}   |   "
                 f"{self.player_name('O')} (O): {s['O']}   |   Draws: {s['Draws']}"
        )


def main():
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()


if __name__ == "__main__":
    main()
