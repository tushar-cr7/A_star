from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import math

# A3 landscape
PAGE_W, PAGE_H = landscape(A3)

# Color palette
BG_DARK    = colors.HexColor('#0a0e1a')
BG_MID     = colors.HexColor('#0f1629')
ACCENT1    = colors.HexColor('#00d4ff')   # cyan
ACCENT2    = colors.HexColor('#7c3aed')   # purple
ACCENT3    = colors.HexColor('#10b981')   # green
GOLD       = colors.HexColor('#f59e0b')   # amber
RED        = colors.HexColor('#ef4444')
WHITE      = colors.white
GRAY_LIGHT = colors.HexColor('#94a3b8')
GRAY_DIM   = colors.HexColor('#334155')
PANEL_BG   = colors.HexColor('#111827')
PANEL_BDR  = colors.HexColor('#1e3a5f')

def rounded_rect(c, x, y, w, h, r, fill_color=None, stroke_color=None, lw=1):
    c.saveState()
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(lw)
    p = c.beginPath()
    p.moveTo(x+r, y)
    p.lineTo(x+w-r, y)
    p.arcTo(x+w-2*r, y, x+w, y+2*r, -90, 90)
    p.lineTo(x+w, y+h-r)
    p.arcTo(x+w-2*r, y+h-2*r, x+w, y+h, 0, 90)
    p.lineTo(x+r, y+h)
    p.arcTo(x, y+h-2*r, x+2*r, y+h, 90, 90)
    p.lineTo(x, y+r)
    p.arcTo(x, y, x+2*r, y+2*r, 180, 90)
    p.close()
    if fill_color and stroke_color:
        c.drawPath(p, fill=1, stroke=1)
    elif fill_color:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke_color:
        c.drawPath(p, fill=0, stroke=1)
    c.restoreState()

def label_tag(c, x, y, text, bg, fg=WHITE, fs=7):
    c.saveState()
    tw = c.stringWidth(text, 'Helvetica-Bold', fs)
    pad = 4
    rounded_rect(c, x, y-1, tw+pad*2, fs+4, 2, fill_color=bg)
    c.setFillColor(fg)
    c.setFont('Helvetica-Bold', fs)
    c.drawString(x+pad, y+1, text)
    c.restoreState()

def draw_grid_demo(c, gx, gy, gw, gh):
    """Draw a mini A* grid simulation."""
    cols, rows = 18, 9
    cw = gw / cols
    ch = gh / rows

    # Define grid: 0=empty, 1=wall, 2=closed, 3=open, 4=path, 5=start, 6=goal
    grid = [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,5,4,4,0,2,2,0,0,0,0,0,0,0,0,0,0,0],
        [0,2,0,4,4,4,2,2,0,0,0,0,0,0,0,0,0,0],
        [0,2,1,1,1,0,4,2,2,2,0,0,0,0,0,0,0,0],
        [0,2,2,0,1,0,0,4,4,2,2,3,3,0,0,0,0,0],
        [0,0,2,0,1,1,0,0,4,4,4,4,2,3,3,0,0,0],
        [0,0,0,0,0,1,0,0,0,0,4,4,4,4,2,6,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]

    color_map = {
        0: colors.HexColor('#1a2035'),  # unvisited
        1: colors.HexColor('#374151'),  # wall
        2: colors.HexColor('#1e3a5f'),  # closed
        3: colors.HexColor('#065f46'),  # open
        4: colors.HexColor('#00d4ff'),  # path
        5: colors.HexColor('#10b981'),  # start
        6: colors.HexColor('#f59e0b'),  # goal
    }

    for r in range(rows):
        for col in range(cols):
            val = grid[r][col]
            cx = gx + col * cw
            cy = gy + gh - (r+1)*ch
            pad = 1
            c.setFillColor(color_map[val])
            c.setStrokeColor(colors.HexColor('#0a0e1a'))
            c.setLineWidth(0.5)
            c.rect(cx+pad, cy+pad, cw-pad*2, ch-pad*2, fill=1, stroke=0)
            # Labels
            if val == 5:
                c.setFillColor(WHITE)
                c.setFont('Helvetica-Bold', 7)
                c.drawCentredString(cx+cw/2, cy+ch/2-3, 'S')
            elif val == 6:
                c.setFillColor(BG_DARK)
                c.setFont('Helvetica-Bold', 7)
                c.drawCentredString(cx+cw/2, cy+ch/2-3, 'E')

    # Legend
    legend = [
        (colors.HexColor('#10b981'), 'Start (S)'),
        (colors.HexColor('#f59e0b'), 'Goal (E)'),
        (colors.HexColor('#00d4ff'), 'Optimal Path'),
        (colors.HexColor('#1e3a5f'), 'Closed List'),
        (colors.HexColor('#065f46'), 'Open List'),
        (colors.HexColor('#374151'), 'Wall / Obstacle'),
        (colors.HexColor('#1a2035'), 'Unvisited'),
    ]
    lx = gx
    ly = gy - 14
    for col, lbl in legend:
        c.setFillColor(col)
        c.rect(lx, ly+1, 9, 9, fill=1, stroke=0)
        c.setFillColor(GRAY_LIGHT)
        c.setFont('Helvetica', 7)
        c.drawString(lx+11, ly+2, lbl)
        lx += c.stringWidth(lbl, 'Helvetica', 7) + 26


def make_poster(filename):
    c = canvas.Canvas(filename, pagesize=landscape(A3))
    W, H = PAGE_W, PAGE_H

    # === BACKGROUND ===
    c.setFillColor(BG_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Subtle grid dots
    c.setFillColor(colors.HexColor('#111827'))
    for xi in range(0, int(W), 20):
        for yi in range(0, int(H), 20):
            c.circle(xi, yi, 0.5, fill=1, stroke=0)

    # Top accent bar
    c.setFillColor(ACCENT2)
    c.rect(0, H-4, W, 4, fill=1, stroke=0)

    M = 10*mm  # margin
    content_y_top = H - 4  # just below accent bar

    # === HEADER BAND ===
    hh = 52  # header height
    rounded_rect(c, M, H-4-hh-2, W-2*M, hh, 6, fill_color=PANEL_BG, stroke_color=ACCENT2, lw=0.8)

    # Tagline left
    c.setFillColor(GRAY_LIGHT)
    c.setFont('Helvetica', 7)
    tag = 'PATHFINDING · ARTIFICIAL INTELLIGENCE · ALGORITHM VISUALIZATION'
    c.drawString(M+10, H-4-11, tag)

    # Main title
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 28)
    c.drawString(M+10, H-4-36, 'A* SEARCH ALGORITHM')

    # Subtitle below title
    c.setFillColor(ACCENT1)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(M+10, H-4-48, 'Visualizer & Interactive Demo')

    # Cost function formula - center area of header
    fx = W//2 - 60
    fy = H - 4 - 46
    c.setFillColor(ACCENT1)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(fx, fy+30, 'COST FUNCTION')
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(fx, fy+16, 'f(n) = g(n) + h(n)')
    c.setFont('Helvetica', 6.5)
    c.setFillColor(GRAY_LIGHT)
    c.drawString(fx, fy+4, 'Total cost  =  Cost from start  +  Heuristic to goal')

    # Tags row
    tags = ['Real-time pathfinding','Heuristic comparison','Obstacle grid navigation','Step-by-step exploration']
    tx = M + 10
    for t in tags:
        label_tag(c, tx, H-4-52, t, ACCENT2, WHITE, 7)
        tx += c.stringWidth(t, 'Helvetica-Bold', 7) + 20

    # === LAYOUT: 3 columns ===
    col_gap = 6*mm
    usable_w = W - 2*M
    # Reserve bottom for info box (36px) + grid (120px)
    grid_h = 115
    grid_y = 52  # above info box
    info_box_h = 42
    body_top = H - 4 - hh - col_gap
    body_bot = grid_y + grid_h + col_gap
    body_h = body_top - body_bot

    col_w = (usable_w - 2*col_gap) / 3
    col1_x = M
    col2_x = col1_x + col_w + col_gap
    col3_x = col2_x + col_w + col_gap

    panel_pad = 8
    panel_inner_w = col_w - 2*panel_pad

    def panel(px, py, pw, ph, title, title_color=ACCENT1):
        rounded_rect(c, px, py, pw, ph, 5, fill_color=PANEL_BG, stroke_color=PANEL_BDR, lw=0.6)
        c.setFillColor(title_color)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(px+panel_pad, py+ph-14, title)
        # underline
        tw = c.stringWidth(title, 'Helvetica-Bold', 8)
        c.setStrokeColor(title_color)
        c.setLineWidth(0.8)
        c.line(px+panel_pad, py+ph-16, px+panel_pad+tw, py+ph-16)
        return py+ph-20  # content start y

    def para_lines(c, lines, x, y, w, fs=7.5, lh=11, color=GRAY_LIGHT, bold_first=False):
        for i, line in enumerate(lines):
            if y < 20: break
            c.setFillColor(color)
            font = 'Helvetica-Bold' if (bold_first and i==0) else 'Helvetica'
            c.setFont(font, fs)
            # simple word wrap
            words = line.split()
            cur = ''
            for word in words:
                test = cur + (' ' if cur else '') + word
                if c.stringWidth(test, font, fs) <= w:
                    cur = test
                else:
                    c.drawString(x, y, cur)
                    y -= lh
                    cur = word
            if cur:
                c.drawString(x, y, cur)
                y -= lh
        return y

    def bullet_lines(c, items, x, y, w, fs=7.5, lh=11):
        for item in items:
            if y < 20: break
            c.setFillColor(ACCENT1)
            c.setFont('Helvetica-Bold', 8)
            c.drawString(x, y, '■')
            c.setFillColor(GRAY_LIGHT)
            c.setFont('Helvetica', fs)
            bx = x+10
            bw = w-10
            words = item.split()
            cur = ''
            first = True
            for word in words:
                test = cur+(' ' if cur else '')+word
                if c.stringWidth(test, 'Helvetica', fs) <= bw:
                    cur = test
                else:
                    c.drawString(bx, y, cur)
                    y -= lh
                    cur = word
                    first = False
            if cur:
                c.drawString(bx, y, cur)
                y -= lh
        return y

    # ============================================================
    # COLUMN 1
    # ============================================================
    cy = body_top

    # WHAT IS A*?
    ph1 = 90
    py = cy - ph1
    ty = panel(col1_x, py, col_w, ph1, 'WHAT IS A* ?', ACCENT1)
    lines1 = [
        'A* (pronounced "A-star") is a best-first graph search algorithm that finds the shortest path between two nodes.',
        'Introduced by Hart, Nilsson & Raphael (1968), it is complete and optimal — guaranteed to find the shortest path if one exists.',
        'Unlike Dijkstra (which explores uniformly outward), A* uses a heuristic h(n) to guide search toward the goal, dramatically reducing nodes explored.',
    ]
    para_lines(c, lines1, col1_x+panel_pad, ty-2, panel_inner_w, 7.5, 10.5)
    cy = py - col_gap

    # ALGORITHM STEPS
    ph2 = 138
    py = cy - ph2
    ty = panel(col1_x, py, col_w, ph2, 'ALGORITHM STEPS', GOLD)
    steps = [
        '1. Add start node to Open List with g = 0',
        '2. Pick node with lowest f(n) from Open List',
        '3. If it\'s the goal → trace path and stop',
        '4. Move current node to Closed List',
        '5. For each neighbor: skip if wall or closed',
        '6. Compute g\' = g(current) + 1',
        '7. If g\' < g(neighbor), update g, h, f, parent',
        '8. Add/update neighbor in Open List',
        '9. Repeat from step 2',
    ]
    ty2 = ty - 2
    for step in steps:
        c.setFillColor(WHITE)
        c.setFont('Helvetica', 7.5)
        c.drawString(col1_x+panel_pad, ty2, step)
        ty2 -= 11
    cy = py - col_gap

    # COMPLEXITY
    ph3 = body_bot + col_gap - py + ph2 + col_gap
    ph3 = py - col_gap - body_bot
    py2 = body_bot
    ph3 = cy - body_bot
    py = body_bot
    ty = panel(col1_x, py, col_w, ph3, 'COMPLEXITY', RED)
    comp = [
        ('Time', 'O(b^d)', 'b = branch factor, d = depth'),
        ('Space', 'O(b^d)', 'All nodes stored in memory'),
        ('Best', 'O(d)', 'Perfect heuristic h = h*'),
        ('Worst', 'O(b^d)', 'h(n) = 0, Dijkstra mode'),
    ]
    cy2 = ty - 4
    for label, val, note in comp:
        c.setFillColor(ACCENT1)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(col1_x+panel_pad, cy2, label)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(col1_x+panel_pad+40, cy2, val)
        c.setFillColor(GRAY_LIGHT)
        c.setFont('Helvetica', 7)
        c.drawString(col1_x+panel_pad, cy2-9, note)
        cy2 -= 22
    # badges
    cy3 = cy2 - 4
    for badge, bc in [('Complete', ACCENT3), ('Optimal', ACCENT2), ('Admissible h(n) required', GOLD)]:
        label_tag(c, col1_x+panel_pad, cy3, badge, bc, WHITE, 7)
        cy3 -= 16

    # ============================================================
    # COLUMN 2
    # ============================================================
    cy = body_top

    # OPEN & CLOSED LISTS
    ph = 118
    py = cy - ph
    ty = panel(col2_x, py, col_w, ph, 'OPEN & CLOSED LISTS', ACCENT1)
    items = [
        'Open List holds discovered nodes not yet fully processed. Sorted ascending by f(n).',
        'The node with lowest f(n) is always chosen next — the "best-first" strategy.',
        'Closed List holds fully explored nodes whose optimal cost g(n) is confirmed.',
        'Nodes in Closed List are never re-expanded, guaranteeing efficiency and no cycles.',
        'If Open List empties without reaching the goal, no valid path exists in the graph.',
    ]
    bullet_lines(c, items, col2_x+panel_pad, ty-2, panel_inner_w)
    cy = py - col_gap

    # HEURISTIC FUNCTIONS
    ph = 135
    py = cy - ph
    ty = panel(col2_x, py, col_w, ph, 'HEURISTIC FUNCTIONS', ACCENT2)
    items2 = [
        'h(n) must be admissible — never overestimate the true cost. This guarantees optimality.',
        'Manhattan: h = |dx| + |dy| — best for 4-directional grid movement.',
        'Euclidean: h = sqrt(dx2 + dy2) — best for any-angle movement.',
        'Chebyshev: h = max(|dx|, |dy|) — best for 8-directional grid movement.',
        'h(n) = 0 reduces A* to Dijkstra\'s algorithm (exhaustive, always optimal but slower).',
    ]
    bullet_lines(c, items2, col2_x+panel_pad, ty-2, panel_inner_w)
    cy = py - col_gap

    # APPLICATIONS
    ph = cy - body_bot
    py = body_bot
    ty = panel(col2_x, py, col_w, ph, 'APPLICATIONS', ACCENT3)
    apps = [
        ('GPS Navigation', 'Google Maps, Waze, TomTom use A* for fastest driving routes.'),
        ('Game AI', 'NPC movement in Warcraft, StarCraft, The Sims — real-time game AI.'),
        ('Robotics', 'Autonomous drones and warehouse robots for obstacle-free navigation.'),
        ('Bioinformatics', 'Protein folding path search and genome sequence alignment.'),
    ]
    ay = ty - 4
    for app_title, app_desc in apps:
        if ay < body_bot+10: break
        c.setFillColor(ACCENT3)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(col2_x+panel_pad, ay, '▸ ' + app_title)
        ay -= 11
        c.setFillColor(GRAY_LIGHT)
        c.setFont('Helvetica', 7.5)
        words = app_desc.split()
        cur = ''
        for word in words:
            test = cur+(' ' if cur else '')+word
            if c.stringWidth(test, 'Helvetica', 7.5) <= panel_inner_w-4:
                cur = test
            else:
                c.drawString(col2_x+panel_pad+4, ay, cur)
                ay -= 10
                cur = word
        if cur:
            c.drawString(col2_x+panel_pad+4, ay, cur)
            ay -= 12

    # ============================================================
    # COLUMN 3
    # ============================================================
    cy = body_top

    # PSEUDOCODE
    ph = 210
    py = cy - ph
    ty = panel(col3_x, py, col_w, ph, 'PSEUDOCODE — A* Algorithm', GOLD)

    code_lines = [
        'function A_Star(start, goal):',
        '  openList = {start}',
        '  closedList = {}',
        '  start.g = 0',
        '  start.h = heuristic(start, goal)',
        '  start.f = start.g + start.h',
        '',
        '  while openList is not empty:',
        '    current = node with lowest f(n)',
        '    if current == goal:',
        '      return reconstruct_path(current)',
        '    move current to closedList',
        '',
        '    for each neighbor of current:',
        '      if neighbor in closedList or',
        '         is_wall: continue',
        '      tentative_g = current.g + 1',
        '      if tentative_g < neighbor.g:',
        '        neighbor.parent = current',
        '        neighbor.g = tentative_g',
        '        neighbor.h = heuristic(...)',
        '        neighbor.f = g + h',
        '        if neighbor not in openList:',
        '          openList.add(neighbor)',
        '',
        '  return None  # no path found',
    ]

    # Code background
    rounded_rect(c, col3_x+panel_pad, ty-len(code_lines)*10-2, panel_inner_w, len(code_lines)*10+6, 3,
                 fill_color=colors.HexColor('#0d1117'))
    cy3 = ty - 4
    for line in code_lines:
        c.setFont('Courier', 7)
        if line.startswith('function') or line.startswith('  while') or line.startswith('    for'):
            c.setFillColor(ACCENT2)
        elif line.strip().startswith('#') or line.strip().startswith('return'):
            c.setFillColor(ACCENT3)
        elif line.strip().startswith('if') or 'move' in line:
            c.setFillColor(GOLD)
        else:
            c.setFillColor(colors.HexColor('#e2e8f0'))
        c.drawString(col3_x+panel_pad+4, cy3, line)
        cy3 -= 10
    cy = py - col_gap

    # ALGORITHM COMPARISON
    ph = cy - body_bot
    py = body_bot
    ty = panel(col3_x, py, col_w, ph, 'ALGORITHM COMPARISON', ACCENT2)

    # Table header
    headers = ['Algorithm', 'Optimal', 'Complete', 'Speed']
    col_widths = [panel_inner_w*0.38, panel_inner_w*0.18, panel_inner_w*0.22, panel_inner_w*0.22]
    row_h = 16
    tx_start = col3_x + panel_pad
    header_y = ty - 4

    # Header background
    rounded_rect(c, tx_start-2, header_y-2, panel_inner_w+4, row_h, 3,
                 fill_color=colors.HexColor('#1e2d47'))
    hx = tx_start
    for i, (hdr, cw) in enumerate(zip(headers, col_widths)):
        c.setFillColor(ACCENT1)
        c.setFont('Helvetica-Bold', 7.5)
        c.drawString(hx+2, header_y+4, hdr)
        hx += cw

    rows = [
        ('A* Search', '✓ Yes', '✓ Yes', '★★★★'),
        ("Dijkstra's", '✓ Yes', '✓ Yes', '★★★☆'),
        ('Greedy BFS', '✗ No', '✗ No', '★★★★'),
        ('BFS', '✓ Yes', '✓ Yes', '★★☆☆'),
        ('DFS', '✗ No', '✗ No', '★★★☆'),
    ]
    row_y = header_y - row_h
    for ri, row in enumerate(rows):
        if row_y < body_bot + 5: break
        bg = colors.HexColor('#131f35') if ri % 2 == 0 else colors.HexColor('#0f1829')
        rounded_rect(c, tx_start-2, row_y-2, panel_inner_w+4, row_h, 2, fill_color=bg)
        rx = tx_start
        for ci, (val, cw) in enumerate(zip(row, col_widths)):
            if ci == 0:
                c.setFillColor(WHITE)
                c.setFont('Helvetica-Bold', 7.5)
            elif '✓' in val:
                c.setFillColor(ACCENT3)
                c.setFont('Helvetica', 7.5)
            elif '✗' in val:
                c.setFillColor(RED)
                c.setFont('Helvetica', 7.5)
            elif '★' in val:
                c.setFillColor(GOLD)
                c.setFont('Helvetica', 7.5)
            else:
                c.setFillColor(GRAY_LIGHT)
                c.setFont('Helvetica', 7.5)
            c.drawString(rx+2, row_y+3, val)
            rx += cw
        row_y -= row_h

    # ============================================================
    # GRID SIMULATION — full width below columns
    # ============================================================
    grid_panel_h = grid_h + col_gap + 20
    grid_panel_y = info_box_h + 6  # just above info box
    grid_pw = W - 2*M

    rounded_rect(c, M, grid_panel_y, grid_pw, grid_panel_h, 5,
                 fill_color=PANEL_BG, stroke_color=PANEL_BDR, lw=0.6)
    c.setFillColor(ACCENT3)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(M+panel_pad, grid_panel_y+grid_panel_h-13, 'GRID SIMULATION — Sample A* Pathfinding Run')
    tw2 = c.stringWidth('GRID SIMULATION — Sample A* Pathfinding Run', 'Helvetica-Bold', 8)
    c.setStrokeColor(ACCENT3)
    c.setLineWidth(0.8)
    c.line(M+panel_pad, grid_panel_y+grid_panel_h-15, M+panel_pad+tw2, grid_panel_y+grid_panel_h-15)

    draw_grid_demo(c,
                   M+panel_pad,
                   grid_panel_y+8,
                   grid_pw - 2*panel_pad,
                   grid_panel_h - 28)

    # ============================================================
    # COURSE INFO BOX — bottom
    # ============================================================
    box_h = info_box_h
    box_y = 4
    box_w = W - 2*M

    # Gradient-style box with accent border
    rounded_rect(c, M, box_y, box_w, box_h, 6,
                 fill_color=colors.HexColor('#0f1a35'),
                 stroke_color=ACCENT1, lw=1.5)

    # Left accent line
    c.setFillColor(ACCENT1)
    c.rect(M+4, box_y+6, 3, box_h-12, fill=1, stroke=0)

    # Course info text - centered
    cx_box = M + box_w/2
    cy_box = box_y + box_h/2

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(cx_box, cy_box+8, 'Artificial Intelligence')

    c.setFillColor(ACCENT1)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(cx_box, cy_box-6, '21CSC206T')

    c.setFillColor(GRAY_LIGHT)
    c.setFont('Helvetica', 9)
    c.drawCentredString(cx_box, cy_box-19, 'Faculty Name — Dr. Anita M.')

    # Decorative dots
    for dx in [-box_w*0.3, box_w*0.3]:
        c.setFillColor(ACCENT2)
        c.circle(cx_box+dx, cy_box, 3, fill=1, stroke=0)

    # ============================================================
    # CREATORS strip — far right of header, just names
    # ============================================================
    creators = ['Tushar Joshi', 'Aryan Dwivedi', 'Krish Gulati']
    # Stack names vertically at top-right corner
    crx = W - M - 10
    cry_start = H - 4 - 14
    c.setFillColor(GRAY_LIGHT)
    c.setFont('Helvetica', 7)
    for i, name in enumerate(creators):
        tw = c.stringWidth(name, 'Helvetica', 7)
        c.drawString(crx - tw, cry_start - i*11, name)

    c.save()

make_poster('/mnt/user-data/outputs/astar_poster_A3.pdf')
print("Done!")
