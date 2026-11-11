#!/usr/bin/env python3
"""Resize the printed parts for a smaller piece of chocolate.

    python tools/resize/build.py            # write the small parts
    python tools/resize/build.py --check    # measure, change nothing

Standard library only.

The parts have no CAD source: the STL files in input/images/ are the design.
So instead of remodelling them, this cuts slabs out of them. Every slab it
removes is *prismatic*: over its whole width the shape does not change, every
surface reaching into it runs straight through it. Cut such a slab out, slide
the far side up to the near side, and the two cut faces match edge for edge.
The result is the same part, narrower, with every hole, pocket, rib, chamfer
and screw boss exactly where the original had it, and the tool refuses to cut
anywhere that is not prismatic rather than producing a part that only looks
right.

The default unit takes a Belgian napolitain, up to 60 x 39 mm. A Swiss one is
30 x 40 mm and 7 mm thick, which rattles around in a lane built for the larger
piece: 10 mm of play across the lane and, worse, 9 mm along it, enough for a
piece to creep forward under the retaining wall and meet the pusher edge on.

The small variant keeps the thickness band the original has - 5.5 mm, the
height of the pusher, to 7.5 mm, the height of the exit slot - so a 7 mm piece
sits in the middle of it and nothing about the height needs to change:

  lane            61.0 x 40.0 mm  ->  48.0 x 31.0
  body            64 x 110 x 105  ->  51 x 101 x 105
  pusher          59.9 x 56.0     ->  46.9 x 51.0
  arm, pin holes  41.0 mm apart   ->  33.7
  stroke          51.0 mm         ->  42.0
  pin             unchanged
  firmware        unchanged: the swing stays at the default anglePush of 77

The depth is the number that matters and it is exact: 31.0 mm for a 30 mm
piece. That play is also what stops a piece turning in the lane, because a
30 x 40 piece cannot rotate more than a couple of degrees in a lane 31 deep.

The width is not free, and 48 mm is as narrow as this mechanism goes. The arm
has to swing out across the lane far enough to drive the pusher, and at the
middle of its swing it reaches the pivot less the crank less 3.9 mm of material
round the pin hole. Beyond that is the rail the pusher runs under, which the
arm passes 3 mm below the top of and so cannot cross: with the crank at 33.7
that puts the far wall of the lane at 48 mm and leaves 1.4 mm to spare. A
narrower lane means a shorter crank, a shorter crank means a wider swing to
keep the stroke, and a wider swing moves the arm through clearances around the
servo box that are already tight on the built unit. Not worth 2 mm.

The play this leaves across the lane - 4 mm each side of a 40 mm piece - does
no harm. The exit slot is the full width of the lane, so a piece lying against
either wall still leaves cleanly. It was the play along the lane, 9 mm of it,
that misfed: enough for a piece to creep forward under the retaining wall and
meet the pusher edge on.

The arm loses its 7.3 mm out of the plain bar between the two holes, so
everything within 23.7 mm of the servo shaft - all of the part that passes
through the slot under the servo box - is exactly as it was, and the sweep of
the arm, with every clearance already proved on a built unit, is unchanged.
"""

import os
import struct
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
IMAGES = os.path.join(ROOT, 'input', 'images')
AXIS = {'x': 0, 'y': 1, 'z': 2}


# ------------------------------------------------------------------ binary STL

def load(path):
    data = open(path, 'rb').read()
    count = struct.unpack('<I', data[80:84])[0]
    out = []
    for i in range(count):
        v = struct.unpack('<12f', data[84 + i * 50:84 + i * 50 + 48])
        out.append((v[3:6], v[6:9], v[9:12]))
    return out


def save(path, tris):
    out = bytearray(b'\0' * 80)
    out += struct.pack('<I', len(tris))
    for t in tris:
        n = normal(t)
        out += struct.pack('<12fH', n[0], n[1], n[2], *[c for p in t for c in p], 0)
    open(path, 'wb').write(bytes(out))


def normal(t):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = (nx * nx + ny * ny + nz * nz) ** 0.5
    return (0.0, 0.0, 0.0) if length == 0 else (nx / length, ny / length, nz / length)


def measure(tris):
    """Triangle count, bounding box, volume, and how far from watertight it is."""
    edges = defaultdict(int)
    volume = 0.0
    for t in tris:
        key = [tuple(round(c, 4) for c in p) for p in t]
        for i in range(3):
            a, b = key[i], key[(i + 1) % 3]
            edges[(a, b) if a < b else (b, a)] += 1
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
        volume += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx)
                   + az * (bx * cy - by * cx)) / 6.0
    span = tuple((min(p[i] for t in tris for p in t), max(p[i] for t in tris for p in t))
                 for i in range(3))
    return dict(tris=len(tris), span=span, volume=abs(volume),
                open_edges=sum(1 for n in edges.values() if n != 2))


# ----------------------------------------------------------------- the surgery

def prismatic_bands(tris, axis, shortest=1.0):
    """Every band along the axis that could be cut out without changing the shape.

    A band is safe when no surface turns inside it. In a closed mesh that is the
    whole test: if every triangle reaching into the band lies parallel to the
    axis, then each patch of surface in there is a plane containing the axis,
    and two such patches can only meet along a line that runs along the axis, so
    the cross section is the same everywhere across the band. A surface that
    began or ended inside the band would have to be capped by a face across the
    axis, and that face is not parallel to it, so it blocks the band.
    """
    i = AXIS[axis]
    blocked = []
    for t in tris:
        lo = min(p[i] for p in t)
        hi = max(p[i] for p in t)
        if abs(normal(t)[i]) > 1e-4 and hi - lo > 1e-9:
            blocked.append([lo, hi])
    blocked.sort()
    merged = []
    for lo, hi in blocked:
        if merged and lo <= merged[-1][1] + 1e-9:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    low = min(p[i] for t in tris for p in t)
    high = max(p[i] for t in tris for p in t)
    free = []
    cursor = low
    for lo, hi in merged:
        if lo - cursor > 1e-9:
            free.append((cursor, lo))
        cursor = max(cursor, hi)
    if high - cursor > 1e-9:
        free.append((cursor, high))
    return [(a, b) for a, b in free if b - a >= shortest]


def check(tris, axis, a, b):
    """The triangles that stop this band from being cut out. Empty means safe."""
    i = AXIS[axis]
    bad = []
    for t in tris:
        lo = min(p[i] for p in t)
        hi = max(p[i] for p in t)
        if hi <= a + 1e-6 or lo >= b - 1e-6:
            continue
        if abs(normal(t)[i]) > 1e-4:
            bad.append(t)
    return bad


def cut(tris, axis, a, b):
    """Take the band a..b out and close the gap.

    Not by cutting the mesh: every vertex in the band is pulled onto its near
    face and everything beyond it slides down. No vertex is added and no
    triangle is divided, so a mesh that was closed stays closed - there is no
    seam to weld, because nothing was ever parted. Triangles that lived entirely
    inside the band come out flat and are dropped.
    """
    bad = check(tris, axis, a, b)
    if bad:
        raise ValueError('%s %.2f..%.2f is not prismatic: %d triangles in the way, '
                         'first at %r' % (axis, a, b, len(bad), bad[0]))
    i = AXIS[axis]
    width = b - a
    out = []
    for t in tris:
        moved = tuple(tuple(_squash(p[k], a, b, width) if k == i else p[k]
                            for k in range(3)) for p in t)
        if normal(moved) != (0.0, 0.0, 0.0):
            out.append(moved)
    return out


def _squash(value, a, b, width):
    if value <= a:
        return value
    return value - width if value >= b else a


def _column(tris, x, y):
    """Heights at which a line straight up through (x, y) meets the surface."""
    out = []
    for (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) in tris:
        d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if d == 0:
            continue
        l1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / d
        if l1 < 0 or l1 > 1:
            continue
        l2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / d
        if l2 < 0 or 1 - l1 - l2 < 0:
            continue
        out.append(l1 * z1 + l2 * z2 + (1 - l1 - l2) * z3)
    out.sort()
    return out


def verify(before, after, axis, a, b, step=1.3):
    """Prove the cut by measuring, not by trusting the test that allowed it.

    Nothing moves in z, so a line straight up through the new part must meet its
    surface at exactly the heights it met the old part's, taken at the point the
    cut moved it from. Walk a grid of such lines and compare. Mismatches are
    returned; none means the two solids agree everywhere the grid looked.
    """
    i = AXIS[axis]
    width = b - a
    spanx = (min(p[0] for t in after for p in t), max(p[0] for t in after for p in t))
    spany = (min(p[1] for t in after for p in t), max(p[1] for t in after for p in t))
    wrong = []
    checked = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            source = [x, y]
            if i == 2:
                raise ValueError('a cut in z cannot be checked by looking along z')
            source[i] = source[i] if source[i] <= a else source[i] + width
            here = _column(after, x, y)
            there = _column(before, source[0], source[1])
            checked += 1
            if len(here) != len(there) or any(
                    abs(p - q) > 1e-3 for p, q in zip(here, there)):
                wrong.append((x, y, here, there))
            x += step
        y += step
    return checked, wrong


# -------------------------------------------------------------- what to cut out

# Every band below is given in the coordinates of the original STL file, which
# is what the measurements in --check report. Cutting one band moves everything
# beyond it, so the bands are applied from the far end back: then each one is
# still where it was measured when its turn comes.

# Body. Two bands across it, one along it.
#   x 40.00..47.00   between the rail the pusher runs under and the bay wall
#   x 74.00..80.00   between the bay and the box the servo sits in
#   y 65.00..74.00   plain lane wall, well clear of the window in the back wall
# 13 mm off the width and 9 mm off the depth of the lane.
BODY = [('x', 40.00, 47.00), ('x', 74.00, 80.00), ('y', 65.00, 74.00)]

# Pusher. The same 13 mm across, in two bands that miss the three ribs
# underneath, and 5 mm out of its length, which brings the pin slot closer to
# the pushing edge by just as much as the stroke has shortened.
PUSHER = [('x', 28.00, 35.00), ('x', 50.00, 56.00), ('y', -70.00, -65.00)]

# Arm. 7.3 mm out of the plain bar between the two holes: 41 mm apart becomes
# 33.7, which with the unchanged 77 degree swing gives a 42 mm stroke.
ARM = [('x', -53.25, -45.95)]

PARTS = [('body', BODY), ('pusher', PUSHER), ('arm', ARM)]


def main():
    check_only = '--check' in sys.argv
    for name, recipe in PARTS:
        source = os.path.join(IMAGES, 'spenser-%s.stl' % name)
        tris = load(source)
        before = measure(tris)
        print('%s: %d triangles, %.0f mm3, %s%s' % (
            name, before['tris'], before['volume'],
            ' x '.join('%.2f..%.2f' % s for s in before['span']),
            '' if before['open_edges'] == 0 else
            '  (%d open edges in the source)' % before['open_edges']))
        if check_only:
            for axis in 'xyz':
                bands = prismatic_bands(tris, axis)
                print('   bands in %s: %s' % (axis, ', '.join(
                    '%.2f..%.2f (%.2f)' % (a, b, b - a) for a, b in bands) or 'none'))
            continue
        for axis, a, b in sorted(recipe, key=lambda band: -band[1]):
            narrower = cut(tris, axis, a, b)
            checked, wrong = verify(tris, narrower, axis, a, b)
            if wrong:
                raise SystemExit('%s: the cut %s %.2f..%.2f does not hold up: %d of %d '
                                 'lines disagree, first at x %.2f y %.2f'
                                 % ((name, axis, a, b, len(wrong), checked) + wrong[0][:2]))
            print('   cut %s %.2f..%.2f  (%.2f mm), %d lines through it agree'
                  % (axis, a, b, b - a, checked))
            tris = narrower
        after = measure(tris)
        target = os.path.join(IMAGES, 'spenser-%s-small.stl' % name)
        save(target, tris)
        print('   -> %s: %d triangles, %.0f mm3, %s' % (
            os.path.relpath(target, ROOT).replace('\\', '/'), after['tris'],
            after['volume'], ' x '.join('%.2f..%.2f' % s for s in after['span'])))
        extra = after['open_edges'] - before['open_edges']
        print('   %s' % ('watertight' if after['open_edges'] == 0 else
                         'open edges: %d, %+d against the source'
                         % (after['open_edges'], extra)))
    if not check_only:
        print('\nthe pin is unchanged: spenser-pin.stl serves both sizes')


if __name__ == '__main__':
    main()
