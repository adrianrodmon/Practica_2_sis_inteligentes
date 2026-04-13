"""
Visualizador 3D "jaula de cristal" para Tic-Tac-Toe 4x4x4
- Arrastrar con clic derecho (o clic izquierdo fuera del cubo) para rotar
- Sin etiquetas en las casillas
- Cubo centrado en pantalla

Dependencias:
    pip install pygame

Controles:
    Clic izquierdo   → jugar casilla (hover resaltado)
    Arrastrar (drag) → rotar el cubo libremente
    R                → reiniciar partida
    ESC              → salir
"""

import pygame
import sys
import math
from collections import namedtuple

# ─── Paleta ───────────────────────────────────────────────────────────────────
BG        = (12,  14,  20)
PANEL_BG  = (18,  21,  30)
ACCENT    = (60,  70, 110)

EDGE_DIM  = (38,  44,  68)
EDGE_HOV  = (100, 130, 220)
WIN_EDGE  = (60,  210, 110)

X_EDGE    = ( 70, 150, 230)
X_FILL    = ( 20,  50,  90)
O_EDGE    = (230,  80,  55)
O_FILL    = ( 90,  28,  18)
HOV_FILL  = ( 60,  90, 180)
WIN_FILL  = ( 20,  80,  40)

TEXT_MAIN = (210, 218, 240)
TEXT_DIM  = ( 90, 100, 135)

CUBE_OUTLINE  = (90, 105, 160)   # contorno exterior del cubo
INNER_OUTLINE = (120, 140, 200)  # contorno del cubo interior

BTN_BG     = (35,  42,  65)
BTN_BORDER = (80,  95, 145)
BTN_ACTIVE = (60, 130, 220)

FACE_ALPHA = 55

# ─── Config ───────────────────────────────────────────────────────────────────
WIDTH, HEIGHT  = 1020, 700
PANEL_X        = 760          # donde empieza el panel lateral
CANVAS_CX      = PANEL_X // 2 # centro horizontal del area de juego = 380
CANVAS_CY      = HEIGHT  // 2 # centro vertical = 350

N         = 4
FPS       = 60
CELL_SIZE = 54

# Ángulos iniciales (rotación libre con matriz 3x3)
INIT_YAW   = math.radians(45)   # rotación horizontal inicial
INIT_PITCH = math.radians(25)   # inclinación vertical inicial

ElEstado = namedtuple('ElEstado', 'jugador, get_utilidad, tablero, movidas')
FACE_NAMES = ['bottom', 'back', 'left', 'right', 'front', 'top']


# ─── Matemática de rotación libre ─────────────────────────────────────────────

def mat_rotY(a):
    """Matriz de rotación alrededor del eje Y (yaw)."""
    c, s = math.cos(a), math.sin(a)
    return [[c,0,s],[0,1,0],[-s,0,c]]

def mat_rotX(a):
    """Matriz de rotación alrededor del eje X (pitch)."""
    c, s = math.cos(a), math.sin(a)
    return [[1,0,0],[0,c,-s],[0,s,c]]

def mat_mul(A, B):
    """Multiplicación de matrices 3x3."""
    return [
        [sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]

def mat_vec(M, v):
    """Aplica matriz 3x3 a vector 3D."""
    return [sum(M[i][k]*v[k] for k in range(3)) for i in range(3)]

def mat_identity():
    return [[1,0,0],[0,1,0],[0,0,1]]


def project(rx, ry, rz):
    """
    Proyección ortográfica simple después de rotar.
    El eje Z sale de la pantalla, Y va hacia arriba, X hacia la derecha.
    """
    scale = CELL_SIZE
    sx = int(CANVAS_CX + rx * scale)
    sy = int(CANVAS_CY - rz * scale)   # Z invertido: arriba en pantalla
    return (sx, sy)


def point_in_poly(px, py, poly):
    inside = False
    x0, y0 = poly[-1]
    for x1, y1 in poly:
        if (y0 > py) != (y1 > py):
            xint = (x1-x0)*(py-y0)/(y1-y0+1e-12) + x0
            if px < xint:
                inside = not inside
        x0, y0 = x1, y1
    return inside


# ─── Visualizador ─────────────────────────────────────────────────────────────

class Visualizador3D:

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("4x4x4 Tic-Tac-Toe 3D")
        self.clock   = pygame.time.Clock()
        self._surf_a = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        self.font_big   = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Consolas", 15)
        self.font_small = pygame.font.SysFont("Consolas", 12)

        # Estado del juego
        self.hovered_cell = None
        self.win_cells    = []
        self.message      = ""
        self.estado       = None

        # Vista interior: oculta la capa exterior para ver el interior
        self._show_interior = False

        # Rotación: almacenamos la matriz de rotación acumulada
        self._rot = mat_mul(mat_rotX(INIT_PITCH), mat_rotY(INIT_YAW))

        # Drag
        self._dragging   = False
        self._drag_start = None   # (mx, my) al iniciar drag
        self._rot_start  = None   # copia de _rot al iniciar drag

        # Centro lógico del cubo (para rotar alrededor del centro)
        self._cube_center = [(N)/2.0, (N)/2.0, (N)/2.0]

    # ── Proyección con rotación libre ─────────────────────────────────────────

    def _project(self, x, y, z):
        """Transforma (x,y,z) world → pantalla usando la matriz de rotación actual."""
        cx, cy, cz = self._cube_center
        # Centrar en origen antes de rotar
        v = [x - cx, y - cy, z - cz]
        r = mat_vec(self._rot, v)
        return project(r[0], r[1], r[2])

    def _face_pts(self, gx, gy, gz, face):
        x0, x1 = gx, gx+1
        y0, y1 = gy, gy+1
        z0, z1 = gz, gz+1
        verts = {
            'top'   : [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],
            'bottom': [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],
            'front' : [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],
            'back'  : [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],
            'right' : [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],
            'left'  : [(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)],
        }
        return [self._project(*v) for v in verts[face]]

    def _cell_center_proj(self, gx, gy, gz):
        return self._project(gx+0.5, gy+0.5, gz+0.5)

    # ── Profundidad dinámica ───────────────────────────────────────────────────

    def _is_outer(self, gx, gy, gz):
        """Devuelve True si la celda (0-indexed) está en la capa exterior."""
        return gx == 0 or gx == N-1 or gy == 0 or gy == N-1 or gz == 0 or gz == N-1

    def _depth_order(self):
        """
        Recalcula el orden de pintado basado en la rotación actual,
        usando la profundidad Y rotada (eje que apunta hacia el espectador).
        """
        cells = []
        for gz in range(N):
            for gx in range(N):
                for gy in range(N):
                    # Filtrar si estamos en modo interior
                    if self._show_interior and self._is_outer(gx, gy, gz):
                        continue
                    cx, cy, cz = self._cube_center
                    v = [gx+0.5-cx, gy+0.5-cy, gz+0.5-cz]
                    r = mat_vec(self._rot, v)
                    # r[1] es la profundidad en pantalla (Y rotado)
                    cells.append((r[1], gx, gy, gz))
        cells.sort(key=lambda c: c[0])
        return [(c[1], c[2], c[3]) for c in cells]

    # ── Aristas ───────────────────────────────────────────────────────────────

    def _cell_edges(self, gx, gy, gz):
        x0,x1 = gx,gx+1
        y0,y1 = gy,gy+1
        z0,z1 = gz,gz+1
        p = self._project
        v = {
            'A': p(x0,y0,z0), 'B': p(x1,y0,z0),
            'C': p(x1,y1,z0), 'D': p(x0,y1,z0),
            'E': p(x0,y0,z1), 'F': p(x1,y0,z1),
            'G': p(x1,y1,z1), 'H': p(x0,y1,z1),
        }
        pairs = [
            ('A','B'),('B','C'),('C','D'),('D','A'),
            ('E','F'),('F','G'),('G','H'),('H','E'),
            ('A','E'),('B','F'),('C','G'),('D','H'),
        ]
        return [(v[a], v[b]) for a, b in pairs]

    # ── Fill translúcido ──────────────────────────────────────────────────────

    def _draw_face_fill(self, pts, rgb, alpha):
        self._surf_a.fill((0, 0, 0, 0))
        pygame.draw.polygon(self._surf_a, (*rgb, alpha), pts)
        self.screen.blit(self._surf_a, (0, 0))

    # ── Celda ─────────────────────────────────────────────────────────────────

    def _draw_cell(self, gx, gy, gz, tablero):
        key      = (gx+1, gy+1, gz+1)
        value    = tablero.get(key)
        is_hover = (key == self.hovered_cell) and (value is None)
        is_win   = key in self.win_cells

        if is_win:
            edge_c, fill_c, fill_a = WIN_EDGE, WIN_FILL, 80
        elif value == 'X':
            edge_c, fill_c, fill_a = X_EDGE, X_FILL, FACE_ALPHA
        elif value == 'O':
            edge_c, fill_c, fill_a = O_EDGE, O_FILL, FACE_ALPHA
        elif is_hover:
            edge_c, fill_c, fill_a = EDGE_HOV, HOV_FILL, 90
        else:
            edge_c, fill_c, fill_a = EDGE_DIM, None, 0

        if fill_c is not None:
            for face in FACE_NAMES:
                pts = self._face_pts(gx, gy, gz, face)
                self._draw_face_fill(pts, fill_c, fill_a)

        edge_w = 3 if (is_win or is_hover) else 2
        for p1, p2 in self._cell_edges(gx, gy, gz):
            pygame.draw.line(self.screen, edge_c, p1, p2, edge_w)

        if value:
            cx, cy = self._cell_center_proj(gx, gy, gz)
            sym_c = (200,220,255) if value=='X' else (255,180,160)
            if is_win: sym_c = (180,255,200)
            if value == 'X':
                d = 13
                pygame.draw.line(self.screen, sym_c, (cx-d,cy-d),(cx+d,cy+d), 3)
                pygame.draw.line(self.screen, sym_c, (cx+d,cy-d),(cx-d,cy+d), 3)
            else:
                pygame.draw.circle(self.screen, sym_c, (cx,cy), 12, 3)

    # ── Hit-test ──────────────────────────────────────────────────────────────

    def _find_hovered(self, mouse_pos):
        mx, my = mouse_pos
        # No detectar si el cursor está en el panel lateral
        if mx >= PANEL_X:
            return None
        for gx, gy, gz in reversed(self._depth_order()):
            # Respetar filtro de vista interior
            if self._show_interior and self._is_outer(gx, gy, gz):
                continue
            for face in FACE_NAMES:
                pts = self._face_pts(gx, gy, gz, face)
                if point_in_poly(mx, my, pts):
                    return (gx+1, gy+1, gz+1)
        return None

    # ── Fondo y panel ─────────────────────────────────────────────────────────

    def _draw_bg(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, PANEL_BG, (PANEL_X, 0, WIDTH-PANEL_X, HEIGHT))
        pygame.draw.line(self.screen, ACCENT, (PANEL_X, 0), (PANEL_X, HEIGHT), 2)

    def _draw_panel(self):
        px = PANEL_X + 13
        y  = 28

        self._txt("TIC-TAC-TOE",     (px,y), TEXT_MAIN, self.font_big,   False); y += 26
        self._txt("4 x 4 x 4  (3D)", (px,y), TEXT_DIM,  self.font_med,   False); y += 40

        if self.win_cells:
            self._txt(self.message, (px,y), WIN_EDGE, self.font_big, False); y += 34
        elif self.estado and not self.estado.get_utilidad:
            player = self.estado.jugador
            col    = X_EDGE if player=='X' else O_EDGE
            self._txt("Turno:",               (px,y), TEXT_DIM, self.font_med, False); y += 20
            self._txt(f"  Jugador  {player}", (px,y), col,      self.font_big, False); y += 34

        pygame.draw.line(self.screen, ACCENT, (px,y), (px+220,y)); y += 14

        self._txt("Jugadores:", (px,y), TEXT_DIM, self.font_small, False); y += 16
        pygame.draw.line(self.screen, X_EDGE, (px,y+5),(px+12,y+5), 2)
        self._txt("  X  - Humano / J1", (px,y), TEXT_MAIN, self.font_small, False); y += 16
        pygame.draw.line(self.screen, O_EDGE, (px,y+5),(px+12,y+5), 2)
        self._txt("  O  - IA / J2",     (px,y), TEXT_MAIN, self.font_small, False); y += 22

        pygame.draw.line(self.screen, ACCENT, (px,y), (px+220,y)); y += 14

        if self.hovered_cell:
            hx,hy,hz = self.hovered_cell
            self._txt("Seleccionando:",         (px,y), TEXT_DIM, self.font_small, False); y += 16
            self._txt(f"  ({hx}, {hy}, {hz})", (px,y), EDGE_HOV, self.font_med,   False); y += 22
            pygame.draw.line(self.screen, ACCENT, (px,y), (px+220,y)); y += 14

        # ── Botón Vista Interior ──────────────────────────────────────────────
        y += 6
        btn_x, btn_y = px, y
        btn_w, btn_h = 220, 32
        self._btn_interior_rect = (btn_x, btn_y, btn_w, btn_h)
        border_c = BTN_ACTIVE if self._show_interior else BTN_BORDER
        pygame.draw.rect(self.screen, BTN_BG, (btn_x, btn_y, btn_w, btn_h), border_radius=6)
        pygame.draw.rect(self.screen, border_c, (btn_x, btn_y, btn_w, btn_h), 2, border_radius=6)
        label = "● Vista Interior" if self._show_interior else "○ Vista Interior"
        label_c = BTN_ACTIVE if self._show_interior else TEXT_DIM
        self._txt(label, (btn_x + btn_w // 2, btn_y + btn_h // 2), label_c, self.font_med)
        y += btn_h + 10

        # Controles al fondo del panel
        cy2 = HEIGHT - 125
        pygame.draw.line(self.screen, ACCENT, (px,cy2),(px+220,cy2)); cy2 += 12
        self._txt("Controles:",           (px,cy2), TEXT_DIM, self.font_small, False); cy2 += 16
        self._txt("Arrastrar  - rotar",   (px,cy2), TEXT_DIM, self.font_small, False); cy2 += 15
        self._txt("Clic       - jugar",   (px,cy2), TEXT_DIM, self.font_small, False); cy2 += 15
        self._txt("V          - interior",(px,cy2), TEXT_DIM, self.font_small, False); cy2 += 15
        self._txt("R          - reiniciar",(px,cy2), TEXT_DIM, self.font_small, False); cy2 += 15
        self._txt("ESC        - salir",   (px,cy2), TEXT_DIM, self.font_small, False)

    def _txt(self, text, pos, color, font, center=True):
        s = font.render(text, True, color)
        x, y = pos
        if center:
            x -= s.get_width()  // 2
            y -= s.get_height() // 2
        self.screen.blit(s, (x, y))

    # ── Contorno del cubo (exterior e interior) ────────────────────────────────

    def _draw_box_outline(self, lo, hi, color, width=3):
        """Dibuja las 12 aristas de un cubo definido por esquinas (lo,lo,lo)-(hi,hi,hi)."""
        p = self._project
        v = {
            'A': p(lo, lo, lo), 'B': p(hi, lo, lo),
            'C': p(hi, hi, lo), 'D': p(lo, hi, lo),
            'E': p(lo, lo, hi), 'F': p(hi, lo, hi),
            'G': p(hi, hi, hi), 'H': p(lo, hi, hi),
        }
        edges = [
            ('A','B'),('B','C'),('C','D'),('D','A'),
            ('E','F'),('F','G'),('G','H'),('H','E'),
            ('A','E'),('B','F'),('C','G'),('D','H'),
        ]
        for a, b in edges:
            pygame.draw.line(self.screen, color, v[a], v[b], width)

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self, estado=None):
        if estado:
            self.estado = estado
        tablero = self.estado.tablero if self.estado else {}

        self._draw_bg()

        order = self._depth_order()
        for gx, gy, gz in order:
            self._draw_cell(gx, gy, gz, tablero)

        # Contornos del cubo
        if self._show_interior:
            # Solo dibujar el contorno interior (celdas 2-3, coords 1-3)
            self._draw_box_outline(1, N-1, INNER_OUTLINE, 3)
        else:
            # Dibujar ambos contornos
            self._draw_box_outline(0, N, CUBE_OUTLINE, 3)
            self._draw_box_outline(1, N-1, INNER_OUTLINE, 2)

        self._draw_panel()
        pygame.display.flip()

    # ── Rotación con drag ─────────────────────────────────────────────────────

    def _apply_drag(self, mx, my):
        """Actualiza la matriz de rotación según el desplazamiento del mouse."""
        dx = mx - self._drag_start[0]
        dy = my - self._drag_start[1]
        # Sensibilidad: 1 pixel ≈ 0.5°
        sens = 0.008
        # Yaw: rotar alrededor de Z del mundo (horizontal en pantalla)
        # Pitch: rotar alrededor del eje X local (vertical en pantalla)
        Ry = mat_rotY(dx * sens)
        Rx = mat_rotX(-dy * sens)
        # Combinar con la rotación base capturada al inicio del drag
        self._rot = mat_mul(Rx, mat_mul(Ry, self._rot_start))

    # ── Bucle de eventos ──────────────────────────────────────────────────────

    def _handle_event(self, ev, validas=None):
        """
        Procesa un evento pygame.
        Retorna:
          - una tupla (x,y,z) si el humano eligió una casilla
          - '__reset__' si se presionó R
          - None en cualquier otro caso
        """
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if ev.key == pygame.K_r:
                return '__reset__'
            if ev.key == pygame.K_v:
                self._show_interior = not self._show_interior

        # ── Clic en botón del panel ──────────────────────────────────────────
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if hasattr(self, '_btn_interior_rect'):
                bx, by, bw, bh = self._btn_interior_rect
                mx, my = ev.pos
                if bx <= mx <= bx + bw and by <= my <= by + bh:
                    self._show_interior = not self._show_interior
                    return None

        # ── Inicio de drag ──────────────────────────────────────────────────
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button in (1, 3):
                self._dragging   = True
                self._drag_start = ev.pos
                self._rot_start  = [row[:] for row in self._rot]  # copia profunda

        # ── Movimiento durante drag ─────────────────────────────────────────
        if ev.type == pygame.MOUSEMOTION:
            if self._dragging:
                self._apply_drag(*ev.pos)
                self.hovered_cell = None   # no hover mientras arrastramos
            else:
                self.hovered_cell = self._find_hovered(ev.pos)

        # ── Fin de drag / clic ──────────────────────────────────────────────
        if ev.type == pygame.MOUSEBUTTONUP:
            if ev.button in (1, 3) and self._dragging:
                dx = abs(ev.pos[0] - self._drag_start[0])
                dy = abs(ev.pos[1] - self._drag_start[1])
                self._dragging = False

                # Solo cuenta como clic si el mouse apenas se movió
                if dx < 5 and dy < 5 and ev.button == 1 and validas is not None:
                    cell = self._find_hovered(ev.pos)
                    if cell and cell in validas:
                        self.hovered_cell = None
                        return cell

        return None

    # ── Interfaz pública ──────────────────────────────────────────────────────

    def actualizar(self, estado, win_cells=None, mensaje=""):
        self.estado    = estado
        self.win_cells = win_cells or []
        self.message   = mensaje
        # Procesar eventos pendientes para que la rotación funcione incluso
        # cuando el juego espera al exterior
        for ev in pygame.event.get():
            self._handle_event(ev)
        self.render(estado)
        self.clock.tick(FPS)

    def esperar_movida(self, estado):
        """
        Bloquea hasta que el humano elija una casilla.
        Mientras espera, permite rotar el cubo con drag.
        """
        self.estado = estado
        validas = set(estado.movidas)

        while True:
            for ev in pygame.event.get():
                result = self._handle_event(ev, validas)
                if result:
                    return result

            self.render(estado)
            self.clock.tick(FPS)

    def mostrar_ganador(self, jugador, win_cells):
        self.win_cells = win_cells
        self.message   = f"Gano {jugador}!"
        t0 = pygame.time.get_ticks()
        while pygame.time.get_ticks() - t0 < 3000:
            for ev in pygame.event.get():
                self._handle_event(ev)
                if ev.type == pygame.KEYDOWN and ev.key in (
                        pygame.K_SPACE, pygame.K_r):
                    return
            self.render()
            self.clock.tick(FPS)

    def cerrar(self):
        pygame.quit()


# ─── Lógica del juego ─────────────────────────────────────────────────────────

def generar_lineas(n=4):
    L = []
    for x in range(1,n+1):
        for y in range(1,n+1):
            L.append([(x,y,z) for z in range(1,n+1)])
            L.append([(x,z,y) for z in range(1,n+1)])
            L.append([(z,x,y) for z in range(1,n+1)])
    for z in range(1,n+1):
        L.append([(i,i,z)     for i in range(1,n+1)])
        L.append([(i,n-i+1,z) for i in range(1,n+1)])
    for y in range(1,n+1):
        L.append([(i,y,i)     for i in range(1,n+1)])
        L.append([(i,y,n-i+1) for i in range(1,n+1)])
    for x in range(1,n+1):
        L.append([(x,i,i)     for i in range(1,n+1)])
        L.append([(x,i,n-i+1) for i in range(1,n+1)])
    L.append([(i,i,i)     for i in range(1,n+1)])
    L.append([(i,i,n-i+1) for i in range(1,n+1)])
    L.append([(i,n-i+1,i) for i in range(1,n+1)])
    L.append([(n-i+1,i,i) for i in range(1,n+1)])
    return L

LINEAS = generar_lineas()


def computa_utilidad(tablero, n=4):
    for l in LINEAS:
        v = [tablero.get(p) for p in l]
        if v.count('X')==n: return  1
        if v.count('O')==n: return -1
    return 0


def get_resultado(estado, m):
    if m not in estado.movidas:
        return estado
    t = estado.tablero.copy()
    t[m] = estado.jugador
    mv = list(estado.movidas); mv.remove(m)
    return ElEstado(
        jugador=('O' if estado.jugador=='X' else 'X'),
        get_utilidad=computa_utilidad(t),
        tablero=t, movidas=mv)


def funcion_eval(estado):
    if estado.get_utilidad ==  1: return  100000
    if estado.get_utilidad == -1: return -100000
    score = 0
    bd = estado.tablero
    pesos = [0, 1, 10, 500, 100000]
    for l in LINEAS:
        v  = [bd.get(p) for p in l]
        xc = v.count('X'); oc = v.count('O')
        if xc and oc: continue
        if xc: score += pesos[xc]
        if oc: score -= pesos[oc]
    # Bonus por control de las 8 celdas centrales del cubo 4x4x4
    for cx in (2,3):
        for cy in (2,3):
            for cz in (2,3):
                c = bd.get((cx,cy,cz))
                if   c == 'X': score += 3
                elif c == 'O': score -= 3
    return score


def _ordenar_movidas(estado):
    """Ordena movidas para mejorar la poda alpha-beta:
       1) Jugadas ganadoras inmediatas
       2) Bloqueos de victoria del oponente
       3) Por cercanía al centro (participan en más líneas)
    """
    wins, blocks, rest = [], [], []
    opp = 'O' if estado.jugador == 'X' else 'X'

    for m in estado.movidas:
        # ¿Esta jugada gana?
        t = estado.tablero.copy()
        t[m] = estado.jugador
        if computa_utilidad(t) != 0:
            wins.append(m)
            continue
        # ¿Bloquea una victoria del oponente?
        t2 = estado.tablero.copy()
        t2[m] = opp
        if computa_utilidad(t2) != 0:
            blocks.append(m)
            continue
        rest.append(m)

    # Ordenar el resto por distancia al centro (más cercano primero)
    centro = (N + 1) / 2.0
    rest.sort(key=lambda m: sum((x - centro) ** 2 for x in m))
    return wins + blocks + rest


def ia_elegir(estado, altura=3):
    jug = estado.jugador
    # Factor de signo: funcion_eval siempre da score desde perspectiva X
    # Si la IA juega O, necesitamos invertir para que maximize correctamente
    factor = 1 if jug == 'X' else -1

    def terminal(e): return e.get_utilidad != 0 or not e.movidas
    def util(e):     return e.get_utilidad * factor
    def heur(e):     return funcion_eval(e) * factor

    def maxv(e, a, b, d):
        if terminal(e): return util(e)
        if d == 0: return heur(e)
        v = -1e9
        for m in _ordenar_movidas(e):
            v = max(v, minv(get_resultado(e, m), a, b, d - 1))
            if v >= b: return v
            a = max(a, v)
        return v

    def minv(e, a, b, d):
        if terminal(e): return util(e)
        if d == 0: return heur(e)
        v = 1e9
        for m in _ordenar_movidas(e):
            v = min(v, maxv(get_resultado(e, m), a, b, d - 1))
            if v <= a: return v
            b = min(b, v)
        return v

    best, bval = None, -1e9
    for m in _ordenar_movidas(estado):
        val = minv(get_resultado(estado, m), -1e9, 1e9, altura)
        if val > bval:
            bval = val; best = m
    return best


def crear_estado():
    mvs = [(x,y,z) for x in range(1,N+1)
                   for y in range(1,N+1)
                   for z in range(1,N+1)]
    return ElEstado(jugador='X', get_utilidad=0, tablero={}, movidas=mvs)


def linea_ganadora(tablero):
    for l in LINEAS:
        v = [tablero.get(p) for p in l]
        if v.count('X')==4 or v.count('O')==4: return l
    return []


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    MODO      = 'hva'   # 'hva' = Humano vs IA  |  'hvh' = Humano vs Humano
    ALTURA_IA = 2       # profundidad alpha-beta (3 si tu PC aguanta)

    vis    = Visualizador3D()
    estado = crear_estado()

    print("=== 4x4x4 Tic-Tac-Toe 3D ===")
    print(f"Modo: {'Humano (X) vs IA (O)' if MODO=='hva' else 'Humano vs Humano'}")
    print("Arrastra para rotar el cubo. Clic para jugar.")
    print("R = reiniciar  |  ESC = salir\n")

    while True:
        vis.actualizar(estado)

        if estado.get_utilidad != 0:
            wl  = linea_ganadora(estado.tablero)
            gan = 'X' if estado.get_utilidad==1 else 'O'
            print(f"\nGano {gan}!")
            vis.mostrar_ganador(gan, wl)
            estado = crear_estado()
            vis.win_cells = []
            continue

        if not estado.movidas:
            print("\nEmpate.")
            vis.message = "Empate"
            pygame.time.wait(2500)
            estado = crear_estado()
            continue

        es_humano = (MODO=='hvh') or (estado.jugador=='X')

        if es_humano:
            movida = vis.esperar_movida(estado)
            if movida == '__reset__':
                estado = crear_estado()
                vis.win_cells = []
                continue
            print(f"Humano ({estado.jugador}) -> {movida}")
        else:
            print("IA pensando...", end=" ", flush=True)
            vis.render(estado)
            pygame.event.pump()
            movida = ia_elegir(estado, ALTURA_IA)
            print(f"IA (O) -> {movida}")

        estado = get_resultado(estado, movida)


if __name__ == "__main__":
    main()