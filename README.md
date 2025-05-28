# ♟️ CHESS AI: MASTERING MOVES WITH Q-LEARNING AND ALPHA-BETA PRUNING!

## 📖 About

Hi there! I’m **Alireza**, and welcome to my Chess AI project!
I built this for a university assignment—and honestly, it’s been a fun project. This AI uses **alpha-beta pruning** to pick moves quickly and **Q-learning** to get smarter over time.

You can:

* Play as **White**
* Or just kick back and watch **AI vs. AI**
* Visualize the AI’s decision tree by pressing `'V'`

It’s not perfect yet, but I’m super proud of what it can already do!

---

## ✨ Features

* 🎮 **Game Modes**
  Play as White or watch AI vs. AI in action.

* 🧠 **AI Intelligence**

  * Alpha-beta pruning with a 1-second move limit (a long story behind it!).
  * Learns from games using Q-learning and stores in a Q-table file.

* 🧾 **Board Evaluation**

  * Material (pawn=100, queen=900, etc.)
  * Center control (extra points for D4, D5, E4, E5)
  * *More scoring logic can be added!*

* 🖥️ **GUI(I had to! Long live the console.)**
  Powered by Pygame, featuring:

  * Piece movement
  * Help system (`H`)
  * Search tree visualization (`V`)

---

## 🛠️ How to Run

### Requirements

* Python 3.8+
* Libraries:

  ```bash
  pip install python-chess pygame networkx matplotlib
  ```
* **Chess piece images**: Keep the `pieces/` folder in the same directory as `gui.py`

### Setup

```bash
git clone https://github.com/SudoACoder/chess-ai.git
cd chess-ai
```

### Start the Game

```bash
python gui.py
```

### In-Game Controls

* `P`: Play as White
* `S`: Watch AI vs. AI
* `H`: Show a hint
* `V`: Visualize the search tree
* **Click to move** (when playing)

---

## 🔍 How It Works

### `logic.py`

Implements:

* Alpha-beta pruning to optimize move decisions
* Q-learning for long-term strategy improvement
* Evaluation based on material and board control

### `gui.py`

Handles:

* Board rendering with Pygame
* Player interaction
* AI feedback messages (e.g., "Your move", "AI thinking...")

---

## 🔮 Future Plans

This project was built for a university assignment, so I might not actively keep updating it, but that doesn't mean it has to stop here! If you’re into chess AI or just want to get your hands dirty with Python, feel free to fork it, play with it, and make it better. Some ideas:

* ♟️ **Improve the Evaluation Function**
  Add factors like king safety, pawn structure, and piece mobility for smarter move choices.

* ⚖️ **Fine-Tune Scoring Weights**
  Tweak how much material, center control, or mobility matters. (Is controlling E4 worth 20 or 30 points?)

* 🚀 **Optimize Q-Learning**

  * Speed up large-scale Q-table handling
  * Consider deep Q-learning or neural nets

* 🌐 **Online Play**
  Hook it up with a server to play others or run it as a bot!

* 🎓 **Teaching Mode**
  Let the AI explain why it chose a move, great for beginners learning chess.

---

> If any of these ideas excite you, **jump in and make a pull request**!
> I’d love to see where others can take this—even if I don’t actively maintain it.

---

## 🧩 Challenges

* Debugging alpha-beta logic—those bounds were tricky!
* Q-learning hyperparameters took ages to get *kinda* right (learning rate = 0.1)
* GUI alignment in Pygame = 🙃 but it works!

---

## 📷 Example Simple Situation, Tree visualization
![search_tree](https://github.com/user-attachments/assets/cb61aa3b-d604-4bd1-bdbe-b0c28e268164)
---

## 🙏 Thanks!

* Huge thanks to **python-chess** ❤️
* Online tutorials helped a ton with pruning and evaluation techniques

---

## 📄 License

**MIT License**
Use it, modify it, break it, improve it, just give me a little credit. :)
