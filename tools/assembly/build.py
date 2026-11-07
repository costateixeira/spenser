#!/usr/bin/env python3
"""Draw the assembly guide from the real STL files.

    python tools/assembly/build.py            # every sheet, into input/images/
    python tools/assembly/build.py 08 09      # just those

Standard library only. The sheets carry no words, so one set serves every
language: the captions live on the translated pages.

Positions below come from measuring the parts, in the body's own coordinates
(millimetres, x across, y from the tray towards the tower, z up):

  servo axis      x 92, y 29.3   the keyhole in the servo box
  arm             41 mm between its holes, flat side down, on top of the pusher
  pusher          ribs down, slot towards the front; the pin rides in the slot
  rest and push   38.5 degrees either side of straight across, which is the
                  77 degree default anglePush in the firmware
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lineart import (Camera, Drawing, IDENTITY, box, cylinder, load_stl, mesh_of, path_data,
                     rotate_x, rotate_y, rotate_z)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
IMAGES = os.path.join(ROOT, 'input', 'images')
INK = '#111111'
LIGHT = '#8a8a8a'

BODY = load_stl(os.path.join(IMAGES, 'spenser-body.stl'))
PUSHER = load_stl(os.path.join(IMAGES, 'spenser-pusher.stl'))
ARM = load_stl(os.path.join(IMAGES, 'spenser-arm.stl'))
PIN = load_stl(os.path.join(IMAGES, 'spenser-pin.stl'))

AXIS = (92.0, 29.3)
SWING = 38.5
ARM_LENGTH = 41.0
ARM_Z = 7.05
FLOOR = 1.5


def pin_xy(phi):
    return (AXIS[0] - ARM_LENGTH * math.cos(math.radians(phi)),
            AXIS[1] - ARM_LENGTH * math.sin(math.radians(phi)))


# ---------------------------------------------------- parts we do not print

def servo_mesh():
    """An SG90, in body coordinates once seated: output side down, ears on the ledge."""
    x0, x1, y0, y1 = 85.85, 97.85, 23.5, 46.7
    return mesh_of(
        box(x0, x1, y0, y1, 19.3, 41.0),                # case
        box(x0, x1, 18.2, 51.4, 23.1, 25.6),            # ears
        cylinder(AXIS[0] - 0.15, AXIS[1], 17.6, 19.3, 5.9),   # gear boss
        cylinder(AXIS[0] - 0.15, 36.0, 17.6, 19.3, 2.8),      # second boss
        cylinder(AXIS[0] - 0.15, AXIS[1], 14.2, 17.6, 2.4),   # spline
        box(89.9, 93.8, 46.7, 48.2, 28.0, 30.0),        # cable exit
    )


def horn_mesh():
    """A one-arm horn around its shaft, at the origin, pointing along -x."""
    return mesh_of(cylinder(0, 0, 0, 3.8, 3.4), box(-15.5, 0, -2.0, 2.0, 2.3, 3.8), cylinder(-15.5, 0, 2.3, 3.8, 2.0))


def screw_mesh(length=8.0):
    """A self-tapping screw with its point at the origin, head upwards: a pointed
    tip, threads along the shank, and a pan head with a cross in it."""
    shapes = [cylinder(0, 0, 0.0, 0.6, 0.35, 10), cylinder(0, 0, 0.6, length, 0.75, 12),
              cylinder(0, 0, length, length + 1.4, 1.9, 20)]
    z = 1.0
    while z < length - 0.6:
        shapes.append(cylinder(0, 0, z, z + 0.35, 1.05, 12))
        z += 0.9
    shapes.append(box(-1.3, 1.3, -0.22, 0.22, length + 1.15, length + 1.42))
    shapes.append(box(-0.22, 0.22, -1.3, 1.3, length + 1.15, length + 1.42))
    return mesh_of(*shapes)


def driver_mesh():
    """A small screwdriver with its tip at the origin, handle upwards."""
    return mesh_of(cylinder(0, 0, 0, 34, 1.4, 12), cylinder(0, 0, 34, 66, 5.0, 24))


# The two M5Stack modules, from M5Stack's dimension drawings. They stand upright,
# as they do in the bay: the base's back against the slot, its battery and
# the Atom facing the tray (-y), the battery end down and the Atom at the top.
# Local origin: the base's back face, lower left corner, above the tab.

BASE_BODY = 10.4      # the base without its battery
BASE_DEPTH = 20.7     # with it, by M5Stack's drawing
BATTERY_AXIS = 17.0   # the cell's axis, from the base's back
BASE_LENGTH = 72.0
ATOM = 9.5            # Atom S3 Lite: 24 x 24 x 9.5
HEADERS = (12.0, 21.0, 30.0, 39.0)   # servo headers S1-S4, up the side facing the servos


def motion_base_mesh(x=0.0, y=0.0, z=0.0):
    """Atomic Motion Base v1.1: 24 x 72 x 20.7, with its battery and its four servo headers."""
    shapes = [
        box(x, x + 24, y - BASE_BODY, y, z, z + BASE_LENGTH),
        # The 18350 cell, 18 x 35, lying along the base in its holder and standing
        # well proud of it.
        cylinder(x + 12, y - BATTERY_AXIS, z + 7, z + 42, 9, 36),
        box(x + 5, x + 19, y - BATTERY_AXIS - 5, y - BASE_BODY, z + 3.5, z + 7),     # holder, lower end
        box(x + 5, x + 19, y - BATTERY_AXIS - 5, y - BASE_BODY, z + 42, z + 45.5),   # holder, upper end
        box(x + 9, x + 15, y - 3, y, z - 3.4, z),                               # the tab with its hole
        box(x - 1.4, x, y - 7.5, y - 4.5, z + 61, z + 66),                      # power switch
    ]
    for h in HEADERS:
        shapes.append(box(x + 24, x + 26.5, y - 7.2, y - 2.4, z + h, z + h + 7.6))
        for pin in (1.27, 3.81, 6.35):
            shapes.append(box(x + 26.5, x + 32, y - 5.1, y - 4.5, z + h + pin - 0.3, z + h + pin + 0.3))
    return mesh_of(*shapes)


def atom_mesh(x=0.0, y=0.0, z=0.0):
    """Atom S3 Lite on the base's upper end: its face is the button, its USB-C port points up."""
    front = y - BASE_BODY - ATOM
    return mesh_of(
        box(x, x + 24, front, y - BASE_BODY, z + 47.5, z + 71.5),
        box(x + 3.5, x + 20.5, front - 0.5, front, z + 51, z + 68),         # the button
        box(x + 17.5, x + 19.5, front - 0.8, front - 0.5, z + 64.5, z + 66.5),   # LED window
        box(x + 7.5, x + 16.5, front + 2.6, front + 6.2, z + 71.5, z + 72),  # USB-C port
    )


def servo_plug_mesh(x, y, z):
    """The SG90's black three-way plug, pushed onto a header whose lowest pin is at z."""
    return mesh_of(box(x + 26.8, x + 41.0, y - 6.2, y - 3.4, z - 0.4, z + 8.0),
                   box(x + 41.0, x + 43.0, y - 5.6, y - 4.0, z + 0.6, z + 7.0))


def rounded_slab(x0, y0, z0, w, l, h, r, segments=8):
    """A rectangular slab with rounded corners in plan."""
    corners = ((x0 + w - r, y0 + l - r, 0), (x0 + r, y0 + l - r, 90), (x0 + r, y0 + r, 180), (x0 + w - r, y0 + r, 270))
    outline = []
    for cx, cy, start in corners:
        for i in range(segments + 1):
            a = math.radians(start + 90 * i / segments)
            outline.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    cx, cy = x0 + w / 2, y0 + l / 2
    triangles = []
    for (ax, ay), (bx, by) in zip(outline, outline[1:] + outline[:1]):
        triangles.append([(cx, cy, z0 + h), (ax, ay, z0 + h), (bx, by, z0 + h)])
        triangles.append([(cx, cy, z0), (bx, by, z0), (ax, ay, z0)])
        triangles.append([(ax, ay, z0), (bx, by, z0), (bx, by, z0 + h)])
        triangles.append([(ax, ay, z0), (bx, by, z0 + h), (ax, ay, z0 + h)])
    return triangles


def powerbank_mesh():
    """A USB power bank: rounded slab, a USB-C port at one end, four charge lights and a button."""
    shapes = [rounded_slab(0, 0, 0, 66, 100, 16, 9),
              box(28.5, 37.5, 99.6, 100.0, 6.5, 9.5)]           # USB-C port, on the far end
    for i in range(4):
        shapes.append(box(24 + i * 5, 26 + i * 5, 6, 8, 16, 16.4))
    shapes.append(cylinder(50, 7, 16, 16.6, 2.6, 16))
    return mesh_of(*shapes)


def usbc_plug_mesh():
    """A USB-C plug pointing along +z, its tip at the origin."""
    return mesh_of(box(-4.2, 4.2, -1.3, 1.3, 0, 6.5), box(-5.5, 5.5, -3.0, 3.0, 6.5, 22))


def frustum(x0, x1, y0, y1, z0, z1, bevel):
    """A box whose top is smaller than its base by bevel all round."""
    p = [(x + (bevel if z == z1 else 0) * (1 if x == x0 else -1),
          y + (bevel if z == z1 else 0) * (1 if y == y0 else -1), z)
         for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return [[p[a], p[b], p[c]] for a, b, c, d in quads] + [[p[a], p[c], p[d]] for a, b, c, d in quads]


def chocolate_mesh(t=6.5, columns=3, rows=2):
    """A small bar, 57 x 37: a thin base with bevelled squares on top and
    grooves between them, which is what makes it read as chocolate."""
    w, h, base, gap = 57.0, 37.0, 4.0, 0.7
    shapes = [box(0, w, 0, h, 0, base)]
    cw, ch = (w - gap * (columns + 1)) / columns, (h - gap * (rows + 1)) / rows
    for i in range(columns):
        for j in range(rows):
            x0, y0 = gap + i * (cw + gap), gap + j * (ch + gap)
            shapes.append(frustum(x0, x0 + cw, y0, y0 + ch, base, t, 1.3))
    return mesh_of(*shapes)


# --------------------------------------------------------------- placing parts

def add_body(d, dx=0.0, **kw):
    return d.add(BODY, move=(dx, 0, 0), **kw)


def pusher_placement(phi=SWING, dx=0.0, extra=(0, 0, 0)):
    # 180 degrees about y: ribs down, slot still towards the front.
    y = pin_xy(phi)[1] + 82.075
    return dict(rotation=rotate_y(180), about=(46.85, 0, 3.35),
                move=(21.15 + dx + extra[0], y + extra[1], 0.9 + extra[2]))


def add_pusher(d, phi=SWING, dx=0.0, extra=(0, 0, 0)):
    return d.add(PUSHER, **pusher_placement(phi, dx, extra))


def add_arm(d, phi=SWING, dx=0.0, extra=(0, 0, 0)):
    return d.add(ARM, rotation=rotate_z(phi), about=(-21, -10, 0),
                 move=(AXIS[0] + 21 + dx + extra[0], AXIS[1] + 10 + extra[1], ARM_Z + extra[2]))


def add_pin(d, phi=SWING, dx=0.0, extra=(0, 0, 0)):
    x, y = pin_xy(phi)
    # Upside down from the STL, so the head rests on the arm.
    return d.add(PIN, rotation=rotate_x(180), about=(-12, 79, 0),
                 move=(x + 12 + dx + extra[0], y - 79 + extra[1], ARM_Z + 3.0 + 1.46 + extra[2]))


def add_servo(d, dx=0.0, extra=(0, 0, 0)):
    return d.add(servo_mesh(), move=(dx + extra[0], extra[1], extra[2]))


def add_horn(d, phi=SWING, dx=0.0, extra=(0, 0, 0)):
    # The horn lies in the arm's groove, pointing along the arm.
    return d.add(horn_mesh(), rotation=rotate_z(phi), move=(AXIS[0] + dx + extra[0], AXIS[1] + extra[1], ARM_Z + 1.9 + extra[2]))


def module_origin(dx=0.0, lift=0.0):
    # The bay: 24 wide between x 48 and 72, its floor at z 25, the slot's back at y 57.
    # The base stands on its tab.
    return (48.0 + dx, 57.0, 28.4 + lift)


def add_module(d, dx=0.0, lift=0.0, atom=True, plugs=()):
    x, y, z = module_origin(dx, lift)
    d.add(motion_base_mesh(x, y, z))
    if atom:
        d.add(atom_mesh(x, y, z))
    for number in plugs:
        d.add(servo_plug_mesh(x, y, z + HEADERS[number - 1]))
    return d


def plug_end(number, dx=0.0):
    """Where a servo plug's cable leaves it, in body coordinates."""
    x, y, z = module_origin(dx)
    return (x + 43.0, y - 4.8, z + HEADERS[number - 1] + 3.8)


# ---------------------------------------------------------------- annotations

def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;')


class Sheet:
    def __init__(self, width=800, height=560):
        self.width, self.height = width, height
        self.under = []
        self.over = []

    def lines(self, drawing, target=None):
        """The visible lines of a drawing, as one or more SVG paths."""
        for part, paths in drawing.visible_lines():
            data = path_data(paths)
            if data:
                (target if target is not None else self.under).append(
                    '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>'
                    % (data, LIGHT if part['ghost'] else INK, part['weight']))

    def guide(self, a, b):
        """The dashed line along which a part travels."""
        self.over.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" stroke-dasharray="7 5"/>'
                         % (a[0], a[1], b[0], b[1], INK))

    def arrow(self, a, b, width=9.0, head=20.0):
        """A hollow block arrow from a to b, in screen coordinates."""
        length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = -uy, ux
        neck = (b[0] - ux * head, b[1] - uy * head)
        pts = [(a[0] + nx * width / 2, a[1] + ny * width / 2),
               (neck[0] + nx * width / 2, neck[1] + ny * width / 2),
               (neck[0] + nx * head * 0.75, neck[1] + ny * head * 0.75),
               b,
               (neck[0] - nx * head * 0.75, neck[1] - ny * head * 0.75),
               (neck[0] - nx * width / 2, neck[1] - ny * width / 2),
               (a[0] - nx * width / 2, a[1] - ny * width / 2)]
        self.over.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="2" stroke-linejoin="round"/>'
                         % (' '.join('%.1f,%.1f' % p for p in pts), INK))

    def turn(self, cx, cy, r=24, start=-150, end=120):
        """A curved arrow, for turning something."""
        a0, a1 = math.radians(start), math.radians(end)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if abs(end - start) > 180 else 0
        self.over.append('<path d="M%.1f %.1f A%d %d 0 %d 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="4"/>'
                         % (x0, y0, r, r, large, x1, y1, INK))
        tx, ty = -math.sin(a1), math.cos(a1)
        nx, ny = -ty, tx
        tip = (x1 + tx * 12, y1 + ty * 12)
        self.over.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                         % (tip[0], tip[1], x1 + nx * 8, y1 + ny * 8, x1 - nx * 8, y1 - ny * 8, INK))

    def text(self, x, y, value, size=30, anchor='start', weight='700'):
        self.over.append('<text x="%.1f" y="%.1f" font-family="Helvetica, Arial, sans-serif" font-size="%d" font-weight="%s" '
                         'text-anchor="%s" fill="%s">%s</text>' % (x, y, size, weight, anchor, INK, esc(value)))

    def count(self, x, y, n):
        """The '2x' mark."""
        self.text(x, y, '%dx' % n)

    def number(self, x, y, n, r=15):
        self.over.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (x, y, r, INK))
        self.text(x, y + r * 0.42, str(n), int(r * 1.2), 'middle')

    def power(self, x, y, r=24):
        """The usual power symbol: a broken ring with a bar through the gap."""
        a = math.radians(50)
        self.over.append('<path d="M%.1f %.1f A%d %d 0 1 0 %.1f %.1f M%.1f %.1f V%.1f" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
                         % (x + r * math.sin(a), y - r * math.cos(a), r, r, x - r * math.sin(a), y - r * math.cos(a), x, y - r - 5, y - 2, INK))

    def mark_wrong(self, x, y, size=46):
        self.over.append('<path d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="7" stroke-linecap="round"/>'
                         % (x - size, y - size, x + size, y + size, x + size, y - size, x - size, y + size, INK))

    def mark_right(self, x, y, size=26):
        self.over.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
                         % (x - size, y, x - size * 0.2, y + size * 0.8, x + size, y - size, INK))

    def inset(self, cx, cy, r, drawing, pointer=None):
        """A magnified view in a circle, with a line to what it magnifies."""
        paths = []
        self.lines(drawing, paths)
        if pointer:
            self.over.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4"/>'
                             % (pointer[0], pointer[1], cx, cy, INK))
            self.over.append('<circle cx="%.1f" cy="%.1f" r="9" fill="none" stroke="%s" stroke-width="1.6"/>' % (pointer[0], pointer[1], INK))
        clip = 'c%d' % (len(self.over) + 1)
        self.over.append('<clipPath id="%s"><circle cx="%d" cy="%d" r="%d"/></clipPath>' % (clip, r, r, r))
        self.over.append('<g transform="translate(%.1f %.1f)"><circle cx="%d" cy="%d" r="%d" fill="#ffffff" stroke="%s" stroke-width="2.4"/>'
                         '<g clip-path="url(#%s)">%s</g></g>' % (cx - r, cy - r, r, r, r, INK, clip, ''.join(paths)))

    def person(self, x, y, scale=1.0):
        """A plain figure in the manner of flat-pack instructions: head, body, arms
        and legs as one continuous outline drawn with a brush-like line that swells
        and thins, the head turned a little towards the work, with a big nose, two
        dot eyes and a small mouth. One arm is held out; returns where its hand is."""
        k = scale
        hx, hy, hr = 0.0, -57.0, 21.0
        # The head, from the right of the neck up over the top and down to the left,
        # with the nose standing out on the side the figure faces.
        head = []
        for deg in range(65, -246, -11):
            r = hr
            if -19 <= deg <= 25:
                r += 8.5 * math.cos(math.radians((deg - 3) * 4.1)) ** 2
            head.append((hx + r * math.cos(math.radians(deg)), hy + r * math.sin(math.radians(deg))))
        # Clockwise from the left of the neck. A smooth curve runs through every point.
        outline = [
            (-9, -33), (-24, -27), (-33, -14), (-37, 8), (-38, 27), (-34, 34), (-29, 29),
            (-28, 10), (-26, 24), (-25, 46), (-23, 70), (-22, 91), (-31, 95), (-30, 100), (-8, 100),
            (-6, 74), (-3, 50), (3, 50), (6, 74), (8, 100), (30, 100), (31, 95), (22, 91),
            (23, 70), (25, 46), (27, 20), (29, 2), (46, -3), (61, -6), (67, -12), (63, -19),
            (46, -19), (30, -23), (22, -29), (9, -33),
        ] + head
        pts = [(x + px * k, y + py * k) for px, py in outline]
        n = len(pts)

        # Sample the closed Catmull-Rom curve, for the fill and for the brush line.
        curve = []
        for m in range(n):
            p0, p1, p2, p3 = pts[m - 1], pts[m], pts[(m + 1) % n], pts[(m + 2) % n]
            for step in range(8):
                t = step / 8.0
                t2, t3 = t * t, t * t * t
                curve.append(tuple(0.5 * (2 * p1[i] + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2
                                          + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3) for i in (0, 1)))
        c = len(curve)
        outer, inner, run = [], [], 0.0
        for m in range(c):
            (ax, ay), (bx, by) = curve[m - 1], curve[(m + 1) % c]
            tx, ty = bx - ax, by - ay
            norm = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / norm, tx / norm
            run += math.hypot(curve[m][0] - curve[m - 1][0], curve[m][1] - curve[m - 1][1])
            # Heavier where the line faces down and to the right, as a pen pressed
            # harder, with a slow wobble along the way.
            w = (1.9 + 1.8 * max(0.0, ny * 0.6 + nx * 0.5) + 0.6 * math.sin(run / (23 * k))) * k / 1.7 * 1.4
            px, py = curve[m]
            outer.append((px + nx * w / 2, py + ny * w / 2))
            inner.append((px - nx * w / 2, py - ny * w / 2))
        loop = lambda ps: 'M' + ' L'.join('%.1f %.1f' % p for p in ps) + 'Z'
        self.over.append('<path d="%s" fill="#ffffff"/>' % loop(curve))
        self.over.append('<path d="%s %s" fill="%s" fill-rule="evenodd"/>' % (loop(outer), loop(inner), INK))

        # The face, looking towards the outstretched hand.
        # Three-quarter view: the eyes sit above the nose and towards it, the far
        # eye a little smaller, and the mouth tucked in below the nose.
        for ex, size in ((3.0, 0.85), (12.5, 1.0)):
            self.over.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
                             % (x + ex * k, y - 64 * k, 1.8 * size * k, 2.5 * size * k, INK))
        self.over.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>'
                         % (x + 6 * k, y - 48 * k, x + 10.5 * k, y - 45.5 * k, x + 15 * k, y - 48.5 * k, INK, 1.6 * k))
        return (x + 64 * k, y - 13 * k)

    def ribbon(self, points, width=7.0):
        """A servo's flat three-wire cable: four edges, drawn as alternating bands."""
        a, c1, c2, b = points
        d = 'M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f' % (a + c1 + c2 + b)
        for colour, w in ((INK, width), ('#ffffff', width - 1.6), (INK, width * 0.46), ('#ffffff', width * 0.46 - 1.4)):
            self.over.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="butt"/>' % (d, colour, w))

    def cable(self, points, width=6.0):
        """A round cable: one outlined tube."""
        a, c1, c2, b = points
        d = 'M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f' % (a + c1 + c2 + b)
        for colour, w in ((INK, width), ('#ffffff', width - 2.6)):
            self.over.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" stroke-linecap="round"/>' % (d, colour, w))

    def label(self, x, y, value, size=15):
        """A small tag on a part, such as the name printed beside a connector."""
        w = 9 + 0.62 * size * len(value)
        self.over.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="#ffffff" stroke="%s" stroke-width="1.6"/>'
                         % (x - w / 2, y - size, w, size * 1.45, INK))
        self.text(x, y + size * 0.1, value, size, 'middle')

    def svg(self, title):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img"><title>%s</title>'
                '<rect width="%d" height="%d" fill="#ffffff"/>%s%s</svg>\n'
                % (self.width, self.height, esc(title), self.width, self.height, ''.join(self.under), ''.join(self.over)))


def scene(az=-32, el=30, width=800, height=560, margin=42):
    return Drawing(Camera(az, el), width, height, margin)


def fit(d, *extra):
    d._fit(extra)
    return d


def screen(d, p):
    return d.to_screen(p)[:2]


# --------------------------------------------------------------------- sheets

def sheet_00():
    """Everything in the box."""
    s = Sheet(800, 600)
    cells = [
        (20, 10, 300, 300, 'body', 2), (330, 10, 200, 150, 'pusher', 2), (540, 10, 240, 150, 'arm', 2),
        (330, 170, 120, 140, 'pin', 2), (460, 170, 150, 140, 'servo', 2), (620, 170, 160, 140, 'horn', 2),
        (20, 330, 105, 190, 'motion', 1), (135, 330, 105, 190, 'atom', 1), (250, 330, 150, 190, 'bank', 1),
        (410, 330, 80, 190, 'screws', 6), (500, 330, 90, 190, 'driver', 1), (600, 330, 180, 150, 'piece', 0),
    ]
    numbers = {'body': 1, 'pusher': 2, 'arm': 3, 'pin': 4, 'servo': 5, 'horn': 6, 'motion': 7, 'atom': 8,
               'bank': 9, 'screws': 10}
    for x, y, w, h, name, n in cells:
        d = Drawing(Camera(-32, 30), w, h - 30, 12)
        if name == 'body':
            d.add(BODY)
        elif name == 'pusher':
            d.add(PUSHER, rotation=rotate_y(180), about=(46.85, 0, 3.35))
        elif name == 'arm':
            d.add(ARM)
        elif name == 'pin':
            d.add(PIN, rotation=rotate_x(180), about=(-12, 79, 4.6))
        elif name == 'servo':
            d.add(servo_mesh(), rotation=rotate_x(180), about=(92, 35, 28))
        elif name == 'horn':
            d.add(horn_mesh(), rotation=rotate_x(180), about=(0, 0, 2))
        elif name == 'motion':
            d.add(motion_base_mesh())
        elif name == 'atom':
            d.add(atom_mesh())
        elif name == 'bank':
            d.add(powerbank_mesh())
        elif name == 'screws':
            d.add(screw_mesh())
        elif name == 'driver':
            d.camera = Camera(-32, 18)
            d.add(driver_mesh())
        elif name == 'piece':
            d.add(chocolate_mesh())
        fit(d)
        lines = []
        s.lines(d, lines)
        s.under.append('<g transform="translate(%d %d)">%s</g>' % (x, y + 30, ''.join(lines)))
        if name in numbers:
            s.number(x + 18, y + 18, numbers[name])
        if n:
            s.text(x + (44 if name in numbers else 0), y + 28, '%dx' % n, 22)
    s.text(600, 505, '≤ 60 × 39 mm', 22)
    s.text(600, 537, '5.5 – 7.5 mm', 22)
    return s


def sheet_01():
    """The servo goes into the box, output side down."""
    s = Sheet()
    d = fit(add_servo(add_body(scene(az=-40, el=38, margin=30)), extra=(0, 0, 48)))
    s.lines(d)
    top = screen(d, (AXIS[0], 32, 56))
    low = screen(d, (AXIS[0], 32, 34))
    s.guide(top, low)
    s.arrow(screen(d, (112, 32, 96)), screen(d, (112, 32, 66)))
    s.count(650, 60, 2)
    return s


def sheet_02():
    """Two screws through the ears."""
    s = Sheet()
    d = scene(az=-40, el=44, margin=30)
    add_servo(add_body(d))
    for y in (20.8, 49.1):
        d.add(screw_mesh(), move=(91.85, y, 62))
    d.add(driver_mesh(), move=(91.85, 49.1, 84))
    fit(d)
    s.lines(d)
    for y in (20.8, 49.1):
        s.guide(screen(d, (91.85, y, 62)), screen(d, (91.85, y, 26)))
    s.turn(*screen(d, (112, 49.1, 118)))
    s.count(650, 60, 2)
    return s


def sheet_03():
    """The Atom presses onto the lower end of the base."""
    s = Sheet()
    d = Drawing(Camera(-38, 22), 800, 560, 70)
    d.add(motion_base_mesh()).add(atom_mesh(y=-34))
    fit(d)
    s.lines(d)
    s.guide(screen(d, (12, -60, 59.5)), screen(d, (12, -22, 59.5)))
    s.arrow(screen(d, (-14, -74, 59.5)), screen(d, (-14, -46, 59.5)))
    s.count(650, 60, 1)
    return s


def sheet_04():
    """Battery end first, the base slides down into the bay of one body, battery towards the tray."""
    s = Sheet()
    d = scene(az=-30, el=24, margin=24)
    add_body(d)
    add_servo(d)
    add_module(d, lift=86)
    fit(d)
    s.lines(d)
    s.guide(screen(d, (60, 52, 110)), screen(d, (60, 52, 78)))
    s.arrow(screen(d, (30, 40, 168)), screen(d, (30, 40, 124)))
    s.count(650, 60, 1)
    return s


def sheet_05():
    """Both bodies side by side; each servo's plug onto its own header."""
    s = Sheet(800, 600)
    d = Drawing(Camera(-24, 30), 800, 600, 30)
    add_servo(add_body(d))
    add_servo(add_body(d, dx=66), dx=66)
    add_module(d, plugs=(3, 4))
    fit(d)
    s.lines(d)
    for number, servo_x in ((4, 91.85), (3, 157.85)):
        a = screen(d, plug_end(number))
        b = screen(d, (servo_x, 48.2, 29))
        s.ribbon((a, (a[0] + 70, a[1] - 30), (b[0] - 10, b[1] - 120), b))
    for number in (4, 3):
        x, y = screen(d, plug_end(number))
        s.label(x + 28, y - 18 if number == 4 else y + 30, 'S%d' % number)

    # Close up: a plug going onto its header, pins and all.
    near = Drawing(Camera(-24, 18), 230, 230, 10)
    x, y, z = module_origin()
    near.add(motion_base_mesh(x, y, z)).add(servo_plug_mesh(x + 12, y, z + HEADERS[2]))
    frame(near, (x + 36, y - 4.8, z + HEADERS[2] + 4), 3.6)
    s.inset(668, 470, 115, near)
    s.arrow((792, 466), (738, 466), width=7, head=14)
    return s


def sheet_06():
    """Power: USB-C into the top of the Atom, base switched on, servos to rest."""
    s = Sheet()
    d = Drawing(Camera(-28, 24), 800, 560, 40)
    add_servo(add_body(d))
    add_module(d)
    d.add(powerbank_mesh(), move=(-58, -112, 0))
    x, y, z = module_origin()
    d.add(usbc_plug_mesh(), move=(x + 12, y - BASE_BODY - ATOM + 4.4, z + 72.2))
    d.add(usbc_plug_mesh(), rotation=rotate_x(-90), move=(-25, -12, 8))
    fit(d)
    s.lines(d)
    a = screen(d, (-25, -12 + 22, 8))
    b = screen(d, (x + 12, y - BASE_BODY - ATOM + 4.4, z + 94.2))
    s.cable((a, (a[0] - 30, a[1] - 260), (b[0] - 10, b[1] - 120), b))
    s.power(680, 64)
    sw = screen(d, (x - 1.4, y - 6, z + 63.5))
    s.arrow((sw[0] - 70, sw[1] - 40), (sw[0] - 8, sw[1] - 4), width=7, head=14)
    return s


def sheet_07():
    """The pusher slides in from the front, ribs down, slot towards you."""
    s = Sheet()
    d = scene(az=-34, el=36, margin=30)
    add_servo(add_body(d))
    add_pusher(d, extra=(0, -72, 0))
    fit(d)
    s.lines(d)
    s.arrow(screen(d, (68, -128, 26)), screen(d, (68, -90, 26)))
    inner = Drawing(Camera(-34, -30), 184, 184, 22)
    inner.add(PUSHER, rotation=rotate_y(180), about=(46.85, 0, 3.35))
    fit(inner)
    s.inset(684, 450, 92, inner)
    s.count(650, 60, 2)
    return s


def frame(drawing, centre, scale):
    """Aim a drawing at a point at a chosen magnification, instead of fitting it."""
    x, y, _ = drawing.camera.project(centre)
    drawing.scale = scale
    drawing.ox = drawing.width / 2 - scale * x
    drawing.oy = drawing.height / 2 - scale * y
    return drawing


def sheet_08():
    """Horn into the arm; the arm slides under the box onto the shaft; screw from underneath."""
    s = Sheet(800, 620)
    d = Drawing(Camera(-34, 36), 800, 620, 30)
    add_servo(add_body(d))
    add_pusher(d)
    lift = (-14, -66, 0)
    add_arm(d, extra=lift)
    add_horn(d, extra=lift)
    fit(d)
    s.lines(d)
    near = screen(d, (AXIS[0] - 14, AXIS[1] - 66, ARM_Z + 6))
    far = screen(d, (AXIS[0], AXIS[1], ARM_Z + 6))
    s.guide(near, far)
    s.arrow((near[0] + 54, near[1] - 2), (near[0] + 92, near[1] - 36), width=8, head=16)

    groove = Drawing(Camera(-34, 40), 200, 200, 14)
    groove.add(ARM).add(horn_mesh(), move=(-21, -10, 16))
    fit(groove)
    s.inset(118, 500, 100, groove)

    under = Drawing(Camera(-34, -42), 236, 236, 14)
    under.add(BODY)
    under.add(screw_mesh(), rotation=rotate_x(180), move=(AXIS[0], 29.5, -7))
    under.add(driver_mesh(), rotation=rotate_x(180), move=(AXIS[0], 29.5, -18))
    frame(under, (AXIS[0], 29.5, -20), 3.0)
    s.inset(668, 130, 118, under)
    s.count(60, 60, 2)
    return s


def rest_view(phi):
    d = Drawing(Camera(0, 89.9), 350, 390, 18)
    d.add(BODY)
    add_servo(d)
    add_pusher(d, phi)
    add_arm(d, phi)
    add_horn(d, phi)
    add_pin(d, phi)
    fit(d)
    return d


def sheet_08b():
    """At rest, the arm points towards the front and the tower floor is clear."""
    s = Sheet(800, 430)
    for x, phi, right in ((30, SWING, True), (420, -SWING, False)):
        lines = []
        s.lines(rest_view(phi), lines)
        s.under.append('<g transform="translate(%d 20)">%s</g>' % (x, ''.join(lines)))
        if right:
            s.mark_right(x + 320, 60)
        else:
            s.mark_wrong(x + 320, 60, 26)
    return s


def sheet_09():
    """The pin drops through the arm into the slot."""
    s = Sheet()
    d = Drawing(Camera(-30, 44), 800, 560, 30)
    add_servo(add_body(d))
    add_pusher(d)
    add_arm(d)
    add_horn(d)
    add_pin(d, extra=(0, 0, 40))
    fit(d)
    s.lines(d)
    x, y = pin_xy(SWING)
    s.guide(screen(d, (x, y, 50)), screen(d, (x, y, 12)))
    s.arrow(screen(d, (x - 22, y, 58)), screen(d, (x - 22, y, 34)), width=8, head=16)

    near = Drawing(Camera(-30, 22), 220, 220, 8)
    near.add(PUSHER, **pusher_placement())
    near.add(ARM, rotation=rotate_z(SWING), about=(-21, -10, 0), move=(AXIS[0] + 21, AXIS[1] + 10, ARM_Z))
    near.add(PIN, rotation=rotate_x(180), about=(-12, 79, 0), move=(x + 12, y - 79, ARM_Z + 4.46))
    frame(near, (x, y, 7), 7.5)
    s.inset(668, 142, 110, near)
    s.count(60, 60, 2)
    return s


def sheet_10():
    """Press the button: the pusher travels and a piece leaves through the back."""
    s = Sheet(800, 600)
    d = Drawing(Camera(146, 30), 800, 600, 34)
    add_body(d)
    add_servo(d)
    add_module(d)
    add_pusher(d, phi=-SWING)
    d.add(chocolate_mesh(), move=(38.5, 112, FLOOR))
    fit(d)
    s.lines(d)
    s.arrow(screen(d, (68, 118, 30)), screen(d, (68, 158, 30)))
    return s


def sheet_11():
    """Load from the top; check the level through the rear window."""
    s = Sheet()
    d = scene(az=-32, el=34, margin=26)
    add_body(d)
    add_servo(d)
    add_module(d)
    add_pusher(d)
    add_arm(d)
    add_horn(d)
    add_pin(d)
    for i in range(3):
        d.add(chocolate_mesh(), move=(39.5, 60.5, 112 + i * 22))
    fit(d)
    s.lines(d)
    s.guide(screen(d, (68, 79, 112)), screen(d, (68, 79, 100)))
    s.arrow(screen(d, (120, 79, 172)), screen(d, (120, 79, 126)))
    s.count(60, 60, 2)
    return s


def sheet_12():
    """Finished, and right and wrong for the one thing that goes wrong."""
    s = Sheet(800, 420)
    d = Drawing(Camera(-32, 32), 360, 400, 20)
    add_body(d)
    add_servo(d)
    add_module(d)
    add_pusher(d)
    add_arm(d)
    add_horn(d)
    add_pin(d)
    add_body(d, dx=66)
    add_servo(d, dx=66)
    add_pusher(d, dx=66)
    add_arm(d, dx=66)
    add_horn(d, dx=66)
    add_pin(d, dx=66)
    fit(d)
    lines = []
    s.lines(d, lines)
    s.under.append('<g transform="translate(40 10)">%s</g>' % ''.join(lines))
    piece = Drawing(Camera(-32, 30), 110, 80, 6)
    piece.add(chocolate_mesh())
    fit(piece)
    lines = []
    s.lines(piece, lines)
    hand = s.person(560, 220, 1.7)
    s.over.append('<g transform="translate(%.1f %.1f)">%s</g>' % (hand[0] - 8, hand[1] - 66, ''.join(lines)))
    return s


SHEETS = {
    '00': (sheet_00, 'Parts'), '01': (sheet_01, 'Servo into the box'), '02': (sheet_02, 'Servo screws'),
    '03': (sheet_03, 'Atom onto the motion base'), '04': (sheet_04, 'Module into the bay'),
    '05': (sheet_05, 'Servo cables'), '06': (sheet_06, 'Power on'), '07': (sheet_07, 'Pusher into the channel'),
    '08': (sheet_08, 'Arm onto the servo'), '08b': (sheet_08b, 'Rest position'), '09': (sheet_09, 'Pin through the arm'),
    '10': (sheet_10, 'First dispense'), '11': (sheet_11, 'Load the chocolate'), '12': (sheet_12, 'Finished'),
}


def main():
    wanted = sys.argv[1:] or list(SHEETS)
    for key in wanted:
        make, title = SHEETS[key]
        sheet = make()
        path = os.path.join(IMAGES, 'assembly-%s.svg' % key)
        with open(path, 'w', encoding='utf-8', newline='\n') as out:
            out.write(sheet.svg(title))
        print(key, os.path.getsize(path) // 1024, 'KB')


if __name__ == '__main__':
    main()
