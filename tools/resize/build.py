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

A slab can also be pushed in rather than taken out. Inserting one at a plane
the surface crosses only side-on lifts everything above it and stretches the
walls that span it, which is the same proof read backwards, and the same
refusal applies: a face that is not parallel to the plane would be sheared, so
it blocks.

The default unit takes a Belgian napolitain, up to 60 x 39 mm. A Swiss one is
30 x 40 mm and 7 mm thick, which rattles around in a lane built for the larger
piece: 20 mm of play across the lane and, worse, 9 mm along it, enough for a
piece to creep forward under the retaining wall and meet the pusher edge on.

The small variant keeps the thickness band the original has - 5.5 mm, the
height of the pusher, to the height of the exit slot - so a 7 mm piece sits in
the middle of it and nothing about the height needs to change:

  lane            61.0 x 40.0 mm  ->  41.75 x 31.0
  body            64 x 110 x 105  ->  44.75 x 80.8 x 107
  pusher          59.9 x 56.0     ->  40.65 x 46.0
  arm, pin holes  41.0 mm apart   ->  28.75
  stroke          51.05 mm        ->  37.11
  retaining ledge z 9.0..10.0     ->  11.0..12.0, lifted, same 2.5 mm overhang
  servo ear seat  z 23.089        ->  23.089, put back down after the lift
  pusher slot     2.345 mm        ->  2.80, which the 2.55 mm pin needs
  arm pin bore    1.247 mm        ->  drill it 2.6; see below
  pin             unchanged
  firmware        anglePush 81, and the arm set 46.9 deg back at rest

Both lane numbers are set by something different, and it is worth knowing
which. The depth is set by the chocolate and it is exact: 31.0 mm for a 30 mm
piece. That is also what stops a piece turning, because a 30 x 40 piece cannot
rotate more than a couple of degrees in a lane 31 deep, and it was the 9 mm of
play along the lane that misfed. The width is set by the mechanism.

The arm has to swing out across the lane to drive the pusher, and its two
reaches from the servo axis are

  across the lane   stroke / (2 sin(swing/2)) + 5 mm of material past the pin
  towards the stack stroke / 2 + 5 mm x sin(swing/2)

The first is what the lane width has to clear, and it shrinks as the swing
opens: a wider swing buys a shorter crank for the same stroke, and a shorter
crank is a narrower lane. The second barely moves, because half the stroke
dominates it, so opening the swing costs almost nothing on the side where the
chocolate is. What it does cost is push: the stroke starts at one end of the
swing, where the crank's purchase along the travel is cos(swing/2), and that is
exactly where the bottom piece has to be sheared out from under the column. At
81 degrees swung back off centre that is 87% of what the built unit starts
with. Past about 120 it would want trying before trusting.

How long the rail has to be is a separate sum, and an easy one to get wrong:
the pushing face does not start at the back of the lane. pusher_placement in
tools/assembly puts the pin 82.075 mm from the pusher's slot, so the face sits
some way behind the stack at rest and the tail reaches some way past the front
of the lane. Write S for half the stroke and s for how much the pusher is
shortened by, and three numbers move together:

  rail the tail never reaches   34.675 - S
  overtravel past the exit      S - 16.925 + s
  take-up behind the stack      S - 14.075 - s

The first is what can come off the front of the rail, and it grows as the
stroke shrinks. Those three sums hold only while the swing stays centred on
the arm pointing straight across, though, and nothing says it has to be:
the hub bore is round, not splined, so the arm can be clamped anywhere on the
horn. Set it further round and the whole travel moves back, which puts the
pushing face behind the stack again without touching the stroke. Centred,
4 mm of overtravel and 1 mm of take-up force 2S >= 36 and cap the rail at
16.7 mm; swung back, the pusher can lose 5 mm at the face and the rail 20.2.

Note which end each cut answers, because it is easy to get backwards: the
pusher's band lies between its slot and its pushing face, so shortening it
moves the face and not the tail.

20.2 mm comes off here, at anglePush 81 with the arm 46.9 degrees back at rest
and a pusher 10 mm shorter than the original. That leaves 4.11 mm of
overtravel against the 3.60 the built unit runs on, 1.90 of take-up, and the
pusher's tail poking 1.66 mm out of the mouth at full advance - which costs
nothing, because the mouth has no front wall. At the height the arm runs, the
front face is the two side walls and nothing between them, so the arm and the
pin move in open air there whatever the pusher is doing.

The far wall the arm must clear used to be the ledge the pusher runs under, at
x 40.0, because the arm's far end is 3.0 mm thick and its top 1.05 mm fouled
the ledge's z 9..10. Lifting the ledge 2.0 mm, by pushing a slab in at z 8.0,
puts its underside at 11.05 and the arm passes a clear 1.0 mm below it. The
obstacle becomes the bare wall at x 37.5, which is worth 2.5 mm of lane and
keeps the full 2.5 mm of overhang that holds the pusher down. The slot the
chocolate leaves by grows with it, 7.5 mm to 9.5, which changes nothing: two
7 mm pieces still cannot pass it together.

A slab pushed in at z 8.0 lifts everything above z 8.0, and the ledge is not
the only thing up there: the shelf the servo's ears rest on, at z 23.089, went
up with it. The servo sets the height of the horn, the horn sets the height of
the arm, so the arm rose the same 2.0 mm and the lift bought nothing. The two
of them kept their old relationship, and the arm's top - 1.0 mm of it - stayed
inside the ledge, where the sweep puts the arm 0.99 mm under the ledge's inner
edge at x 40.0. It also cost what had not been wrong before: the pin hangs
2.0 mm higher in the pusher's slot, which is a through slot 4.71 mm deep, so
engagement went from 4.69 mm to 2.69. So the seat is moved back down by 2.0 mm
after the lift, which leaves the ledge lifted and the arm where the built unit
has it. Nothing else in the part sits on that plane - the 105 vertices on it
are all inside the servo box, and the nearest other plane is 0.074 mm away -
and the shoulder under it keeps 7.46 mm of its 9.46.

What that leaves, measured over the whole swing rather than at the centreline:
1.50 mm from the far wall, 4.72 mm from the face of the chocolate stack, and
the magazine wall lifted clean out of reach. For scale, the same measurement
run against the built unit reports it 1.5 mm inside both the magazine wall and
the servo pocket, so the datum here - ARM_Z, or the pocket - is off by about
that much and these figures carry the error. The comparison is the part to
trust: this variant has more room than the unit that works.

The arm loses 12.25 mm out of the plain bar between the two holes; everything
within 16.5 mm of the servo shaft - all of the part that passes through the
slot under the servo box - is exactly as it was. The bar would give 16.49
before the hub's walls start, and the second arm here, spenser-arm-small-short,
takes 3.00 mm more of it for a crank of 25.75. That is a stop-gap for a body
already printed with the seat 2.0 mm high: it pulls the arm's far end back to
x 42.0, two clear millimetres short of the ledge, without touching the body.
It is not the better fix. Stroke falls to 33.44 mm, and since the lane is
31.0 mm deep, overtravel past the exit and take-up behind the stack share
whatever the stroke has over 31: 6.11 mm at a crank of 28.75, 2.44 at 25.75,
against the 3.60 mm of overtravel the built unit runs on. Dropping the seat
costs no stroke at all.

One thing here is not about the small size at all, and is in the stock files:
the pin's shaft measures 2.550 mm, the arm's bore 1.247 and the pusher's slot
2.345, so three parts that have to share one diameter have three. The pin was
never going to fit either of them, on any printer. The slot this tool widens,
because its far wall is one flat face and what moved can be measured
afterwards. The bore it leaves alone: that hole is a fourteen-sided prism, so
scaling its wall by eye lands somewhere between 2.53 and 2.60 depending on
whether you read the facets or the corners, which is how you get a part that
looks right and still does not fit. Drill it 2.6 mm instead - the 1.25 mm bore
is a pilot and will centre the drill for you.
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


def lift(tris, axis, at, amount):
    """Push a slab in at the plane `at` and move everything beyond it out.

    The reverse of cut, and safe under the same condition. A triangle that
    crosses the plane side-on - parallel to the axis - simply gets longer, which
    is what a stretched wall should do. One that crosses it at an angle would be
    sheared into a shape the original never had, so it blocks. Nothing is split
    and no vertex is added, so a closed mesh stays closed.
    """
    i = AXIS[axis]
    bad = []
    for t in tris:
        lo = min(p[i] for p in t)
        hi = max(p[i] for p in t)
        if lo < at - 1e-6 and hi > at + 1e-6 and abs(normal(t)[i]) > 1e-4:
            bad.append(t)
    if bad:
        raise ValueError('%s = %.2f is not a clean seam: %d triangles cross it at an '
                         'angle, first at %r' % (axis, at, len(bad), bad[0]))
    return [tuple(tuple(p[k] + (amount if (k == i and p[k] > at + 1e-9) else 0.0)
                        for k in range(3)) for p in t) for t in tris]


def move_plane(tris, axis, at, delta):
    """Slide one flat face along its own normal: a slot gets wider, a wall thinner.

    Every vertex sitting on the plane moves and no other does, so this is only
    right where that plane carries a single flat face. Unlike a cut it cannot be
    proved from the mesh, so what it did is measured afterwards instead.
    """
    i = AXIS[axis]
    hits = 0
    out = []
    for t in tris:
        moved = []
        for p in t:
            if abs(p[i] - at) < 1e-3:
                hits += 1
                q = list(p)
                q[i] = p[i] + delta
                moved.append(tuple(q))
            else:
                moved.append(p)
        out.append(tuple(moved))
    if not hits:
        raise ValueError('nothing sits on %s = %.3f' % (axis, at))
    return out


def union(tris, count, overlap=1.5):
    """N lanes in one printed part, by standing copies in each other's side wall.

    Both outer faces of the body are flat planes over its whole depth and
    height, and both side walls are the same 1.5 mm slab, so a copy moved along
    by the width less one wall thickness lands its left wall exactly where the
    last copy's right wall is. The two slabs then occupy the same space rather
    than meeting at a surface, which is what a slicer wants: it unions them, and
    the part comes out with one shared wall between neighbouring lanes instead
    of two back to back.

    Nothing is cut and nothing is welded. Each copy keeps its own closed
    surface, so every edge still has exactly the two triangles it had and the
    file reports watertight; what makes it one part is that the copies overlap
    in solid material. Lanes come out identical, at a pitch of width - 1.5.
    """
    low = min(p[0] for t in tris for p in t)
    high = max(p[0] for t in tris for p in t)
    pitch = (high - low) - overlap
    out = []
    for k in range(count):
        shift = k * pitch
        out += [tuple((p[0] + shift, p[1], p[2]) for p in t) for t in tris]
    return out, pitch


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

# Every position below is given in the coordinates of the original STL file,
# which is what the measurements in --check report. Cutting one band moves
# everything beyond it, so the cuts are applied from the far end back: then each
# one is still where it was measured when its turn comes. The other operations
# follow, on positions that the cuts did not disturb.

# Body. Three bands across it, one along it, then the lift.
#   x 40.00..47.00   between the rail the pusher runs under and the bay wall
#   x 50.00..52.60   the lane's own air, between the rail and the bay
#   x 74.00..83.65   between the bay and the box the servo sits in
# The first two come off below the window in the back wall and the third above
# it, 9.60 against 9.65, so that the window - the one feature that was centred
# on the lane - still is. Take it all off one side and it ends up 9.15 mm out.
#   y 65.00..74.00   plain lane wall, well clear of the window in the back wall
#   y -10.00..10.20  the front of the rail, bar 1.5 mm the tail now pokes out of
#   z 8.00 + 2.00    lifts the retaining ledge off the arm's path
#   z 25.089 - 2.00  puts the servo's ear seat back down, which that lift raised
# 19.25 mm off the width, 9 off the depth of the lane and 20.2 off the rail.
# The seat is given at 25.089 because the lift has already moved it by then:
# it reads 23.089 in the source file, and has to end up there again.
BODY = [('cut', 'x', 40.00, 47.00),
        ('cut', 'x', 50.00, 52.60),
        ('cut', 'x', 74.00, 83.65),
        ('cut', 'y', 65.00, 74.00),
        ('cut', 'y', -10.00, 10.20),
        ('lift', 'z', 8.00, 2.00),
        ('plane', 'z', 25.089, -2.00)]

# Pusher. The same 19.25 across, in two bands that miss the three ribs
# underneath, and 10 mm out of its length. That band lies between the pin slot
# and the pushing face, so it moves the face and not the tail: 5 mm of it
# answers the shallower lane and the other 5 lets the whole travel sit further
# back, which is what frees the rail. Then the slot's far wall moves out 0.455,
# which is what makes room for the pin.
PUSHER = [('cut', 'x', 27.00, 36.625),
          ('cut', 'x', 48.00, 57.625),
          ('cut', 'y', -70.00, -60.00),
          ('plane', 'y', -83.248, -0.455)]

# Arm. 12.25 mm out of the plain bar between the two holes: 41 mm apart becomes
# 28.75, which at anglePush 81 gives the 37.11 mm stroke the lane wants.
ARM = [('cut', 'x', -55.49, -43.24)]

# And the stop-gap: 3.00 mm more, for a crank of 25.75. Not one band of 15.25,
# because two triangles lie across x -43.24..-43.00; two bands either side of
# them come to the same thing, and the far one is cut first, so the near one is
# still where it was measured when its turn comes.
ARM_SHORT = ARM + [('cut', 'x', -43.00, -40.00)]

PARTS = [('body', 'body-small', BODY),
         ('pusher', 'pusher-small', PUSHER),
         ('arm', 'arm-small', ARM),
         ('arm', 'arm-small-short', ARM_SHORT)]


def main():
    check_only = '--check' in sys.argv
    if '--union' in sys.argv:
        count = int(sys.argv[sys.argv.index('--union') + 1])
        which = 'body-small' if '--standard' not in sys.argv else 'body'
        tris = load(os.path.join(IMAGES, 'spenser-%s.stl' % which))
        one = measure(tris)
        many, pitch = union(tris, count)
        both = measure(many)
        target = os.path.join(IMAGES, 'spenser-%s-x%d.stl' % (which, count))
        save(target, many)
        print('%s: %s, lane pitch %.2f mm, one 1.50 mm wall between lanes'
              % (which, ' x '.join('%.2f' % (s[1] - s[0]) for s in one['span']), pitch))
        print('-> %s: %d triangles, %.0f mm3, %s' % (
            os.path.relpath(target, ROOT).replace('\\', '/'), both['tris'],
            both['volume'], ' x '.join('%.2f' % (s[1] - s[0]) for s in both['span'])))
        print('   %s' % ('watertight' if both['open_edges'] == 0 else
                         'open edges: %d' % both['open_edges']))
        print('   needs %d pushers, %d arms, %d pins and %d servos' % ((count,) * 4))
        return
    seen = set()
    for name, target_name, recipe in PARTS:
        source = os.path.join(IMAGES, 'spenser-%s.stl' % name)
        tris = load(source)
        before = measure(tris)
        print('%s: %d triangles, %.0f mm3, %s%s' % (
            target_name, before['tris'], before['volume'],
            ' x '.join('%.2f..%.2f' % s for s in before['span']),
            '' if before['open_edges'] == 0 else
            '  (%d open edges in the source)' % before['open_edges']))
        if check_only:
            if name in seen:
                continue
            seen.add(name)
            for axis in 'xyz':
                bands = prismatic_bands(tris, axis)
                print('   bands in %s: %s' % (axis, ', '.join(
                    '%.2f..%.2f (%.2f)' % (a, b, b - a) for a, b in bands) or 'none'))
            continue
        cuts = [op for op in recipe if op[0] == 'cut']
        for _, axis, a, b in sorted(cuts, key=lambda op: -op[2]):
            narrower = cut(tris, axis, a, b)
            checked, wrong = verify(tris, narrower, axis, a, b)
            if wrong:
                raise SystemExit('%s: the cut %s %.2f..%.2f does not hold up: %d of %d '
                                 'lines disagree, first at x %.2f y %.2f'
                                 % ((target_name, axis, a, b, len(wrong), checked) + wrong[0][:2]))
            print('   cut %s %.2f..%.2f  (%.2f mm), %d lines through it agree'
                  % (axis, a, b, b - a, checked))
            tris = narrower
        for op in recipe:
            if op[0] == 'lift':
                _, axis, at, amount = op
                tris = lift(tris, axis, at, amount)
                print('   lifted everything above %s = %.2f by %.2f mm' % (axis, at, amount))
            elif op[0] == 'plane':
                _, axis, at, delta = op
                tris = move_plane(tris, axis, at, delta)
                print('   moved the face at %s = %.3f by %+.3f mm' % (axis, at, delta))
        after = measure(tris)
        target = os.path.join(IMAGES, 'spenser-%s.stl' % target_name)
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
