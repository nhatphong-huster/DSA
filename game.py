import pygame
import sys
import random
import time
import copy

# ─── Constants ───────────────────────────────────────────────────────────────
W, H = 720, 820
BOARD_X, BOARD_Y = 30, 140
CELL = 62
GRID = CELL * 9        # 558
FPS = 60

# Palette
BG          = (245, 245, 250)
WHITE       = (255, 255, 255)
BLACK       = (20,  20,  30)
GRAY_LIGHT  = (210, 210, 220)
GRAY_MID    = (160, 160, 175)
GRAY_DARK   = (100, 100, 115)

BLUE_DARK   = ( 30,  80, 200)
BLUE_MED    = ( 60, 120, 240)
BLUE_LIGHT  = (200, 215, 255)
BLUE_PALE   = (230, 238, 255)

RED         = (220,  50,  50)
RED_LIGHT   = (255, 200, 200)
GREEN       = ( 34, 160,  80)
GREEN_LIGHT = (190, 240, 210)
ORANGE      = (240, 130,  20)
PURPLE      = (130,  60, 200)
GOLD        = (220, 170,   0)

BOX_LINE    = ( 50,  50,  80)
THIN_LINE   = (180, 180, 200)

# ─── Puzzle generation / solving ─────────────────────────────────────────────
BASE_PUZZLES = [
    # puzzle, solution  (flatten -> list of 81)
    (
        "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
        "534678912672195348198342567859761423426853791713924856961537284287419635345286179",
    ),
    (
        "003020600900305001001806400008102900700000008006708200002609500800203009005010300",
        "483921657967345821251876493548132976729564138136798245372689514814253769695417382",
    ),
    (
        "200080300060070084030500209000105408000000000402706000301007040720040060004010003",
        "214986375963271584837594219579135468186347921452768137391827046728453691645619823",
    ),
    (
        "000000907000420180000705026100904000050000040000507009920108000034059000507000000",
        "612843957753429186489715326167934572258671493394287619926158743834562917571396248",
    ),
    (
        "000006000059000008200008000045000000003000600000003054000325006000000031000900080",
        "431796285659132748287548319145869273893217654726483951914325867568974132372651489",
    ),
]

def str_to_board(s):
    return [[int(s[r*9+c]) for c in range(9)] for r in range(9)]

def board_to_str(b):
    return "".join(str(b[r][c]) for r in range(9) for c in range(9))

def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    br, bc = (row//3)*3, (col//3)*3
    for r in range(br, br+3):
        for c in range(bc, bc+3):
            if board[r][c] == num:
                return False
    return True

def solve_backtrack(board, steps=None):
    """Returns True/False; mutates board in place. Optionally collects steps."""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1,10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if steps is not None:
                            steps.append((r, c, num))
                        if solve_backtrack(board, steps):
                            return True
                        board[r][c] = 0
                        if steps is not None:
                            steps.append((r, c, 0))
                return False
    return True

def generate_puzzle(difficulty="medium"):
    # Start from a known puzzle for reliability
    idx = random.randrange(len(BASE_PUZZLES))
    puzzle_str, sol_str = BASE_PUZZLES[idx]
    puzzle = str_to_board(puzzle_str)
    solution = str_to_board(sol_str)
    # Rotate/reflect randomly for variety
    op = random.randint(0, 3)
    if op == 1:
        puzzle   = [row[::-1] for row in puzzle]
        solution = [row[::-1] for row in solution]
    elif op == 2:
        puzzle   = puzzle[::-1]
        solution = solution[::-1]
    elif op == 3:
        puzzle   = [list(col) for col in zip(*puzzle)]
        solution = [list(col) for col in zip(*solution)]
    return puzzle, solution

# ─── Button helper ────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, color, text_color=WHITE, radius=10, font=None):
        self.rect       = pygame.Rect(rect)
        self.label      = label
        self.color      = color
        self.hover_col  = tuple(min(255,v+30) for v in color)
        self.text_color = text_color
        self.radius     = radius
        self.font       = font
        self.hovered    = False

    def draw(self, surf, font):
        f = self.font or font
        col = self.hover_col if self.hovered else self.color
        pygame.draw.rect(surf, col, self.rect, border_radius=self.radius)
        pygame.draw.rect(surf, WHITE, self.rect, 1, border_radius=self.radius)
        txt = f.render(self.label, True, self.text_color)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# ─── Main game ────────────────────────────────────────────────────────────────
class SudokuGame:
    MAX_ERRORS = 3

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Sudoku")
        self.clock  = pygame.time.Clock()

        self.font_xl  = pygame.font.SysFont("segoeui", 46, bold=True)
        self.font_lg  = pygame.font.SysFont("segoeui", 30, bold=True)
        self.font_md  = pygame.font.SysFont("segoeui", 22)
        self.font_sm  = pygame.font.SysFont("segoeui", 17)
        self.font_num = pygame.font.SysFont("segoeui", 34, bold=True)
        self.font_dft = pygame.font.SysFont("segoeui", 16)

        self.state = "menu"   # menu | playing | won | lost | solving
        self._build_menu()
        self.new_game("medium")

    # ── Layout helpers ────────────────────────────────────────────────────────
    def cell_rect(self, r, c):
        x = BOARD_X + c*CELL
        y = BOARD_Y + r*CELL
        return pygame.Rect(x, y, CELL, CELL)

    def pos_to_cell(self, mx, my):
        c = (mx - BOARD_X) // CELL
        r = (my - BOARD_Y) // CELL
        if 0 <= r < 9 and 0 <= c < 9:
            return r, c
        return None, None

    # ── Build UI buttons ──────────────────────────────────────────────────────
    def _build_menu(self):
        self.menu_btns = [
            Button((W//2-110, 280, 220, 52), "Easy",   GREEN,  radius=12),
            Button((W//2-110, 350, 220, 52), "Medium", BLUE_MED, radius=12),
            Button((W//2-110, 420, 220, 52), "Hard",   ORANGE, radius=12),
        ]

    def _build_game_buttons(self):
        bx = BOARD_X
        by = BOARD_Y + GRID + 16
        bw, bh = 100, 40
        gap = 12
        self.btn_new     = Button((bx,            by, bw, bh), "New Game",  BLUE_MED,  radius=8)
        self.btn_draft   = Button((bx+bw+gap,      by, bw, bh), "Draft: ON" if self.draft_mode else "Draft: OFF",
                                   PURPLE if self.draft_mode else GRAY_MID, radius=8)
        self.btn_solve   = Button((bx+2*(bw+gap),  by, bw, bh), "Auto Solve", ORANGE,  radius=8)
        self.btn_limit   = Button((bx+3*(bw+gap),  by, bw+20, bh),
                                   f"Limit: {'ON' if self.error_limit else 'OFF'}",
                                   RED if self.error_limit else GRAY_MID, radius=8)
        self.btn_menu    = Button((bx,            by+52, 80, 36), "← Menu", GRAY_DARK, radius=8)
        self.btn_hint    = Button((bx+96,         by+52, 80, 36), "Hint",   GOLD,      radius=8, font=self.font_sm)

        self.numpad_btns = []
        nx_start = BOARD_X
        ny = BOARD_Y + GRID + 16 + 52 + 16 + 36 + 12
        nw = nh = 50
        ng = 8
        for i in range(1, 10):
            nx = nx_start + (i-1)*(nw+ng)
            self.numpad_btns.append(Button((nx, ny, nw, nh), str(i), BLUE_DARK, radius=6))
        self.btn_erase = Button((nx_start+9*(nw+ng)-ng, ny, nw+16, nh), "⌫", GRAY_DARK, radius=6)
        self.numpad_y  = ny

    # ── New game ──────────────────────────────────────────────────────────────
    def new_game(self, difficulty="medium"):
        self.difficulty  = difficulty
        self.puzzle, self.solution = generate_puzzle(difficulty)
        self.board       = copy.deepcopy(self.puzzle)
        self.given       = [[self.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
        self.drafts      = [[set() for _ in range(9)] for _ in range(9)]
        self.selected    = None
        self.errors      = 0
        self.error_cells = set()   # (r,c) currently showing wrong value
        self.draft_mode  = False
        self.error_limit = True
        self.solved      = False
        self.start_time  = time.time()
        self.elapsed     = 0
        self.hints_used  = 0
        self.anim_solve  = False
        self.solve_steps = []
        self.solve_idx   = 0
        self.solve_board = None
        self.flash       = {}      # (r,c) -> (color, end_time)
        self._build_game_buttons()

    # ── Event loop ────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.handle_event(event)
            self.update()
            self.draw()
            pygame.display.flip()

    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()
        if self.state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in self.menu_btns:
                    if btn.clicked((mx,my)):
                        diff = btn.label.lower()
                        self.new_game(diff)
                        self.state = "playing"
        elif self.state in ("playing", "solving"):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(mx, my)
            if event.type == pygame.KEYDOWN and self.state == "playing":
                self._handle_key(event)

    def _handle_click(self, mx, my):
        # cell click
        r, c = self.pos_to_cell(mx, my)
        if r is not None:
            self.selected = (r, c)
            return

        if self.state != "playing":
            return

        # buttons
        if self.btn_new.clicked((mx,my)):
            self.state = "menu"; return
        if self.btn_draft.clicked((mx,my)):
            self.draft_mode = not self.draft_mode
            self.btn_draft.label = "Draft: ON" if self.draft_mode else "Draft: OFF"
            self.btn_draft.color = PURPLE if self.draft_mode else GRAY_MID
            return
        if self.btn_solve.clicked((mx,my)):
            self._start_auto_solve(); return
        if self.btn_limit.clicked((mx,my)):
            self.error_limit = not self.error_limit
            self.btn_limit.label = f"Limit: {'ON' if self.error_limit else 'OFF'}"
            self.btn_limit.color = RED if self.error_limit else GRAY_MID
            return
        if self.btn_menu.clicked((mx,my)):
            self.state = "menu"; return
        if self.btn_hint.clicked((mx,my)):
            self._give_hint(); return

        for btn in self.numpad_btns:
            if btn.clicked((mx,my)):
                self._place_num(int(btn.label)); return
        if self.btn_erase.clicked((mx,my)):
            self._erase(); return

    def _handle_key(self, event):
        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            if self.selected is None:
                self.selected = (0,0); return
            r, c = self.selected
            if event.key == pygame.K_UP:    r = max(0,r-1)
            if event.key == pygame.K_DOWN:  r = min(8,r+1)
            if event.key == pygame.K_LEFT:  c = max(0,c-1)
            if event.key == pygame.K_RIGHT: c = min(8,c+1)
            self.selected = (r,c)
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            self._erase()
        elif event.unicode.isdigit() and event.unicode != '0':
            self._place_num(int(event.unicode))

    # ── Game logic ────────────────────────────────────────────────────────────
    def _place_num(self, num):
        if self.selected is None: return
        r, c = self.selected
        if self.given[r][c]: return

        if self.draft_mode:
            if num in self.drafts[r][c]:
                self.drafts[r][c].remove(num)
            else:
                self.drafts[r][c].add(num)
            return

        # normal placement
        correct = self.solution[r][c]
        if num == self.board[r][c]:
            return  # same number, ignore

        if self.error_limit:
            if num != correct:
                self.errors += 1
                self.board[r][c] = num
                self.error_cells.add((r,c))
                self._flash(r, c, RED_LIGHT)
                if self.errors >= self.MAX_ERRORS:
                    self.state = "lost"
                return
            else:
                self.error_cells.discard((r,c))
                self.board[r][c] = num
                self.drafts[r][c].clear()
                self._clear_related_drafts(r, c, num)
                self._flash(r, c, GREEN_LIGHT)
        else:
            # no enforcement: accept anything
            prev = self.board[r][c]
            self.board[r][c] = num
            self.drafts[r][c].clear()
            if num != correct:
                self.error_cells.add((r,c))
                self._flash(r, c, RED_LIGHT)
            else:
                self.error_cells.discard((r,c))
                self._flash(r, c, GREEN_LIGHT)
                self._clear_related_drafts(r, c, num)

        self._check_win()

    def _clear_related_drafts(self, r, c, num):
        br, bc = (r//3)*3, (c//3)*3
        for i in range(9):
            self.drafts[r][i].discard(num)
            self.drafts[i][c].discard(num)
        for dr in range(br, br+3):
            for dc in range(bc, bc+3):
                self.drafts[dr][dc].discard(num)

    def _erase(self):
        if self.selected is None: return
        r, c = self.selected
        if self.given[r][c]: return
        self.board[r][c] = 0
        self.drafts[r][c].clear()
        self.error_cells.discard((r,c))

    def _give_hint(self):
        empties = [(r,c) for r in range(9) for c in range(9)
                   if not self.given[r][c] and self.board[r][c]==0]
        if not empties: return
        r, c = random.choice(empties)
        self.board[r][c] = self.solution[r][c]
        self.given[r][c] = True
        self.hints_used += 1
        self.error_cells.discard((r,c))
        self.drafts[r][c].clear()
        self._clear_related_drafts(r, c, self.solution[r][c])
        self._flash(r, c, GREEN_LIGHT)
        self._check_win()

    def _check_win(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != self.solution[r][c]:
                    return
        self.solved = True
        self.state  = "won"
        self.elapsed = time.time() - self.start_time

    def _flash(self, r, c, color, duration=0.5):
        self.flash[(r,c)] = (color, time.time()+duration)

    # ── Auto solver ───────────────────────────────────────────────────────────
    def _start_auto_solve(self):
        self.anim_solve  = True
        self.solve_board = copy.deepcopy(self.solution)  # show solution directly step by step
        self.solve_steps = []
        # replay the backtracking visually from current board state
        temp = copy.deepcopy(self.board)
        # fill givens and player-correct cells
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != 0 and self.board[r][c] == self.solution[r][c]:
                    temp[r][c] = self.solution[r][c]
                else:
                    temp[r][c] = self.puzzle[r][c]
        solve_backtrack(temp, self.solve_steps)
        self.solve_idx    = 0
        self.last_step_t  = time.time()
        self.step_delay   = 0.025   # seconds between steps
        self.state        = "solving"
        # show current clean puzzle
        for r in range(9):
            for c in range(9):
                self.board[r][c] = self.puzzle[r][c]
        self.error_cells.clear()
        self.drafts = [[set() for _ in range(9)] for _ in range(9)]

    def _step_solve(self):
        now = time.time()
        while self.solve_idx < len(self.solve_steps) and now - self.last_step_t >= self.step_delay:
            r, c, v = self.solve_steps[self.solve_idx]
            if not self.given[r][c]:
                self.board[r][c] = v
                if v != 0:
                    self._flash(r, c, BLUE_LIGHT, 0.2)
            self.solve_idx  += 1
            self.last_step_t = now
        if self.solve_idx >= len(self.solve_steps):
            self.anim_solve = False
            self.state      = "won"
            self.elapsed    = time.time() - self.start_time

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self):
        mx, my = pygame.mouse.get_pos()
        if self.state == "menu":
            for btn in self.menu_btns:
                btn.update((mx,my))
        elif self.state in ("playing","solving","won","lost"):
            if self.state == "playing":
                for b in [self.btn_new, self.btn_draft, self.btn_solve,
                          self.btn_limit, self.btn_menu, self.btn_hint]+self.numpad_btns+[self.btn_erase]:
                    b.update((mx,my))
            if self.state == "solving":
                self._step_solve()
            if self.state == "playing" and not self.solved:
                self.elapsed = time.time() - self.start_time
            # expire flashes
            now = time.time()
            self.flash = {k:v for k,v in self.flash.items() if v[1]>now}

    # ── Drawing ───────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)
        if self.state == "menu":
            self._draw_menu()
        else:
            self._draw_header()
            self._draw_board()
            self._draw_ui_buttons()
            if self.state == "won":
                self._draw_overlay("🎉 Puzzle Solved!", GREEN,
                    f"Time: {self._fmt_time(self.elapsed)}  |  Hints: {self.hints_used}  |  Errors: {self.errors}")
            elif self.state == "lost":
                self._draw_overlay("💀 Game Over", RED, f"You made {self.MAX_ERRORS} errors!")

    # ── Menu screen ───────────────────────────────────────────────────────────
    def _draw_menu(self):
        # Title
        t = self.font_xl.render("SUDOKU", True, BLUE_DARK)
        self.screen.blit(t, t.get_rect(centerx=W//2, y=130))
        sub = self.font_md.render("Select difficulty to start", True, GRAY_DARK)
        self.screen.blit(sub, sub.get_rect(centerx=W//2, y=210))
        # Info cards
        info = [
            ("Easy",   GREEN,    "Perfect for beginners"),
            ("Medium", BLUE_MED, "A balanced challenge"),
            ("Hard",   ORANGE,   "For seasoned players"),
        ]
        for i, (label, col, desc) in enumerate(info):
            btn = self.menu_btns[i]
            btn.draw(self.screen, self.font_md)
            d = self.font_sm.render(desc, True, GRAY_DARK)
            self.screen.blit(d, d.get_rect(centerx=W//2, y=btn.rect.bottom+4))

        # Footer instructions
        lines = [
            "Arrow keys / Click  ·  navigate cells",
            "1-9 keys / numpad   ·  place numbers",
            "Draft mode          ·  pencil candidates",
            "Auto Solve          ·  watch backtracking",
        ]
        for i, line in enumerate(lines):
            t = self.font_sm.render(line, True, GRAY_MID)
            self.screen.blit(t, t.get_rect(centerx=W//2, y=530+i*24))

    # ── Header bar ────────────────────────────────────────────────────────────
    def _draw_header(self):
        pygame.draw.rect(self.screen, BLUE_DARK, (0,0,W,110), border_radius=0)
        title = self.font_lg.render("SUDOKU", True, WHITE)
        self.screen.blit(title, (30, 18))
        diff_col = {"easy":GREEN,"medium":GOLD,"hard":RED}.get(self.difficulty, WHITE)
        diff = self.font_sm.render(self.difficulty.upper(), True, diff_col)
        self.screen.blit(diff, (32, 55))

        # timer
        t_str = self._fmt_time(self.elapsed)
        tc = self.font_md.render(f"⏱ {t_str}", True, WHITE)
        self.screen.blit(tc, tc.get_rect(centerx=W//2, y=20))

        # errors
        err_txt = self.font_md.render("Errors:", True, WHITE)
        self.screen.blit(err_txt, (W-200, 18))
        for i in range(self.MAX_ERRORS):
            col = RED if i < self.errors else GRAY_DARK
            pygame.draw.circle(self.screen, col, (W-120+i*28, 30), 10)
        if not self.error_limit:
            note = self.font_sm.render("(unlimited)", True, GRAY_MID)
            self.screen.blit(note, (W-200, 50))

        # draft indicator
        if self.draft_mode:
            d = self.font_sm.render("✏ DRAFT", True, (200,160,255))
            self.screen.blit(d, (W//2-30, 55))

        # solving indicator
        if self.state == "solving":
            s = self.font_sm.render("⚡ Auto solving…", True, ORANGE)
            self.screen.blit(s, s.get_rect(centerx=W//2, y=78))

    # ── Board ─────────────────────────────────────────────────────────────────
    def _draw_board(self):
        now = time.time()
        sel = self.selected
        sel_num = (self.board[sel[0]][sel[1]] if sel and self.board[sel[0]][sel[1]]!=0 else None) if sel else None

        # background per cell
        for r in range(9):
            for c in range(9):
                rect = self.cell_rect(r, c)
                flash_info = self.flash.get((r,c))
                if flash_info:
                    pygame.draw.rect(self.screen, flash_info[0], rect)
                elif sel and (r,c)==sel:
                    pygame.draw.rect(self.screen, BLUE_LIGHT, rect)
                elif sel and (r==sel[0] or c==sel[1] or
                              (r//3==sel[0]//3 and c//3==sel[1]//3)):
                    pygame.draw.rect(self.screen, BLUE_PALE, rect)
                elif sel_num and self.board[r][c]==sel_num:
                    pygame.draw.rect(self.screen, (220,230,255), rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, rect)

        # numbers
        for r in range(9):
            for c in range(9):
                v = self.board[r][c]
                rect = self.cell_rect(r, c)
                if v != 0:
                    is_err = (r,c) in self.error_cells
                    if self.given[r][c]:
                        col = BLACK
                    elif is_err:
                        col = RED
                    else:
                        col = BLUE_MED
                    txt = self.font_num.render(str(v), True, col)
                    self.screen.blit(txt, txt.get_rect(center=rect.center))
                elif self.drafts[r][c]:
                    self._draw_drafts(rect, self.drafts[r][c])

        # grid lines
        for i in range(10):
            x = BOARD_X + i*CELL
            y = BOARD_Y + i*CELL
            thick = 3 if i % 3 == 0 else 1
            col   = BOX_LINE if i % 3 == 0 else THIN_LINE
            pygame.draw.line(self.screen, col, (BOARD_X, y), (BOARD_X+GRID, y), thick)
            pygame.draw.line(self.screen, col, (x, BOARD_Y), (x, BOARD_Y+GRID), thick)

        # outer border
        pygame.draw.rect(self.screen, BOX_LINE, (BOARD_X, BOARD_Y, GRID, GRID), 3)

    def _draw_drafts(self, cell_rect, nums):
        for n in sorted(nums):
            dr = (n-1)//3
            dc = (n-1) % 3
            x  = cell_rect.x + 4 + dc*(CELL//3)
            y  = cell_rect.y + 4 + dr*(CELL//3)
            t  = self.font_dft.render(str(n), True, PURPLE)
            self.screen.blit(t, (x,y))

    # ── UI buttons below board ────────────────────────────────────────────────
    def _draw_ui_buttons(self):
        if self.state not in ("playing",): return
        for b in [self.btn_new, self.btn_draft, self.btn_solve, self.btn_limit,
                  self.btn_menu, self.btn_hint]+self.numpad_btns+[self.btn_erase]:
            b.draw(self.screen, self.font_sm)
        # label above numpad
        lbl = self.font_sm.render("Number pad:", True, GRAY_DARK)
        self.screen.blit(lbl, (BOARD_X, self.numpad_y - 20))

    # ── Overlay (won / lost) ──────────────────────────────────────────────────
    def _draw_overlay(self, title, col, sub=""):
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        surf.fill((0,0,0,160))
        self.screen.blit(surf, (0,0))

        box = pygame.Rect(W//2-220, H//2-120, 440, 220)
        pygame.draw.rect(self.screen, WHITE, box, border_radius=18)
        pygame.draw.rect(self.screen, col, box, 4, border_radius=18)

        t = self.font_lg.render(title, True, col)
        self.screen.blit(t, t.get_rect(centerx=W//2, y=box.y+30))
        if sub:
            s = self.font_md.render(sub, True, GRAY_DARK)
            self.screen.blit(s, s.get_rect(centerx=W//2, y=box.y+85))

        # replay button
        rb = pygame.Rect(W//2-90, box.y+140, 180, 44)
        pygame.draw.rect(self.screen, BLUE_MED, rb, border_radius=10)
        rt = self.font_md.render("Play Again", True, WHITE)
        self.screen.blit(rt, rt.get_rect(center=rb.center))
        mx,my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and rb.collidepoint(mx,my):
            self.state = "menu"

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _fmt_time(self, secs):
        secs = int(secs)
        return f"{secs//60:02d}:{secs%60:02d}"


if __name__ == "__main__":
    game = SudokuGame()
    game.run()