"""
Wordle Clone - a mini project using only Python's standard library (tkinter).

How to play:
  - Guess the hidden 5-letter word in 6 tries.
  - Green  = right letter, right spot
  - Yellow = right letter, wrong spot
  - Gray   = letter not in the word
  - Type with your keyboard or click the on-screen keys.

Run:  python wordle.py
"""

import random
import tkinter as tk
from collections import Counter

# ---------------------------------------------------------------- word list --
# Add or remove words freely. Every word must be exactly 5 letters.
WORDS = """
about above actor adult after again agree alarm alive allow alone along among
angry apple apply arena argue arise armor aside asset avoid awake award aware
badly baker basic beach began begin being below bench black blame blank blind
block blood board brain brave bread break brick bring broad brown build burst
cabin candy carry catch cause chain chair chart cheap check chess chief child
claim class clean clear clock close cloud coach coast count court cover crane
crash cream crowd crown cycle daily dance death delay depth dirty doubt dozen
draft drama dream dress drink drive early earth eight elite empty enemy enjoy
enter equal error event every exact exist extra faith false fault fiber field
fifth fifty fight final first flame flash fleet floor focus force frame fresh
front fruit funny giant given glass globe glory grace grade grain grand grant
grass great green group guard guess guest guide happy heart heavy honey horse
hotel house human ideal image index inner input issue joint judge juice knife
known label large laser later laugh layer learn least leave legal lemon level
light limit local lucky lunch magic major maker march match maybe mayor media
metal might minor model money month moral motor mount mouse mouth movie music
never night noise north novel nurse ocean offer often onion order other outer
owner paint panel paper party peace phase phone photo piano pilot pitch place
plain plane plant plate point power press price pride prime print prize proof
proud queen quick quiet radio raise range rapid ratio reach ready right river
robot rough round route royal rural salad scale scene scope score sense serve
seven shade shape share sharp sheet shelf shift shine shirt shock shoot short
sight skill sleep slice small smart smile smoke solid solve sound south space
spare speak speed spend split sport staff stage stair stand start state steam
steel stick still stone store storm story strip study style sugar sunny super
sweet table taste teach thank theme thick thing think third three throw tight
title today topic total touch tough tower track trade train treat trend trial
tribe truck truly trust truth twice uncle under union unity until upper urban
usual valid value video virus visit vital voice waste watch water wheel where
which while white whole whose woman world worry worth would write wrong young
youth
""".split()

WORD_LENGTH = 5
MAX_ATTEMPTS = 6

# Sanity check so a typo in the list can't break the game.
WORDS = sorted({w.lower() for w in WORDS if len(w) == WORD_LENGTH and w.isalpha()})
VALID_GUESSES = set(WORDS)

# ------------------------------------------------------------------- colors --
COLORS = {
    "correct": "#6aaa64",   # green
    "present": "#c9b458",   # yellow
    "absent": "#787c7e",    # gray
    "empty": "#ffffff",
    "key": "#d3d6da",
}
BORDER_EMPTY = "#d3d6da"
BORDER_FILLED = "#878a8c"
STATE_PRIORITY = {"absent": 1, "present": 2, "correct": 3}


# -------------------------------------------------------------- game logic --
def evaluate_guess(guess: str, answer: str) -> list[str]:
    """Return a list of 'correct' / 'present' / 'absent' for each letter.

    Handles duplicate letters properly: a letter is only marked yellow as
    many times as it actually appears in the answer.
    """
    result = ["absent"] * len(guess)
    remaining = Counter()

    # Pass 1: greens, and count the answer letters that are still unmatched.
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = "correct"
        else:
            remaining[a] += 1

    # Pass 2: yellows, using up the unmatched letters.
    for i, g in enumerate(guess):
        if result[i] != "correct" and remaining[g] > 0:
            result[i] = "present"
            remaining[g] -= 1

    return result


# --------------------------------------------------------------------- GUI --
class WordleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Wordle Clone")
        self.root.configure(bg="white")
        self.root.resizable(False, False)

        self.tiles: list[list[tk.Label]] = []
        self.key_buttons: dict[str, tk.Button] = {}
        self.key_states: dict[str, str] = {}

        self._build_ui()
        self.root.bind("<Key>", self.on_physical_key)
        self.new_game()

    # ---- building the interface ------------------------------------------
    def _build_ui(self):
        tk.Label(
            self.root, text="WORDLE", font=("Helvetica", 26, "bold"), bg="white"
        ).pack(pady=(14, 4))

        self.message = tk.Label(
            self.root, text="", font=("Helvetica", 12), bg="white", fg="#333", height=2
        )
        self.message.pack()

        grid = tk.Frame(self.root, bg="white")
        grid.pack(padx=20, pady=6)
        for r in range(MAX_ATTEMPTS):
            row = []
            for c in range(WORD_LENGTH):
                tile = tk.Label(
                    grid,
                    text="",
                    width=3,
                    height=1,
                    font=("Helvetica", 24, "bold"),
                    bg=COLORS["empty"],
                    fg="black",
                    highlightthickness=2,
                    highlightbackground=BORDER_EMPTY,
                )
                tile.grid(row=r, column=c, padx=3, pady=3, ipady=4)
                row.append(tile)
            self.tiles.append(row)

        keyboard = tk.Frame(self.root, bg="white")
        keyboard.pack(pady=(10, 6))
        layout = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for r, letters in enumerate(layout):
            frame = tk.Frame(keyboard, bg="white")
            frame.pack(pady=2)
            if r == 2:
                self._make_key(frame, "ENTER", "ENTER", width=6)
            for ch in letters:
                self._make_key(frame, ch, ch.lower())
            if r == 2:
                self._make_key(frame, "⌫", "BACK", width=4)

        tk.Button(
            self.root,
            text="New Game",
            font=("Helvetica", 11, "bold"),
            command=self.new_game,
            takefocus=False,
        ).pack(pady=(4, 14))

    def _make_key(self, parent, label, value, width=3):
        btn = tk.Button(
            parent,
            text=label,
            width=width,
            font=("Helvetica", 11, "bold"),
            bg=COLORS["key"],
            relief="flat",
            takefocus=False,
            command=lambda v=value: self.handle_input(v),
        )
        btn.pack(side="left", padx=2)
        if len(value) == 1:
            self.key_buttons[value] = btn

    # ---- game state ------------------------------------------------------
    def new_game(self):
        self.answer = random.choice(WORDS)
        self.row = 0
        self.current = ""
        self.game_over = False
        self.key_states.clear()

        for row in self.tiles:
            for tile in row:
                tile.config(
                    text="",
                    bg=COLORS["empty"],
                    fg="black",
                    highlightbackground=BORDER_EMPTY,
                )
        for btn in self.key_buttons.values():
            btn.config(bg=COLORS["key"], fg="black")
        self.show_message("Guess the 5-letter word!")

    def show_message(self, text, color="#333"):
        self.message.config(text=text, fg=color)

    # ---- input handling --------------------------------------------------
    def on_physical_key(self, event):
        if event.keysym == "Return":
            self.handle_input("ENTER")
        elif event.keysym == "BackSpace":
            self.handle_input("BACK")
        elif len(event.char) == 1 and event.char.isascii() and event.char.isalpha():
            self.handle_input(event.char.lower())
        # Anything else (numbers, symbols, arrows...) is ignored on purpose.

    def handle_input(self, value: str):
        if self.game_over:
            return

        if value == "BACK":
            self.current = self.current[:-1]
        elif value == "ENTER":
            self.submit_guess()
            return
        elif len(self.current) < WORD_LENGTH:
            self.current += value

        self.refresh_current_row()

    def refresh_current_row(self):
        for c in range(WORD_LENGTH):
            tile = self.tiles[self.row][c]
            if c < len(self.current):
                tile.config(text=self.current[c].upper(), highlightbackground=BORDER_FILLED)
            else:
                tile.config(text="", highlightbackground=BORDER_EMPTY)

    def submit_guess(self):
        # ---- input validation ----
        if len(self.current) < WORD_LENGTH:
            self.show_message("Not enough letters.", "#b00020")
            return
        if self.current not in VALID_GUESSES:
            self.show_message(f"'{self.current.upper()}' is not in the word list.", "#b00020")
            return

        # ---- score the guess ----
        result = evaluate_guess(self.current, self.answer)
        for c, state in enumerate(result):
            tile = self.tiles[self.row][c]
            tile.config(bg=COLORS[state], fg="white", highlightbackground=COLORS[state])
            self.update_key(self.current[c], state)

        # ---- win / lose / continue ----
        if self.current == self.answer:
            self.game_over = True
            self.show_message(
                f"You got it in {self.row + 1}/{MAX_ATTEMPTS}! 🎉", "#2e7d32"
            )
            return

        self.row += 1
        self.current = ""
        if self.row == MAX_ATTEMPTS:
            self.game_over = True
            self.show_message(f"Out of tries! The word was {self.answer.upper()}.", "#b00020")
        else:
            self.show_message(f"Attempt {self.row + 1} of {MAX_ATTEMPTS}")

    def update_key(self, letter: str, state: str):
        """Colour the on-screen key, never downgrading (green stays green)."""
        old = self.key_states.get(letter)
        if old and STATE_PRIORITY[old] >= STATE_PRIORITY[state]:
            return
        self.key_states[letter] = state
        self.key_buttons[letter].config(bg=COLORS[state], fg="white")


def main():
    root = tk.Tk()
    WordleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
