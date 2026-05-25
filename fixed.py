import pygame
import sys
import random
import time
import copy
import math

# ─── Constants ───────────────────────────────────────────────────────────────
FPS     = 60
CELL    = 52
GRID    = CELL * 9       # 468
BOARD_X = 25
HEADER_H = 110
BOARD_Y  = HEADER_H + 16
# bottom: 14 + 38 + 10 + 34 + 10 + 20 + 52 + 14 = ~192
W = BOARD_X * 2 + GRID   # 518
H = BOARD_Y + GRID + 192  # ~786

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



# ─── Puzzle data ─────────────────────────────────────────────────────────────
BASE_PUZZLES = [
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
    if num in board[row]: return False
    if num in [board[r][col] for r in range(9)]: return False
    br, bc = (row//3)*3, (col//3)*3
    for r in range(br, br+3):
        for c in range(bc, bc+3):
            if board[r][c] == num: return False
    return True

def solve_backtrack(board, steps=None):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for num in range(1, 10):
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if steps is not None: steps.append((r, c, num))
                        if solve_backtrack(board, steps): return True
                        board[r][c] = 0
                        if steps is not None: steps.append((r, c, 0))
                return False
    return True

def generate_puzzle(difficulty="medium"):
    idx = random.randrange(len(BASE_PUZZLES))
    puzzle_str, sol_str = BASE_PUZZLES[idx]
    puzzle   = str_to_board(puzzle_str)
    solution = str_to_board(sol_str)
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

# ─── Icon drawing helpers ─────────────────────────────────────────────────────
def draw_clock_icon(surf, cx, cy, r, color, tick_frac=0.0):
    """Draw a simple clock icon. tick_frac rotates the minute hand (0–1)."""
    pygame.draw.circle(surf, color, (cx, cy), r, 2)
    # hour ticks
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        r0  = r - 4 if i % 3 == 0 else r - 2
        x0  = cx + int(r0  * math.cos(ang))
        y0  = cy + int(r0  * math.sin(ang))
        x1  = cx + int((r-1) * math.cos(ang))
        y1  = cy + int((r-1) * math.sin(ang))
        pygame.draw.line(surf, color, (x0,y0), (x1,y1), 2 if i%3==0 else 1)
    # minute hand (rotates)
    ang_m = math.radians(tick_frac * 360 - 90)
    mx = cx + int((r-4) * math.cos(ang_m))
    my = cy + int((r-4) * math.sin(ang_m))
    pygame.draw.line(surf, color, (cx, cy), (mx, my), 2)
    # hour hand (fixed ~10:10 look)
    ang_h = math.radians(-60)
    hx = cx + int((r-8) * math.cos(ang_h))
    hy = cy + int((r-8) * math.sin(ang_h))
    pygame.draw.line(surf, color, (cx, cy), (hx, hy), 3)
    # center dot
    pygame.draw.circle(surf, color, (cx, cy), 2)

def draw_tick_icon(surf, cx, cy, r, color):
    """Draw a circle with a checkmark inside."""
    pygame.draw.circle(surf, color, (cx, cy), r, 0)
    pygame.draw.circle(surf, WHITE, (cx, cy), r-3, 0)
    # checkmark
    pts = [
        (cx - r//2, cy),
        (cx - r//5, cy + r//3),
        (cx + r//2, cy - r//3),
    ]
    pygame.draw.lines(surf, color, False, pts, 3)

def draw_x_icon(surf, cx, cy, r, color):
    """Draw a red circle with X inside."""
    pygame.draw.circle(surf, color, (cx, cy), r, 0)
    pygame.draw.circle(surf, WHITE, (cx, cy), r-3, 0)
    m = r // 3
    pygame.draw.line(surf, color, (cx-m, cy-m), (cx+m, cy+m), 3)
    pygame.draw.line(surf, color, (cx+m, cy-m), (cx-m, cy+m), 3)

# ─── Button ───────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, color, text_color=WHITE, radius=10, font=None, icon=None):
        self.rect       = pygame.Rect(rect)
        self.label      = label
        self.color      = color
        self.hover_col  = tuple(min(255, v+30) for v in color)
        self.text_color = text_color
        self.radius     = radius
        self.font       = font
        self.icon       = icon
        self.hovered    = False

    def draw(self, surf, font):
        f   = self.font or font
        col = self.hover_col if self.hovered else self.color
        pygame.draw.rect(surf, col, self.rect, border_radius=self.radius)
        pygame.draw.rect(surf, WHITE, self.rect, 1, border_radius=self.radius)
        if self.icon == "erase":
            self._draw_erase_icon(surf)
        else:
            txt = f.render(self.label, True, self.text_color)
            surf.blit(txt, txt.get_rect(center=self.rect.center))

    def _draw_erase_icon(self, surf):
        pad_x = 12
        pad_y = 10
        x0 = self.rect.x + pad_x
        x1 = self.rect.right - pad_x
        y0 = self.rect.y + pad_y
        y1 = self.rect.bottom - pad_y
        points = [
            (x0, y1 - 6),
            (x0 + 10, y1),
            (x1, y0 + 6),
            (x1 - 10, y0),
        ]
        pygame.draw.polygon(surf, self.text_color, points)
        pygame.draw.polygon(surf, WHITE, points, 2)
        strike_y = self.rect.y + self.rect.height * 0.45
        pygame.draw.line(surf, WHITE, (x0 + 8, strike_y), (x1 - 8, strike_y), 2)

    def update(self, pos): self.hovered = self.rect.collidepoint(pos)
    def clicked(self, pos): return self.rect.collidepoint(pos)

# ─── Main game ────────────────────────────────────────────────────────────────
class SudokuGame:
    MAX_ERRORS = 3
    MAX_HINTS = 3

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Sudoku")
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_xl  = pygame.font.SysFont("segoeui", 38, bold=True)
        self.font_lg  = pygame.font.SysFont("segoeui", 26, bold=True)
        self.font_md  = pygame.font.SysFont("segoeui", 20)
        self.font_sm  = pygame.font.SysFont("segoeui", 15)
        self.font_sm_bold = pygame.font.SysFont("segoeui", 15, bold=True)
        self.font_xs  = pygame.font.SysFont("segoeui", 13)
        self.font_xs_bold = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_num = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_dft = pygame.font.SysFont("segoeui", 13)
        self.font_mono= pygame.font.SysFont("couriernew", 18, bold=True)

        self.solve_ms   = None
        self.clock_anim = 0.0

        self.state = "menu"
        self._build_menu()
        self.new_game("medium")

    # ── Layout helpers ────────────────────────────────────────────────────────
    def cell_rect(self, r, c):
        return pygame.Rect(BOARD_X + c*CELL, BOARD_Y + r*CELL, CELL, CELL)

    def pos_to_cell(self, mx, my):
        c = (mx - BOARD_X) // CELL
        r = (my - BOARD_Y) // CELL
        if 0 <= r < 9 and 0 <= c < 9:
            return r, c
        return None, None

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_menu(self):
        self.menu_btns = [
            Button((W//2-100, 220, 200, 46), "Easy",   GREEN,    radius=12),
            Button((W//2-100, 291, 200, 46), "Medium", BLUE_MED, radius=12),
            Button((W//2-100, 361, 200, 46), "Hard",   ORANGE,   radius=12),
        ]

    def _build_game_buttons(self):
        bx = BOARD_X
        by = BOARD_Y + GRID + 14
        bw, bh = 90, 34
        gap = 8

        self.btn_new   = Button((bx,              by, bw, bh), "New Game",   BLUE_MED,  radius=7)
        self.btn_draft = Button((bx+bw+gap,       by, bw, bh),
                                "Draft: ON" if self.draft_mode else "Draft: OFF",
                                PURPLE if self.draft_mode else GRAY_MID, radius=7)
        self.btn_solve = Button((bx+2*(bw+gap),   by, bw, bh), "Auto Solve", ORANGE,    radius=7)
        self.btn_limit = Button((bx+3*(bw+gap),   by, bw+14, bh),
                                f"Limit: {'ON' if self.error_limit else 'OFF'}",
                                RED if self.error_limit else GRAY_MID, radius=7)
        self.btn_menu  = Button((bx,              by+44, 70, 30), "Menu",  GRAY_DARK, radius=7)
        self.btn_hint  = Button((bx+80,           by+44, 70, 30), "Hint",    GOLD,      radius=7,
                                font=self.font_sm)

        # Numpad — 10 buttons (1-9 + ⌫) spanning GRID width
        self.numpad_btns = []
        ny = by + 44 + 40
        ng = 5
        nw = (GRID - 9 * ng) // 10
        nh = 44
        for i in range(1, 10):
            nx = BOARD_X + (i-1) * (nw + ng)
            self.numpad_btns.append(Button((nx, ny, nw, nh), str(i), BLUE_DARK, radius=5,
                                           font=self.font_md))
        erase_x = BOARD_X + 9 * (nw + ng)
        erase_w = BOARD_X + GRID - erase_x
        self.btn_erase = Button((erase_x, ny, erase_w, nh), "DEL", GRAY_DARK, radius=5,
                                font=self.font_md)
        self.numpad_y = ny

    # ── New game ──────────────────────────────────────────────────────────────
    def new_game(self, difficulty="medium"):
        self.difficulty  = difficulty
        self.puzzle, self.solution = generate_puzzle(difficulty)
        self.board       = copy.deepcopy(self.puzzle)
        self.given       = [[self.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
        self.drafts      = [[set() for _ in range(9)] for _ in range(9)]
        self.selected    = None
        self.errors      = 0
        self.error_cells = set()
        self.draft_mode  = False
        self.error_limit = True
        self.solved      = False
        self.start_time  = time.time()
        self.elapsed     = 0
        self.hints_used  = 0
        self.flash       = {}
        self.solve_ms    = None
        self._build_game_buttons()

    # ── Event loop ────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()

    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()
        if self.state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in self.menu_btns:
                    if btn.clicked((mx,my)):
                        self.new_game(btn.label.lower())
                        self.state = "playing"
        elif self.state in ("playing",):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(mx, my)
            if event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_click(self, mx, my):
        r, c = self.pos_to_cell(mx, my)
        if r is not None:
            self.selected = (r, c); return

        if self.btn_new.clicked((mx,my)):
            self.state = "menu"
            return
        if self.btn_draft.clicked((mx,my)):
            self.draft_mode = not self.draft_mode
            self.btn_draft.label = "Draft: ON" if self.draft_mode else "Draft: OFF"
            self.btn_draft.color = PURPLE if self.draft_mode else GRAY_MID; return
        if self.btn_solve.clicked((mx,my)): self._instant_auto_solve(); return
        if self.btn_limit.clicked((mx,my)):
            self.error_limit = not self.error_limit
            self.btn_limit.label = f"Limit: {'ON' if self.error_limit else 'OFF'}"
            self.btn_limit.color = RED if self.error_limit else GRAY_MID; return
        if self.btn_menu.clicked((mx,my)):
            self.state = "menu"
            return
        if self.btn_hint.clicked((mx,my)):  self._give_hint(); return
        for btn in self.numpad_btns:
            if btn.clicked((mx,my)): self._place_num(int(btn.label)); return
        if self.btn_erase.clicked((mx,my)): self._erase(); return

    def _handle_key(self, event):
        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            if self.selected is None: self.selected = (0,0); return
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
            if num in self.drafts[r][c]: self.drafts[r][c].remove(num)
            else: self.drafts[r][c].add(num)
            return

        correct = self.solution[r][c]
        if num == self.board[r][c]: return

        if self.error_limit:
            if num != correct:
                self.errors += 1
                self.board[r][c] = num
                self.error_cells.add((r,c))
                self._flash(r, c, RED_LIGHT)
                if self.errors >= self.MAX_ERRORS: self.state = "lost"
                return
            else:
                self.error_cells.discard((r,c))
                self.board[r][c] = num
                self.drafts[r][c].clear()
                self._clear_related_drafts(r, c, num)
                self._flash(r, c, GREEN_LIGHT)
        else:
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
        if self.hints_used >= self.MAX_HINTS: return
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
                if self.board[r][c] != self.solution[r][c]: return
        self.solved  = True
        self.state   = "won"
        self.elapsed = time.time() - self.start_time

    def _flash(self, r, c, color, duration=0.5):
        self.flash[(r,c)] = (color, time.time()+duration)

    # ── Instant Auto Solver ───────────────────────────────────────────────────
    def _instant_auto_solve(self):
        """Solve instantly, measure real CPU time in microseconds."""
        temp = copy.deepcopy(self.puzzle)
        t0   = time.perf_counter()
        solve_backtrack(temp)
        t1   = time.perf_counter()
        self.solve_ms = (t1 - t0) * 1000.0   # milliseconds (can be < 1 ms)

        # Apply solution to board
        for r in range(9):
            for c in range(9):
                self.board[r][c] = temp[r][c]
                self.given[r][c] = True
        self.error_cells.clear()
        self.drafts = [[set() for _ in range(9)] for _ in range(9)]
        self.solved  = True
        self.elapsed = time.time() - self.start_time
        self.state   = "won"

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        if self.state == "menu":
            for btn in self.menu_btns:
                btn.update((mx,my))
        elif self.state == "playing":
            for b in ([self.btn_new, self.btn_draft, self.btn_solve,
                       self.btn_limit, self.btn_menu, self.btn_hint]
                      + self.numpad_btns + [self.btn_erase]):
                b.update((mx,my))
            if not self.solved:
                self.elapsed = time.time() - self.start_time
                # animate clock hand
                self.clock_anim = (self.elapsed % 60) / 60.0
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
                self._draw_overlay_won()
            elif self.state == "lost":
                self._draw_overlay_lost()

    # ── Menu ──────────────────────────────────────────────────────────────────
    def _draw_menu(self):
        # Title
        t = self.font_xl.render("SUDOKU", True, BLUE_DARK)
        self.screen.blit(t, t.get_rect(centerx=W//2, y=60))

        sub = self.font_sm.render("Select difficulty to start", True, GRAY_DARK)
        self.screen.blit(sub, sub.get_rect(centerx=W//2, y=118))

        # Difficulty buttons
        info = [
            ("Easy",   GREEN,    "Perfect for beginners"),
            ("Medium", BLUE_MED, "A balanced challenge"),
            ("Hard",   ORANGE,   "For seasoned players"),
        ]
        for i, (label, col, desc) in enumerate(info):
            btn = self.menu_btns[i]
            btn.draw(self.screen, self.font_md)
            d = self.font_xs.render(desc, True, GRAY_DARK)
            self.screen.blit(d, d.get_rect(centerx=W//2, y=btn.rect.bottom + 4))

        # Decorative clock icon
        draw_clock_icon(self.screen, W//2, 480, 20, GRAY_MID, tick_frac=0.3)

        # Footer instructions
        lines = [
            "Click / Arrow keys  ·  navigate",
            "1–9 / numpad        ·  place numbers",
            "Draft mode          ·  pencil candidates",
            "Auto Solve          ·  instant + timing",
        ]
        for i, line in enumerate(lines):
            t2 = self.font_xs.render(line, True, GRAY_MID)
            self.screen.blit(t2, t2.get_rect(centerx=W//2, y=512 + i*20))

    # ── Header ────────────────────────────────────────────────────────────────
    def _draw_header(self):
        pygame.draw.rect(self.screen, BLUE_DARK, (0, 0, W, HEADER_H))

        # Title (left)
        title = self.font_lg.render("SUDOKU", True, WHITE)
        self.screen.blit(title, (30, 14))

        # Difficulty badge
        diff_col = {"easy": GREEN, "medium": GOLD, "hard": RED}.get(self.difficulty, WHITE)
        diff     = self.font_sm_bold.render(self.difficulty.upper(), True, diff_col)
        self.screen.blit(diff, (32, 52))

        # Draft indicator (below difficulty, no overlap)
        if self.draft_mode:
            d = self.font_xs.render("✏ DRAFT", True, (200, 160, 255))
            self.screen.blit(d, (32, 74))

        # ── Clock icon + timer (center) ──────────────────────────────────────
        cx_center = W // 2
        clock_r   = 16
        clock_cx  = cx_center - 56
        clock_cy  = 34
        draw_clock_icon(self.screen, clock_cx, clock_cy, clock_r, WHITE, self.clock_anim)
        t_str = self._fmt_time_precise(self.elapsed)
        tc    = self.font_md.render(t_str, True, WHITE)
        self.screen.blit(tc, (clock_cx + clock_r + 6, clock_cy - tc.get_height()//2))

        # ── Errors (right side) ───────────────────────────────────────────────
        err_txt = self.font_sm.render("Errors:", True, WHITE)
        self.screen.blit(err_txt, (W - 200, 14))
        for i in range(self.MAX_ERRORS):
            ecx = W - 120 + i * 30
            ecy = 28
            if i < self.errors:
                draw_x_icon(self.screen, ecx, ecy, 11, RED)
            else:
                pygame.draw.circle(self.screen, GRAY_DARK, (ecx, ecy), 11, 2)

        if not self.error_limit:
            note = self.font_xs.render("(unlimited)", True, GRAY_MID)
            self.screen.blit(note, (W - 200, 44))

        # ── Auto solve timing result ──────────────────────────────────────────
        if self.solve_ms is not None:
            ms = self.solve_ms
            if ms >= 1.0:
                ts = f"Solved in {ms:.3f} ms"
            else:
                ts = f"Solved in {ms*1000:.1f} µs"
            timing_surf = self.font_xs.render(ts, True, GOLD)
            self.screen.blit(timing_surf, timing_surf.get_rect(centerx=W//2, y=68))
        else:
            # second row of header: hints count
            hints_remaining = self.MAX_HINTS - self.hints_used
            h_txt = self.font_xs_bold.render(f"Hints: {hints_remaining}/{self.MAX_HINTS}", True, WHITE)
            self.screen.blit(h_txt, h_txt.get_rect(centerx=W//2, y=68))

        # Separator line
        pygame.draw.line(self.screen, (60, 100, 220), (0, HEADER_H-1), (W, HEADER_H-1), 2)

    # ── Board ─────────────────────────────────────────────────────────────────
    def _draw_board(self):
        sel     = self.selected
        sel_num = (self.board[sel[0]][sel[1]] if sel and self.board[sel[0]][sel[1]] != 0 else None) if sel else None

        for r in range(9):
            for c in range(9):
                rect       = self.cell_rect(r, c)
                flash_info = self.flash.get((r,c))
                if flash_info:
                    pygame.draw.rect(self.screen, flash_info[0], rect)
                elif sel and (r,c) == sel:
                    pygame.draw.rect(self.screen, BLUE_LIGHT, rect)
                elif sel and (r==sel[0] or c==sel[1] or
                              (r//3==sel[0]//3 and c//3==sel[1]//3)):
                    pygame.draw.rect(self.screen, BLUE_PALE, rect)
                elif sel_num and self.board[r][c] == sel_num:
                    pygame.draw.rect(self.screen, (220, 230, 255), rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, rect)

        for r in range(9):
            for c in range(9):
                v    = self.board[r][c]
                rect = self.cell_rect(r, c)
                if v != 0:
                    is_err = (r,c) in self.error_cells
                    col = BLACK if self.given[r][c] else (RED if is_err else BLUE_MED)
                    txt = self.font_num.render(str(v), True, col)
                    self.screen.blit(txt, txt.get_rect(center=rect.center))
                elif self.drafts[r][c]:
                    self._draw_drafts(rect, self.drafts[r][c])

        for i in range(10):
            x     = BOARD_X + i*CELL
            y     = BOARD_Y + i*CELL
            thick = 3 if i%3==0 else 1
            col   = BOX_LINE if i%3==0 else THIN_LINE
            if i % 3 != 0:  # Draw thin lines first
                pygame.draw.line(self.screen, col, (BOARD_X, y), (BOARD_X+GRID, y), thick)
                pygame.draw.line(self.screen, col, (x, BOARD_Y), (x, BOARD_Y+GRID), thick)
        
        for i in range(10):
            if i % 3 == 0:  # Draw bold lines last to cover thin lines
                x     = BOARD_X + i*CELL
                y     = BOARD_Y + i*CELL
                col   = BOX_LINE
                pygame.draw.line(self.screen, col, (BOARD_X, y), (BOARD_X+GRID, y), 3)
                pygame.draw.line(self.screen, col, (x, BOARD_Y), (x, BOARD_Y+GRID), 3)
        
        pygame.draw.rect(self.screen, BOX_LINE, (BOARD_X, BOARD_Y, GRID, GRID), 3)

    def _draw_drafts(self, cell_rect, nums):
        cell_third = CELL / 3.0
        for n in sorted(nums):
            dr = (n-1) // 3
            dc = (n-1) % 3
            sub_x = cell_rect.x + dc * cell_third
            sub_y = cell_rect.y + dr * cell_third
            txt = self.font_dft.render(str(n), True, PURPLE)
            txt_rect = txt.get_rect(center=(sub_x + cell_third/2, sub_y + cell_third/2))
            self.screen.blit(txt, txt_rect)

    # ── Game buttons ──────────────────────────────────────────────────────────
    def _draw_ui_buttons(self):
        if self.state != "playing": return
        for b in ([self.btn_new, self.btn_draft, self.btn_solve, self.btn_limit,
                   self.btn_menu, self.btn_hint] + self.numpad_btns + [self.btn_erase]):
            b.draw(self.screen, self.font_sm)

    # ── Win overlay ───────────────────────────────────────────────────────────
    def _draw_overlay_won(self):
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 150))
        self.screen.blit(surf, (0, 0))

        box = pygame.Rect(W//2-230, H//2-150, 460, 290)
        pygame.draw.rect(self.screen, WHITE, box, border_radius=20)
        pygame.draw.rect(self.screen, GREEN, box, 4, border_radius=20)

        # Big tick icon
        draw_tick_icon(self.screen, W//2, box.y + 56, 36, GREEN)

        # Title
        t = self.font_lg.render("Puzzle Solved!", True, GREEN)
        self.screen.blit(t, t.get_rect(centerx=W//2, y=box.y + 100))

        # Stats
        time_str  = self._fmt_time_precise(self.elapsed)
        stats_str = f"Time: {time_str}   Hints: {self.hints_used}/{self.MAX_HINTS}   Errors: {self.errors}"
        s = self.font_sm.render(stats_str, True, GRAY_DARK)
        self.screen.blit(s, s.get_rect(centerx=W//2, y=box.y + 142))

        # Auto-solve timing (if used)
        if self.solve_ms is not None:
            ms = self.solve_ms
            ts = (f"Auto-solve: {ms:.3f} ms" if ms >= 1.0
                  else f"Auto-solve: {ms*1000:.1f} µs")
            t2 = self.font_mono.render(ts, True, BLUE_MED)
            self.screen.blit(t2, t2.get_rect(centerx=W//2, y=box.y + 172))

        # Play Again button
        rb = pygame.Rect(W//2-100, box.y+220, 200, 46)
        pygame.draw.rect(self.screen, BLUE_MED, rb, border_radius=12)
        rt = self.font_md.render("Play Again", True, WHITE)
        self.screen.blit(rt, rt.get_rect(center=rb.center))
        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and rb.collidepoint(mx, my):
            self.state = "menu"
    def _draw_overlay_lost(self):
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 150))
        self.screen.blit(surf, (0, 0))

        box = pygame.Rect(W//2-220, H//2-130, 440, 250)
        pygame.draw.rect(self.screen, WHITE, box, border_radius=20)
        pygame.draw.rect(self.screen, RED, box, 4, border_radius=20)

        # Big X icon
        draw_x_icon(self.screen, W//2, box.y + 52, 36, RED)

        # Title
        t = self.font_lg.render("Game Over", True, RED)
        self.screen.blit(t, t.get_rect(centerx=W//2, y=box.y + 100))

        s = self.font_sm.render(f"You made {self.MAX_ERRORS} errors!", True, GRAY_DARK)
        self.screen.blit(s, s.get_rect(centerx=W//2, y=box.y + 142))

        rb = pygame.Rect(W//2-100, box.y+185, 200, 46)
        pygame.draw.rect(self.screen, BLUE_MED, rb, border_radius=12)
        rt = self.font_md.render("Play Again", True, WHITE)
        self.screen.blit(rt, rt.get_rect(center=rb.center))
        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and rb.collidepoint(mx, my):
            self.state = "menu"
    def _fmt_time(self, secs):
        secs = int(secs)
        return f"{secs//60:02d}:{secs%60:02d}"

    def _fmt_time_precise(self, secs):
        """MM:SS  (minutes and seconds, no fractional)"""
        secs = int(secs)
        mins = secs // 60
        sec  = secs % 60
        return f"{mins:02d}:{sec:02d}"


if __name__ == "__main__":
    game = SudokuGame()
    game.run()