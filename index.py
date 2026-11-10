"""
JARE OODAY - Ciyaar Soomaaliyeed (strategy, 2 ciyaaryahan)
Python 3 + tkinter (looma baahna xirmo dheeraad ah). Waxay ku habboon tahay mobile iyo kombiyuutar.

XEERARKA
1. 24 god. Dhagaxaan (12) vs Dhuxul (12). Dhagaxaan ayaa bilaabata ciyaarta kowaad.
2. Wejiga 1 (Dhigid): mid mid ayaa la dhigaa godad banaan.
3. JARE: marka 3 gabal oo isku xariiq ah la isugu geeyo, hal gabal cadowga ka mid ah ayaa la qaadaa.
   Gabal saddex-xariiqda ku jira waa la ilaaliyaa, ilaa kuwa kale oo dhan ay saddex-xariiq ku jiraan.
4. Wejiga 2 (Dhaqaaq): gabal waxaa loo dhaqaajiyaa god ku xiga oo banaan.
   IRMAAN: saddex-xariiq ayaa mar kasta dib loo furi karaa oo dib loo xidhi karaa; mar kasta
   oo saddex-xariiq la sameeyo, hal gabal ayaa la qaadaa.
   XEER CUSUB 3: gabal waxaa loo guuri karaa KALIYA god banaan oo ku xiga (xariiqda, dhexe
   ama koone). Haddii hal god banaan oo ku xiga gabal kasta oo ciyaaryahanku leeyahay aysan
   jirin, wuu xirmayaa (wuu dhacayaa) - uma boodi karo god kale (haddii uusan 3 gabal haysan).
5. DUULID: waa la tirtiray. Gabal kasta, xitaa marka 3 gabal u hadhaan, god banaan oo ku xiga
   oo kaliya ayuu u guuraa. (Beddel FLYING = True haddii aad dib u rabto.)
6. XEER CUSUB 1 - GODADKA OO BUUXA: haddii godadka oo dhan buuxsamaan (jare la'aan),
   ninka AAN bilaabin ayaa hal gabal qaadaa. Kadib ninka bilaabay ayaa hormuudaa.
7. XEER CUSUB 2 - CIYAARTA XIGTA: ciyaaryahanka guuleysta ayaa bilaaba ciyaarta xigta
   (haddii Dhuxul guuleysato, isagaa bilaabaya).
8. Ciyaaryahan 2 gabal u hadhay ama dhaqaaq waayay wuu dhacaa.
"""
import json
import os
import random
import tkinter as tk

FLYING = False           # duulidda waa damisan tahay: gabal had iyo jeer god ku xiga ayuu u guuraa
STONE, COAL = 0, 1
NAMES = ["Dhagaxaan", "Dhuxul"]
COLORS = ["#d9d9d9", "#1a1a1a"]
BG = "#fff8d6"

try:
    SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jare_save.json")
except NameError:
    SAVE_FILE = "jare_save.json"

# ------------------------------------------------------------ Xogta suuqa
POINTS = []
LINES = []
for r in range(3):
    a, b, c = r, 3, 6 - r
    LINES += [
        [(a, a), (b, a), (c, a)],
        [(a, c), (b, c), (c, c)],
        [(a, a), (a, b), (a, c)],
        [(c, a), (c, b), (c, c)],
    ]
    for p in [(a, a), (b, a), (c, a), (c, b), (c, c), (b, c), (a, c), (a, b)]:
        POINTS.append(p)
LINES += [
    [(3, 0), (3, 1), (3, 2)],
    [(3, 4), (3, 5), (3, 6)],
    [(0, 3), (1, 3), (2, 3)],
    [(4, 3), (5, 3), (6, 3)],
]
assert len(POINTS) == 24 and len(LINES) == 16


# NEIGHBORS[s] = godadka ku xiga s ee xariiqda (hal tallaabo, god dhexe ama koone)
NEIGHBORS = {p: set() for p in POINTS}
for ln in LINES:
    for i in range(len(ln) - 1):
        NEIGHBORS[ln[i]].add(ln[i + 1])
        NEIGHBORS[ln[i + 1]].add(ln[i])
MILLS_OF = {p: [ln for ln in LINES if p in ln] for p in POINTS}


# ------------------------------------------------------------ Ciyaarta
class Game:
    def __init__(self):
        self.reset()

    def reset(self, starter=STONE):
        self.starter = starter          # kan ciyaarta bilaabay
        self.turn = starter
        self.board = {p: None for p in POINTS}
        self.to_place = [12, 12]
        self.removing = False
        self.full_removal = False       # qaadista xeerka "godadka buuxa"
        self.selected = None
        self.over = False
        self.winner = None
        self.msg = ""

    # ---- keydin / soo celin
    def to_dict(self):
        return {
            "starter": self.starter, "turn": self.turn,
            "board": [[p[0], p[1], v] for p, v in self.board.items()],
            "to_place": self.to_place, "removing": self.removing,
            "full_removal": self.full_removal,
            "selected": list(self.selected) if self.selected else None,
            "over": self.over, "winner": self.winner, "msg": self.msg,
        }

    def from_dict(self, d):
        self.starter = d["starter"]
        self.turn = d["turn"]
        self.board = {p: None for p in POINTS}
        for x, y, v in d["board"]:
            self.board[(x, y)] = v
        self.to_place = list(d["to_place"])
        self.removing = d["removing"]
        self.full_removal = d["full_removal"]
        self.selected = tuple(d["selected"]) if d["selected"] else None
        self.over = d["over"]
        self.winner = d["winner"]
        self.msg = d["msg"]

    # ---- caawiyayaal
    def count(self, pl):
        return sum(1 for v in self.board.values() if v == pl)

    def total(self, pl):
        return self.count(pl) + self.to_place[pl]

    def forms_mill(self, pos, pl, board=None):
        b = board or self.board
        return any(all(b[q] == pl for q in ln) for ln in MILLS_OF[pos])

    def in_mill(self, pos):
        pl = self.board[pos]
        return pl is not None and self.forms_mill(pos, pl)

    def removable(self, victim):
        mine = [p for p, v in self.board.items() if v == victim]
        free = [p for p in mine if not self.in_mill(p)]
        return free if free else mine

    def can_fly(self, pl):
        return FLYING and self.to_place[pl] == 0 and self.count(pl) == 3

    def destinations(self, src):
        if self.can_fly(self.turn):
            return [p for p, v in self.board.items() if v is None]
        return [p for p in NEIGHBORS[src] if self.board[p] is None]

    def has_moves(self, pl):
        if self.to_place[pl] > 0:
            return any(v is None for v in self.board.values())
        if self.can_fly(pl):
            return any(x is None for x in self.board.values())
        # xirmay = hal god banaan oo ku xiga gabal kasta oo uu leeyahay ma jiro
        return any(v == pl and any(self.board[n] is None for n in NEIGHBORS[p])
                   for p, v in self.board.items())

    # ---- dhaqdhaqaaqyada
    def place(self, pos):
        self.board[pos] = self.turn
        self.to_place[self.turn] -= 1
        self._after_action(pos)

    def move(self, src, dst):
        self.board[src] = None
        self.board[dst] = self.turn
        self.selected = None
        self._after_action(dst)

    def _after_action(self, pos):
        if self.forms_mill(pos, self.turn):
            if any(v == 1 - self.turn for v in self.board.values()):
                self.removing = True
                self.msg = "JARE! Dooro gabal cadow ah."
                return
        self.end_turn()

    def remove(self, pos):
        self.board[pos] = None
        self.removing = False
        self.full_removal = False
        self.end_turn()

    def end_turn(self):
        self.turn = 1 - self.turn
        self.msg = f"Hawsha: {NAMES[self.turn]}"
        for pl in (STONE, COAL):
            if self.total(pl) < 3:
                self.over, self.winner = True, 1 - pl
                self.msg = f"{NAMES[1 - pl]} ayaa guuleystay! ({NAMES[pl]}: 2 gabal)"
                return
        # XEER 6: godadka oo dhan buuxa -> ninka aan bilaabin hal gabal ayuu qaadaa
        if all(v is not None for v in self.board.values()):
            self.turn = 1 - self.starter
            self.removing = True
            self.full_removal = True
            self.msg = f"Godadku waa buuxaan! {NAMES[self.turn]}, hal gabal qaad."
            return
        if not self.has_moves(self.turn):
            self.over, self.winner = True, 1 - self.turn
            self.msg = f"{NAMES[1 - self.turn]} ayaa guuleystay! ({NAMES[self.turn]} wuu xirmay)"


# ------------------------------------------------------------ AI fudud
def ai_choose_removal(g):
    opts = g.removable(1 - g.turn)
    foe = 1 - g.turn

    def threat(p):
        s = 0
        for ln in MILLS_OF[p]:
            vals = [g.board[q] for q in ln]
            if vals.count(foe) == 2 and vals.count(None) == 1:
                s += 3
            elif vals.count(foe) >= 2:
                s += 1
        return s + random.random()
    return max(opts, key=threat)


def ai_choose_action(g):
    me, foe = g.turn, 1 - g.turn
    actions = []
    if g.to_place[me] > 0:
        for p, v in g.board.items():
            if v is None:
                actions.append(("place", None, p))
    else:
        for s, v in g.board.items():
            if v == me:
                g.selected = s
                for d in g.destinations(s):
                    actions.append(("move", s, d))
        g.selected = None

    def score(a):
        _, s, d = a
        b = dict(g.board)
        if s:
            b[s] = None
        b[d] = me
        sc = random.random()
        if g.forms_mill(d, me, b):
            sc += 10                     # samee jare
        b2 = dict(g.board)
        b2[d] = foe
        if g.board[d] is None and g.forms_mill(d, foe, b2):
            sc += 6                      # xir jarada cadowga
        sc += len(NEIGHBORS[d]) * 0.3    # god xidhiidh badan
        return sc
    return max(actions, key=score)


# ------------------------------------------------------------ UI (mobile-friendly)
class App:
    def __init__(self, root):
        self.root = root
        root.title("Jare Ooday")
        root.configure(bg=BG)

        # cabbirka suuqa waxaa laga qaadaa shaashadda (mobile ama kombiyuutar)
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        side = max(280, min(sw - 20, int(sh * 0.62), 700))
        self.CELL = side // 7
        self.OFF = self.CELL // 2
        self.SIDE = self.CELL * 7
        u = self.CELL

        def font(k, bold=False):          # cabbir pixel ah (negative) = isku mid mobile & PC
            n = -max(10, int(u * k))
            return ("Helvetica", n, "bold") if bold else ("Helvetica", n)

        self.g = Game()
        self.vs_cpu = tk.BooleanVar(value=False)
        self.next_starter = STONE
        self.recorded = False

        # ================= SHAASHADDA HORE (menu) =================
        self.menu = tk.Frame(root, bg=BG)
        tk.Label(self.menu, text="JARE OODAY", font=font(0.6, True),
                 bg=BG, fg="#333").pack(pady=(int(u * 0.8), int(u * 0.2)))
        tk.Label(self.menu, text="Ciyaar Soomaaliyeed", font=font(0.25),
                 bg=BG, fg="#555").pack(pady=(0, int(u * 0.6)))
        bw = max(14, int(self.SIDE / (u * 0.2 * 1.0) / 6))
        self.btn_play = tk.Button(self.menu, text="Play Game", font=font(0.3, True),
                                  width=14, command=self.start_new)
        self.btn_play.pack(pady=int(u * 0.15), ipady=int(u * 0.1))
        self.btn_continue = tk.Button(self.menu, text="Sii Wad Ciyaarta", font=font(0.3, True),
                                      width=14, command=self.continue_game)
        self.btn_continue.pack(pady=int(u * 0.15), ipady=int(u * 0.1))

        # ================= SHAASHADDA CIYAARTA =================
        self.gf = tk.Frame(root, bg=BG)
        tk.Label(self.gf, text="JARE OODAY", font=font(0.36, True), bg=BG, fg="#333").pack(pady=(6, 0))
        self.status = tk.Label(self.gf, text="", font=font(0.23), bg=BG, fg="#222",
                               wraplength=self.SIDE, justify="center", height=3)
        self.status.pack()
        self.info = tk.Label(self.gf, text="", font=font(0.18), bg=BG, fg="#555",
                             wraplength=self.SIDE, justify="center", height=3)
        self.info.pack()

        self.cv = tk.Canvas(self.gf, width=self.SIDE, height=self.SIDE, bg="#ffffcc",
                            highlightthickness=0)
        self.cv.pack(padx=6, pady=4)
        self.cv.bind("<Button-1>", self.on_click)

        bar = tk.Frame(self.gf, bg=BG)
        bar.pack(pady=(2, 8))
        tk.Button(bar, text="Ciyaar Cusub", font=font(0.21), command=self.new_game
                  ).pack(side="left", padx=4)
        tk.Checkbutton(bar, text="Kombiyuutar (Dhuxul)", font=font(0.21), variable=self.vs_cpu,
                       bg=BG, activebackground=BG, command=self.new_game
                       ).pack(side="left", padx=4)
        tk.Button(bar, text="Menu", font=font(0.21), command=self.show_menu
                  ).pack(side="left", padx=4)

        self.show_menu()

    # ---- shaashadaha
    def show_menu(self):
        self.gf.pack_forget()
        self.menu.pack(fill="both", expand=True)
        has_save = self.load_data() is not None
        self.btn_continue.config(state="normal" if has_save else "disabled")

    def show_game(self):
        self.menu.pack_forget()
        self.gf.pack()

    def start_new(self):
        self.show_game()
        self.new_game()

    def continue_game(self):
        data = self.load_data()
        if data is None:
            return
        self.g.from_dict(data["game"])
        self.vs_cpu.set(data.get("vs_cpu", False))
        self.next_starter = data.get("next_starter", STONE)
        self.recorded = False
        self.show_game()
        self.draw()
        self.maybe_ai()

    # ---- keydin
    def save_data(self):
        try:
            if self.g.over:
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                return
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({"game": self.g.to_dict(), "vs_cpu": self.vs_cpu.get(),
                           "next_starter": self.next_starter}, f)
        except OSError:
            pass

    def load_data(self):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data["game"].get("over"):
                return None
            return data
        except (OSError, ValueError, KeyError):
            return None

    def xy(self, p):
        return self.OFF + p[0] * self.CELL, self.OFF + p[1] * self.CELL

    def new_game(self):
        self.g.reset(self.next_starter)     # XEER 7: guuleystaha ayaa bilaabaya
        self.recorded = False
        self.g.msg = f"{NAMES[self.next_starter]} ayaa bilaabaya. Dhig gabal."
        self.draw()
        self.maybe_ai()

    def on_click(self, ev):
        g = self.g
        if g.over or (self.vs_cpu.get() and g.turn == COAL):
            return
        r = self.CELL * 0.32
        for p in POINTS:
            x, y = self.xy(p)
            if (ev.x - x) ** 2 + (ev.y - y) ** 2 <= r * r:
                self.handle(p)
                return

    def handle(self, pos):
        g = self.g
        me, foe = g.turn, 1 - g.turn
        if g.removing:
            if g.board[pos] == foe and pos in g.removable(foe):
                g.remove(pos)
            else:
                g.msg = "Gabalkaas lama qaadi karo. Dooro mid kale."
        elif g.to_place[me] > 0:
            if g.board[pos] is None:
                g.place(pos)
        else:
            if g.board[pos] == me:
                g.selected = pos
            elif g.selected and g.board[pos] is None:
                if pos in g.destinations(g.selected):
                    g.move(g.selected, pos)
                else:
                    g.msg = "Halkaas ma tegi kartid. Hal god oo ku xiga oo banaan kaliya."
        self.draw()
        self.maybe_ai()

    def maybe_ai(self):
        if self.vs_cpu.get() and not self.g.over and self.g.turn == COAL:
            self.root.after(700, self.ai_play)

    def ai_play(self):
        g = self.g
        if g.over or g.turn != COAL or not self.vs_cpu.get():
            return
        if not self.gf.winfo_ismapped():      # haddii menu-ga la joogo, ha ciyaarin
            return
        if g.removing:
            g.remove(ai_choose_removal(g))
        else:
            kind, s, d = ai_choose_action(g)
            if kind == "place":
                g.place(d)
            else:
                g.selected = s
                g.move(s, d)
        self.draw()
        if g.removing and g.turn == COAL:      # jare cusub ama xeerka godadka buuxa
            self.root.after(600, self.ai_play)
        else:
            self.maybe_ai()

    def check_over(self):
        g = self.g
        if g.over and not self.recorded:
            self.recorded = True
            if g.winner in (STONE, COAL):
                self.next_starter = g.winner
                g.msg += f"\nXigta: {NAMES[g.winner]} bilaabaa."

    # ---- sawirka
    def draw(self):
        self.check_over()
        g, cv, u = self.g, self.cv, self.CELL
        cv.delete("all")
        lw = max(4, int(u * 0.08))
        r_dot, r_pc = int(u * 0.11), int(u * 0.27)
        r_hint, r_ring, r_mill = int(u * 0.21), int(u * 0.33), int(u * 0.08)
        ring_w = max(3, int(u * 0.04))

        for ln in LINES:
            x1, y1 = self.xy(ln[0])
            x2, y2 = self.xy(ln[-1])
            cv.create_line(x1, y1, x2, y2, width=lw, fill="#333", capstyle="round")

        hints = set()
        if g.selected and not g.removing:
            hints = set(g.destinations(g.selected))
        rem = set(g.removable(1 - g.turn)) if g.removing else set()

        for p in POINTS:
            x, y = self.xy(p)
            v = g.board[p]
            if v is None:
                cv.create_oval(x - r_dot, y - r_dot, x + r_dot, y + r_dot,
                               fill="#333", outline="#333")
                if p in hints:
                    cv.create_oval(x - r_hint, y - r_hint, x + r_hint, y + r_hint,
                                   outline="#2e9e3e", width=ring_w)
            else:
                cv.create_oval(x - r_pc, y - r_pc, x + r_pc, y + r_pc, fill=COLORS[v],
                               outline="#777" if v == STONE else "#000", width=3)
                if g.in_mill(p):
                    cv.create_oval(x - r_mill, y - r_mill, x + r_mill, y + r_mill,
                                   fill="#e8b400" if v == COAL else "#8a6d00", outline="")
                if p == g.selected:
                    cv.create_oval(x - r_ring, y - r_ring, x + r_ring, y + r_ring,
                                   outline="#1e5bff", width=ring_w)
                if p in rem and v == 1 - g.turn:
                    cv.create_oval(x - r_ring, y - r_ring, x + r_ring, y + r_ring,
                                   outline="#e02020", width=ring_w)

        self.status.config(text=g.msg)
        if g.over:
            phase = "Ciyaarta waa dhammaatay"
        else:
            phase = "Wejiga 1: Dhigid" if g.to_place[g.turn] > 0 else "Wejiga 2: Dhaqaaq"
            if g.can_fly(g.turn):
                phase += " (Duulid)"
        self.info.config(text=(
            f"{phase}\n"
            f"Dhagaxaan: {g.count(0)} Shaxda, {g.to_place[0]} gacanta\n"
            f"Dhuxul: {g.count(1)} Shaxda, {g.to_place[1]} gacanta"))
        self.save_data()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()