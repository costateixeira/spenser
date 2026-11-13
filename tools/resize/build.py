#!/usr/bin/env python3
"""Resize the printed parts for a smaller piece of chocolate.

    python tools/resize/build.py                  # the Belgian mignonette: nothing
                                                  #   to cut, these parts are it
    python tools/resize/build.py --piece 40x30x7 --name small
                                                  # the Swiss napolitain
    python tools/resize/build.py --check          # measure, change nothing
    python tools/resize/build.py --union 2        # two lanes in one printed part

Standard library only.

The parts have no CAD source: the STL files in input/images/ are the design.
Nothing here writes one of them. spenser-body.stl, spenser-pusher.stl,
spenser-arm.stl and spenser-pin.stl are only ever read, every variant is
written beside them under a name of its own, and a target that would land on
one of the four is refused.

Since they are the design, instead of remodelling them this cuts slabs out of
them. Every slab it removes is *prismatic*: over its whole width the shape does
not change, every surface reaching into it runs straight through it. Cut such a
slab out, slide the far side up to the near side, and the two cut faces match
edge for edge. The result is the same part, narrower, with every hole, pocket,
rib, chamfer and screw boss exactly where the original had it, and the tool
refuses to cut anywhere that is not prismatic rather than producing a part that
only looks right.

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

  lane            61.0 x 40.0 mm  ->  44.35 x 31.0
  body            64 x 110 x 105  ->  47.35 x 80.8 x 105
  pusher          59.9 x 56.0     ->  43.25 x 46.0
  arm, pin holes  41.0 mm apart   ->  26.75
  stroke          51.05 mm        ->  34.53
  module bay      24.00 mm wide   ->  unchanged; it is what sets the width
  retaining ledge z 9.0..10.0     ->  unchanged, and 3.61 mm clear of the arm
  servo box       unchanged       ->  unchanged, like every height in the body
  pusher slot     2.345 mm        ->  2.55, 1.00 nearer the edge, and a second
                                      one 5.00 further in again
  arm pin bore    2.760 mm        ->  3.10, as far as the method goes
  pin shaft       2.550 mm        ->  2.30, the other half of the same fit
  firmware        anglePush 81, and the arm set 46.9 deg back at rest

Each of the lane's three numbers is set by something different, and it is
worth knowing which. The height is the original's, untouched. The depth is set
by the chocolate and it is exact: 31.0 mm for a 30 mm piece. That is also what
stops a piece turning, because a 30 x 40 piece cannot rotate more than a couple
of degrees in a lane 31 deep whatever the lane's width, and it was the 9 mm of
play along the lane that misfed.

The width is set by neither, and not by the mechanism either. It is set by one
thing standing in the lane's own width: the bay the Atomic Motion Base drops
into, 24.00 mm wide between its posts for a module 24.0 wide, with no clearance
at all in the part that works. Nothing may come out of that, and nothing may
come out of the servo's pocket beside it either, 12.26 mm for a case 12.2
thick. What is left is two bands, and together they are the whole of the width
this can give up:

  x 40.00..47.00   7.00, between the retaining ledge's inner edge and the bay's
                   near post: plain air at every height
  x 74.00..83.65   9.65 of the 11.53 slot between the bay's far post and the
                   servo tower, leaving 1.88

So the lane goes 61 -> 44.35 and no further, the body 64 -> 47.35, and a 40 mm
piece keeps 3.35 mm of play across the lane.

The second band took two goes to get right, in both directions. It looks like
the channel the servo plugs reach into, and on that reading it had to stay: the
module's four headers stand out of its far face and a servo plug needs 8 mm in
front of one. But measure the slot and it is walled on both sides only over
z 14.00..32.00, which is the servo tower's own height, while the headers sit at
z 40.40..75.00 - the base stands on its tab at z 28.4 and they start 12 mm up
it. Above z 32.00 there is nothing on that side of the body at all, so the
plugs are in open air and the slot under them is free. It had been cut, then
put back, then cut again.

What was not free, and is the whole of what went wrong, is x 50.00..52.60. That
band is inside the bay, and 2.60 out of 24.00 leaves 21.41 for a module 24.0
wide - about the 2 mm it was short by when it was tried. A cut through air is
still prismatic: a cross section through the front of the body shows a lot of
air, the tool proves only that the shape does not change across the band, and
nothing in this file knows which of that air something stands in. What stands
where is in tools/assembly/build.py, which has the module at 24 x 72 x 20.7,
its bay "24 wide between x 48 and 72", and its headers up the side at 12, 21,
30 and 39 mm.

The arm has to swing out across the lane to drive the pusher, and its two
reaches from the servo axis are

  across the lane   stroke / (2 sin(swing/2)) + 5 mm of material past the pin
  towards the stack stroke / 2 + 5 mm x sin(swing/2)

The first is what the lane width has to clear, and it shrinks as the swing
opens: a wider swing buys a shorter crank for the same stroke. On this body
that no longer sets the width - the electronics do - but it is what decides
whether the arm fits the width they leave. The second barely moves, because half the stroke
dominates it, so opening the swing costs almost nothing on the side where the
chocolate is. What it does cost is push: the stroke starts at one end of the
swing, where the crank's purchase along the travel is cos(swing/2), and that is
exactly where the bottom piece has to be sheared out from under the column. At
81 degrees swung back off centre that is 87% of what the built unit starts
with. Past about 120 it would want trying before trusting.

How long the rail has to be is a separate sum, and an easy one to get wrong:
the pushing face does not start at the back of the lane. pusher_placement in
tools/assembly puts the pin 82.075 mm from the pusher's slot, so the face sits
some way behind the stack at rest and the tail reaches some way back along the
rail. Write S for half the stroke and s for how much the pusher is
shortened by, and three numbers move together:

  rail the tail never reaches   34.675 - S
  overtravel past the exit      S - 16.925 + s
  take-up behind the stack      S - 14.075 - s

The first is what can come off the back of the rail, and it grows as the
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
and a pusher 10 mm shorter than the original. With the arm shortened to a crank
of 26.75 that leaves 1.63 mm of overtravel against the 3.60 the built unit runs
on and 1.90 of take-up. It comes off the back, which is the end away from the
mouth: the chocolate leaves through the other end, where the magazine's end
wall carries a 7.5 mm slot under a lintel at z 9.00..17.00. The back has no
wall at all at the height the arm runs - the two side walls and nothing between
them - so the arm, the pin and the pusher's tail all move in open air there,
and 20.2 mm of rail behind the pusher is what the body can lose without the
mouth or the lane noticing.

The one thing in the way of the arm is the ledge the pusher runs under, at
x 40.0: the arm's far end is 3.0 mm thick and its top 1.05 mm fouls the ledge's
z 9..10. There are two ways past that, and this went down the wrong one first.

Lifting the ledge 2.0 mm, by pushing a slab in at z 8.0, puts its underside at
11.05 and the arm passes a clear millimetre below it. But a slab pushed in at
z 8.0 lifts everything above z 8.0, and the ledge is not the only thing up
there: the servo box goes with it. The servo sets the height of the horn and
the horn the height of the arm, so the arm rises the same 2.0 mm and the lift
buys nothing, while the pin hangs 2.0 mm higher in the pusher's slot - a
through slot 4.71 mm deep - so engagement drops from 4.69 mm to 2.69. Pulling
the box back down is no better. It is what the servo itself needs, because it
hangs by its ears on a seat and the short end of its case, 3.80 mm of it, has
to fit between that seat and the floor of the pocket, where the standard body
leaves 3.841 and the hole in that floor is 15.60 mm long against a case 22.8
long, so the floor is a hard stop and not something the case passes through.
But the box is also what the arm's hub swings under, and taking the box down
out from under a lifted ledge closes that gap from the 8.061 mm the standard
body gives it to 6.186. Two faces of the same 2 mm, and no height in the body
satisfies both.

So the body is left alone. No slab is pushed in and no face is moved: all five
cuts are in x and y, so every height in the part is the height the standard
body has it - the ledge at 9..10 with its 2.5 mm of overhang, the exit slot at
7.5 which one 7 mm piece passes and two cannot, the floor of the servo box, the
seat, and the 3.841 between them that the case needs. The 2 mm comes off the
arm instead, where it costs stroke and nothing else.

The arm loses 14.25 mm out of the plain bar between the two holes, in two bands:
12.25 is as much as one band can take, because two triangles lie across
x -43.24..-43.00, and the last 2.00 comes from the stretch beyond them. The holes end up 26.75 mm apart, and
that is what lets the ledge stay where it is - the far end then reaches only
x 41.0, a clear millimetre short of the ledge's inner edge, so no part of the
arm ever passes under it. Everything within 16.5 mm of the servo shaft, which
is all of the part that goes through the slot under the servo box, is exactly
as it was.

The last 2.00 mm is not free. Stroke runs at 1.291 mm per mm of crank, so 37.11
becomes 34.53, and since the lane is 31.0 mm deep, overtravel past the exit and
take-up behind the stack share whatever the stroke has over 31. Take-up is set
by where the arm is fitted - the check is that at rest the pushing face sits
just behind the stack - so the overtravel takes the loss: 4.11 mm at a crank of
28.75, 1.63 at 26.75, against the 3.60 the built unit runs on. 1.63 is the
least of those and still more than the 0.54 an interim arm at 25.75 ran on,
which dispensed. anglePush stays at 81. If the overtravel turns out to be
wanted, 88 buys the whole 37.11 back at a crank of 26.75, for 0.70 mm more
sideways swing in a slot 37.0 mm long that has it to spare.

Taking the 2 mm off the tip instead would cost no stroke at all, and it is the
wrong end. The tip stands 3.90 mm beyond the bore, which is 2.40 mm of wall
round a 3.00 mm hole: 2.00 off leaves 0.40, and the pin's head is 8 mm across
and rests on the plate's top face right there. The tip stays 3.00 mm thick and
the pin still hangs 4.69 mm into a 4.71 mm slot, as it does on the built unit.

Measured over the whole swing rather than at the centreline, the one thing the
sweep still finds in the way is the hub, 0.50 mm into the far wall of the
lane. Axis to far wall is 6.50 mm in every size, so that 0.50 is in
the stock parts as much as in these, and it is the datum rather than the
geometry: the same check run against the built unit reports it 1.5 mm inside
both the magazine wall and the servo pocket, so ARM_Z, or the pocket, is off by
about that much and every figure here carries the error. The comparison is the
part to trust, and on it this variant has the room the unit that works has.

The pin and the arm's hole are the one fit here that paper gets wrong. On
paper there was never a problem: the bore at 2.760 against a shaft of 2.550
leaves 0.21, and opening the bore to 3.00 made that 0.44. Printed, it still
bound - a small hole comes out under its nominal size and a small shaft over
its own, and between them they ate the 0.44. So both halves move now, which is
the only way left:

  the arm's bore   2.760 -> 3.10 across the corners, 3.093 across the flats
  the pin's shaft  2.550 -> 2.30
  between them     0.44 of clearance -> 0.79

The bore cannot carry it alone. The method's limit is nearer than the part's:
the next ring of vertices out sits 1.629 from the axis, so a rim pushed much
past 1.55 would fold the face between them, and 1.55 is where it now is. The
wall around the bore is 2.52 mm and loses 0.17 of it; the pin's head is 8.00
across and still bears 2.45 all round the hole.

Thinning the shaft is the same move as opening the bore, inwards: one ring of
vertices, all at one radius, slid along their own radii. The pusher's slot
then follows the pin rather than the pin the slot: 2.345 as it comes, it is
opened to 2.55 rather than the 2.80 a 2.55 mm pin wanted, which leaves the
thinner pin the same 0.25 of play that worked. It is the far wall that moves,
so the wall the pin actually pushes against is where it always was. The
standard pin is not touched: spenser-pin.stl stays as it is, and
spenser-pin-small.stl is the thinner one.

Both walls of it then move 1.00 mm further back, towards the pusher's own
edge, which is where the pin wants to sit. That leaves 2.25 mm of plate behind
the slot instead of 3.25, and since the pin bears on the near wall going
forward, that plate carries the return stroke and nothing else.

There are two of those slots in the pusher, 5.00 mm apart, and the pin goes in
whichever one is wanted. The second is further in, towards the pushing face,
because that is the way there is room: 2.25 mm of plate lies behind the first
and the whole of the plate in front of it. The choice moves the pusher, not
the stroke. With the pin in the second slot the pusher hangs 5 mm further back
at every point of the swing, so the face starts 5 mm behind where it started
and stops 5 mm short of where it stopped, and the 34.53 mm between those two
is what it was. --second-slot 0 leaves the one slot, and --second-slot takes
any other spacing.

Cutting that slot is not a cut in the sense of the rest of this file: it
leaves a cavity instead of closing one up. It asks the same thing of the band
all the same - every surface reaching into it has to run straight through it -
because that is what makes the band a prism, and the cavity's two end walls
are then a copy of the cross-section it had. The band crosses the three ribs
on the pusher's top face, which is why that cross-section is worth building
properly rather than assuming a rectangle: the walls follow it up over each
rib and down again. What it did is measured afterwards, like everything else
here. The volume lost has to be the volume of the box, to a twentieth of a
cubic millimetre; a line straight up inside the box has to meet no surface at
all; every line beside it has to meet the surface at the heights it met it
before; and the mesh has to come out as closed as it went in.

None of that is about the small size, and all of it is in the stock files:
the pin's shaft measures 2.550 mm, the arm's bore 2.760 and the pusher's slot
2.345, so three parts that have to share one diameter have three, and the
slack between them is thinner than a printer's own error. The slot is the one
the pin cannot enter at all, and this tool widens it, because its far wall is
one flat face and what moved can be measured afterwards. The bore and the
shaft are both 48-sided prisms of one radius - the bore 1.380, which is 2.754
across the flats and 2.760 across the corners - so each is round enough to be
pushed along its own radius and come out round. The standard arm is left at
2.760 and the standard pin at 2.550, which are nominally clear of each other
and print tight; drill that arm 2.6 mm.

All of the above is one size of piece. The numbers come from PIECE, three
dimensions in millimetres - across the lane, along it, and thick. PIECE itself
is the Belgian mignonette, 60 x 39 x 7, which is the piece the files in
input/images are already cut for: run this with nothing after it and it says
so and writes nothing, because the standard parts are the parts for that
piece. --piece 40x30x7 --name small is the Swiss one, and any other piece goes
the same way:

  along the lane   the lane's depth, exactly: the piece plus 1.00, so the band
                   out of the magazine wall is 40.0 less that. This is the one
                   the variant was made for, and the one that misfed.
  thick            the clear height under the retaining ledge, by pushing a
                   slab in at z 8.00. It costs pin engagement a millimetre for
                   a millimetre, because the servo box goes up with the ledge
                   and the arm with the servo. A 7 mm piece needs none of it.
  across the lane  the width, but only between 53 and 60 mm across. Below 53
                   the electronics are the limit and the lane stays at 54.0.

and from the depth, by way of the stroke: the arm's crank, the band out of its
bar, how much comes off the pusher's face, and how much of the rail is left.
Only the depth: a piece that is narrower but no shallower keeps the whole
travel, the arm and the rail as they come, and anglePush stays at 77. plan()
does that arithmetic and prints it, with a note wherever the piece asks for
more than the parts have, and raises rather than write a file it cannot stand
behind. What no piece moves is the module bay, the channel beside it, the
servo pocket, the ear seat, the pocket floor or any other height in the body:
those are the same in every size, which is the whole point of cutting slabs
rather than remodelling.
"""

import math
import os
import struct
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
IMAGES = os.path.join(ROOT, 'input', 'images')
AXIS = {'x': 0, 'y': 1, 'z': 2}

# The four parts everything here is cut from. They have no CAD source: they are
# the design, so nothing in this file ever writes one of them.
SOURCES = frozenset(os.path.normcase(os.path.abspath(
    os.path.join(IMAGES, 'spenser-%s.stl' % part)))
    for part in ('body', 'pusher', 'arm', 'pin'))


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

    What can be checked is that nothing folded over. A face stretched between
    the plane and something closer to it than `delta` comes out inside out, and
    a mesh like that prints as a hole or a blob. So every triangle's normal is
    compared before and after, and a reversal stops the build: usually it means
    two of these moves want doing in the other order, lower face first.
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
    turned = []
    for before, after in zip(tris, out):
        n1, n2 = normal(before), normal(after)
        if n1 == (0.0, 0.0, 0.0):
            continue
        if n2 == (0.0, 0.0, 0.0) or sum(u * v for u, v in zip(n1, n2)) < 0:
            turned.append(after)
    if turned:
        raise ValueError('moving %s = %.3f by %+.3f turns %d faces inside out, '
                         'first at %r' % (axis, at, delta, len(turned), turned[0]))
    return out


def _clip(poly, i, value, below, tol=1e-4):
    """The part of a convex polygon on one side of an axis-aligned plane.

    A vertex within `tol` of the plane counts as being on it: it is kept by
    both sides of the cut and no point is interpolated against it, which is
    what stops a face that was meant to be left whole losing a sliver to the
    single-precision coordinates a binary STL is written in.
    """
    out = []
    for n, a in enumerate(poly):
        b = poly[(n + 1) % len(poly)]
        da = (a[i] - value) * (1.0 if below else -1.0)
        db = (b[i] - value) * (1.0 if below else -1.0)
        da = 0.0 if abs(da) < tol else da
        db = 0.0 if abs(db) < tol else db
        if da <= 0.0:
            out.append(a)
        if (da < 0.0 < db) or (db < 0.0 < da):
            t = da / (da - db)
            out.append(tuple(a[k] + t * (b[k] - a[k]) for k in range(3)))
    return out


def _fan(poly, least=1e-6):
    """A convex polygon as triangles, keeping its winding, dropping slivers."""
    out = []
    for n in range(1, len(poly) - 1):
        t = (poly[0], poly[n], poly[n + 1])
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        if (nx * nx + ny * ny + nz * nz) ** 0.5 / 2.0 > least:
            out.append(t)
    return out


def _outside(tris, xa, xb, y0, y1, tol=1e-7):
    """The part minus a box: every face cut by the box's four side planes.

    Both sides of all four cuts are kept and the pieces whose middle lands
    inside the box are dropped. Every triangle is cut, whether the box comes
    near it or not, because that is what keeps the mesh closed: two triangles
    that share an edge are cut at the same points along it, and so is the edge
    a face passing over the cavity's mouth has lying in the band's own plane -
    half of that edge faces solid and half of it faces the cavity, so it has to
    break where the slot's sides are.

    A face lying in one of the planes is not cut by that plane. It satisfies
    both sides of it, so cutting would hand back two copies of it.
    """
    polys = [list(t) for t in tris]
    for i, at in ((1, y0), (1, y1), (0, xa), (0, xb)):
        split = []
        for poly in polys:
            if all(abs(p[i] - at) < 1e-4 for p in poly):
                split.append(poly)
                continue
            for below in (True, False):
                piece = _clip(poly, i, at, below)
                if len(piece) >= 3:
                    split.append(piece)
        polys = split
    out = []
    for poly in polys:
        n = len(poly)
        cx = sum(p[0] for p in poly) / n
        cy = sum(p[1] for p in poly) / n
        if xa + tol < cx < xb - tol and y0 + tol < cy < y1 - tol:
            continue
        out += _fan(poly)
    return out


def _on(a, b, p, tol=1e-4):
    """Where p sits along the segment a..b, if it is on it and not an end of it."""
    ab = [b[k] - a[k] for k in range(3)]
    ap = [p[k] - a[k] for k in range(3)]
    length = sum(v * v for v in ab) ** 0.5
    if length < tol:
        return None
    t = sum(u * v for u, v in zip(ab, ap)) / length ** 2
    if not 1e-9 < t < 1 - 1e-9:
        return None
    off = max(abs(ap[k] - t * ab[k]) for k in range(3))
    return t if off < tol else None


def _rect(fixed, i, lo, hi, zlo, zhi, outward, pts=()):
    """A rectangle on a plane, facing `outward`, carrying its neighbours' vertices.

    A rectangle is four corners, but an edge of it may be shared with several
    triangles of the part, which meet it at points of their own. Every such
    point is put into the outline, and the triangles then run from the middle
    out, so each edge is broken exactly where the other side breaks and the
    mesh stays closed.
    """
    j = 1 if i == 0 else 0
    corners = []
    for u, v in ((lo, zlo), (hi, zlo), (hi, zhi), (lo, zhi)):
        p = [0.0, 0.0, v]
        p[i], p[j] = fixed, u
        corners.append(tuple(p))
    poly = []
    for n, a in enumerate(corners):
        b = corners[(n + 1) % 4]
        poly.append(a)
        along = [(t, p) for t, p in ((_on(a, b, p), p) for p in pts) if t is not None]
        poly += [p for _, p in sorted(along)]
    middle = tuple(sum(p[k] for p in poly) / len(poly) for k in range(3))
    out = [(middle, poly[n], poly[(n + 1) % len(poly)]) for n in range(len(poly))]
    if normal(out[0])[i] * outward < 0:
        out = [(c, q, p) for c, p, q in out]
    return [t for t in out if _fan(t)]


def slit(tris, xa, xb, y0, y1, eps=1e-6):
    """Carve a through-slot out of a plate: a box taken out, nothing closed up.

    A cut has to be prismatic so that its two faces meet when the far side
    slides up; this has to be prismatic for the opposite reason, so that the
    cavity it leaves is bounded by a copy of the cross-section the band had.
    Every surface reaching into the band must run straight through it, exactly
    as for a cut, and then the band is a prism and its profile is what the
    cavity's two end walls are.

    What the faces crossing the band lose is clipped away rather than moved,
    and the cavity's own walls are built on a grid - every x where a wall
    stands in the band, every z where the profile changes - so each new edge
    has a neighbour along the whole of it. Nothing is stretched and nothing
    slides, so the part is the part it was with a box missing.
    """
    standing = set()
    for t in tris:
        if max(p[1] for p in t) <= y0 + eps or min(p[1] for p in t) >= y1 - eps:
            continue
        n = normal(t)
        if abs(n[1]) > 1e-4:
            raise ValueError('y = %.3f..%.3f is not a clean band for a slot: a face '
                             'reaching into it crosses it at an angle, at %r'
                             % (y0, y1, t))
        flat = max(p[0] for p in t) - min(p[0] for p in t) < 1e-6
        if abs(n[0]) > 1e-4 and not flat:
            raise ValueError('y = %.3f..%.3f is not a clean band for a slot: a wall '
                             'reaching into it leans in x, at %r' % (y0, y1, t))
        if flat:
            standing.add(round(t[0][0], 4))
    for x in standing:
        if abs(x - xa) < 1e-3 or abs(x - xb) < 1e-3:
            raise ValueError('a wall already stands at x = %.3f, where one side of '
                             'the slot would be' % x)
    for t in tris:
        for at in (y0, y1):
            if (all(abs(p[1] - at) < 1e-4 for p in t)
                    and min(p[0] for p in t) < xb and max(p[0] for p in t) > xa):
                raise ValueError('a face already lies in y = %.3f, where one end of '
                                 'the slot would be, at %r' % (at, t))

    edges = [xa] + sorted(x for x in standing if xa < x < xb) + [xb]
    middle = y0 + (y1 - y0) * 0.513
    spans = []
    for a, b in zip(edges, edges[1:]):
        column = _column(tris, a + (b - a) * 0.371, middle)
        if len(column) % 2:
            raise ValueError('the band is not solid at x = %.3f: a line up through it '
                             'meets the surface %d times' % (a, len(column)))
        spans.append([(column[n], column[n + 1]) for n in range(0, len(column), 2)])
    for side, at in ((spans[0], xa - 0.07), (spans[-1], xb + 0.07)):
        column = _column(tris, at, middle)
        outer = [(column[n], column[n + 1]) for n in range(0, len(column), 2)]
        if len(outer) != len(side) or any(abs(p - q) > 1e-4
                                         for u, v in zip(outer, side)
                                         for p, q in zip(u, v)):
            raise ValueError('the profile at x = %.3f is not the one the slot starts '
                             'in: %r against %r' % (at, outer, side))

    levels = sorted({round(v, 6) for s in spans for pair in s for v in pair})
    out = _outside(tris, xa, xb, y0, y1)
    on = {}
    for t in out:
        for p in t:
            for i, at in ((0, xa), (0, xb), (1, y0), (1, y1)):
                if abs(p[i] - at) < 1e-4:
                    on.setdefault((i, at), {})[tuple(round(c, 6) for c in p)] = p

    removed = 0.0
    for zlo, zhi in zip(levels, levels[1:]):
        runs = []
        for (a, b), profile in zip(zip(edges, edges[1:]), spans):
            if not any(lo - eps < (zlo + zhi) / 2.0 < hi + eps for lo, hi in profile):
                continue
            if runs and abs(runs[-1][1] - a) < 1e-9:
                runs[-1] = (runs[-1][0], b)
            else:
                runs.append((a, b))
        for a, b in runs:
            # each end wall holds back the material behind it, so it faces the
            # cavity: forwards at the near end, backwards at the far one
            out += _rect(y0, 1, a, b, zlo, zhi, +1, on.get((1, y0), {}).values())
            out += _rect(y1, 1, a, b, zlo, zhi, -1, on.get((1, y1), {}).values())
            if abs(a - xa) < 1e-9:
                out += _rect(xa, 0, y0, y1, zlo, zhi, +1, on.get((0, xa), {}).values())
            if abs(b - xb) < 1e-9:
                out += _rect(xb, 0, y0, y1, zlo, zhi, -1, on.get((0, xb), {}).values())
            removed += (b - a) * (zhi - zlo) * (y1 - y0)
    return out, removed, len(edges) - 1


def widen_hole(tris, cx, cy, radius, to, tol=0.05):
    """Move the wall of a round feature that runs straight through, along its radius.

    Outwards with `to` larger than `radius`, which opens a hole; inwards with it
    smaller, which thins a shaft. The move is the same either way.

    The wall of such a hole is a ring of vertices all at one radius from its
    axis, the same ring repeated at the top and at the bottom. Move each of them
    out along its own radius and the wall stays vertical and stays a cylinder;
    both rims move with it, because they are those same vertices; and nothing is
    split and no vertex is added, so a closed mesh stays closed.

    Only the ring moves. What the tolerance does not catch is left where it is,
    which is also the limit on how far this can go: the rim must not reach the
    next ring of vertices out, or the face between them folds over.
    """
    moved = set()
    out = []
    for t in tris:
        face = []
        for p in t:
            dx, dy = p[0] - cx, p[1] - cy
            r = math.hypot(dx, dy)
            if abs(r - radius) <= tol:
                moved.add(tuple(round(c, 4) for c in p))
                face.append((cx + dx * to / r, cy + dy * to / r, p[2]))
            else:
                face.append(p)
        out.append(tuple(face))
    if not moved:
        raise ValueError('no hole wall at (%.2f, %.2f) r %.2f'
                         % (cx, cy, radius))
    return out, len(moved)

def lift_beyond(tris, axis, at, amount, gate_axis, gate):
    """Insert a slab at `at`, but only beyond `gate`, and ramp across it.

    A step in a part, not a slab through it: past the gate everything at or
    above the seam goes up, so the material under the seam gets `amount`
    thicker, and short of the gate nothing moves at all.

    The seam is the same proof as `lift` - a surface crossing it must be
    parallel to the axis, or it is sheared - but the gate is not. Triangles
    straddling the gate have some corners raised and some not, and that is
    what builds the riser: nothing is split and no vertex is added, so a closed
    mesh stays closed, and what was a vertical face across the gate comes out
    as a ramp from the old height to the new one. The ramp is as long as those
    triangles are, so the gate wants choosing where they are small and where a
    ramp is harmless - and `at` wants choosing below everything the step is
    meant to carry, so that it is carried rather than stretched.

    Returns the part, and the span the ramp occupies, which is what the
    verification has to leave out and what the caller should check is clear of
    anything that matters.
    """
    i, j = AXIS[axis], AXIS[gate_axis]
    moved = []
    for t in tris:
        moved.append(tuple(
            tuple(p[k] + (amount if (k == i and p[i] >= at - 1e-6 and p[j] >= gate)
                          else 0.0) for k in range(3)) for p in t))
    ramp = [t for t in tris
            if min(p[j] for p in t) < gate < max(p[j] for p in t)
            and max(p[i] for p in t) > at - 1e-6]
    span = ((min(p[j] for t in ramp for p in t), max(p[j] for t in ramp for p in t))
            if ramp else (gate, gate))
    return moved, span, len(ramp)


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


def verify_beyond(before, after, at, amount, gate, ramp, step=0.37):
    """Prove the step by measuring, on both sides of the ramp.

    A line straight up through the part must meet its surface where it did,
    except that beyond the gate every crossing at or above the seam is `amount`
    further up - that and nothing else. Short of the gate every crossing is
    where it was. Lines through the ramp itself are the transition and are
    skipped; they are counted separately so that it is clear how much of the
    part went unchecked.
    """
    spanx = (min(p[0] for t in after for p in t), max(p[0] for t in after for p in t))
    spany = (min(p[1] for t in after for p in t), max(p[1] for t in after for p in t))
    wrong = []
    checked = skipped = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            if ramp[0] - 1e-9 <= x <= ramp[1] + 1e-9:
                skipped += 1
                x += step
                continue
            here = _column(after, x, y)
            there = _column(before, x, y)
            if x >= gate:
                there = sorted(h + amount if h >= at - 1e-6 else h for h in there)
            checked += 1
            if len(here) != len(there) or any(
                    abs(p - q) > 1e-3 for p, q in zip(here, there)):
                wrong.append((x, y, here, there))
            x += step
        y += step
    return checked, skipped, wrong


def verify_shaft(before, after, cx, cy, radius, to, step=0.23):
    """Prove a thinned shaft, the same way as a hole but from the outside in.

    A line straight up through the part must meet its surface where it did,
    everywhere but the ring of material the shaft has just given up. Then the
    new wall is found by walking inwards until the material starts, which says
    what the shaft actually came out at rather than what it was asked for.
    """
    spanx = (min(p[0] for t in after for p in t), max(p[0] for t in after for p in t))
    spany = (min(p[1] for t in after for p in t), max(p[1] for t in after for p in t))
    wrong = []
    checked = skipped = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            if to - 0.06 <= math.hypot(x - cx, y - cy) <= radius + 0.06:
                skipped += 1
                x += step
                continue
            here = _column(after, x, y)
            there = _column(before, x, y)
            checked += 1
            if len(here) != len(there) or any(
                    abs(p - q) > 1e-3 for p, q in zip(here, there)):
                wrong.append((x, y, here, there))
            x += step
        y += step
    # A shaft stands on something wider, so "where the material starts" finds
    # that instead. What marks the shaft out is that it alone reaches the top.
    top = max(p[2] for t in after for p in t)
    wall = []
    for deg in range(3, 360, 7):
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        r = radius + 0.40
        while r > max(0.05, to - 0.40):
            column = _column(after, cx + r * c, cy + r * s)
            if column and max(column) > top - 0.01:
                break
            r -= 0.005
        wall.append(r)
    return checked, skipped, wrong, (min(wall), max(wall))


def verify_slit(before, after, xa, xb, y0, y1, step=0.31, margin=0.06):
    """Prove the slot: the cavity empty, and every line beside it where it was.

    A line straight up inside the box must now meet no surface at all, and one
    outside it must meet the surface at the heights it met it before, since
    nothing moved. Lines within a margin of the box's own walls are left out,
    a line on a face being neither in nor out.
    """
    spanx = (min(p[0] for t in before for p in t), max(p[0] for t in before for p in t))
    spany = (min(p[1] for t in before for p in t), max(p[1] for t in before for p in t))
    wrong = []
    checked = inside = skipped = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            near_x = xa - margin < x < xa + margin or xb - margin < x < xb + margin
            near_y = y0 - margin < y < y0 + margin or y1 - margin < y < y1 + margin
            if (near_x and y0 - margin < y < y1 + margin) or (
                    near_y and xa - margin < x < xb + margin):
                skipped += 1
            elif xa < x < xb and y0 < y < y1:
                inside += 1
                if _column(after, x, y):
                    wrong.append((x, y, _column(after, x, y), []))
            else:
                checked += 1
                here, there = _column(after, x, y), _column(before, x, y)
                if len(here) != len(there) or any(
                        abs(p - q) > 1e-3 for p, q in zip(here, there)):
                    wrong.append((x, y, here, there))
            x += step
        y += step
    return checked, inside, skipped, wrong


def verify_hole(before, after, cx, cy, radius, to, step=0.23):
    """Prove the hole, the same way: by measuring the part, not the intention.

    A line straight up through the part must meet its surface exactly where it
    did, everywhere except the ring of material the hole has just taken. Lines
    inside that ring are the change itself and are counted, not checked. Then
    the new wall is found by walking outwards until the material starts, which
    says what the hole actually came out at rather than what it was asked for.
    """
    spanx = (min(p[0] for t in after for p in t), max(p[0] for t in after for p in t))
    spany = (min(p[1] for t in after for p in t), max(p[1] for t in after for p in t))
    wrong = []
    checked = skipped = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            if radius - 0.06 <= math.hypot(x - cx, y - cy) <= to + 0.06:
                skipped += 1
                x += step
                continue
            here = _column(after, x, y)
            there = _column(before, x, y)
            checked += 1
            if len(here) != len(there) or any(
                    abs(p - q) > 1e-3 for p, q in zip(here, there)):
                wrong.append((x, y, here, there))
            x += step
        y += step
    wall = []
    for deg in range(3, 360, 7):
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        r = max(0.05, to - 0.40)
        while r < to + 0.40:
            if _column(after, cx + r * c, cy + r * s):
                break
            r += 0.005
        wall.append(r)
    return checked, skipped, wrong, (min(wall), max(wall))

# -------------------------------------------------------------- what to cut out

# Every position below is given in the coordinates of the original STL files,
# which is what the measurements in --check report. Cutting one band moves
# everything beyond it, so the cuts are applied from the far end back: then each
# one is still where it was measured when its turn comes. The other operations
# follow, on positions that the cuts did not disturb.

# The piece, in millimetres: across the lane, along it, and thick. The default
# is the Belgian mignonette, the napolitain the files in input/images are
# already cut for, so build.py with nothing after it has nothing to do. Name
# another piece and it cuts the three parts down to that one instead:
#   python tools/resize/build.py --piece 40x30x7 --name small
# is the Swiss napolitain, laid in with its long side across the lane, which is
# what keeps its stroke short.
PIECE = (60.0, 39.0, 7.0)

# The standard parts, measured out of the files these are cut from.
LANE = (61.0, 40.0, 7.505)   # the lane: width, depth, clear height under the ledge
PLAY = (1.0, 1.0, 0.0)       # what a piece is given in each of the three
CRANK = 41.0                 # the arm's two holes, this far apart
PUSHER_FACE = 5.5            # the pushing face, which a piece has to be taller than
PIN_IN_SLOT = 4.69           # how far the pin hangs into the pusher's 4.71 mm slot

# Where a band is allowed to be. These are the only places in each part where a
# slab can come out without taking something with it, and the width is much the
# tightest of them: see the note at the top of the file.
WIDTH_BANDS = ((40.00, 47.00),    # the ledge's inner edge .. the bay's near post
               (74.00, 84.50))    # all but 1.03 of the slot between the bay and the
#                                 # servo tower, which is walled only below the headers
DEPTH_BAND = (65.00, 100.00)  # plain magazine wall, running back
RAIL_BAND = (-10.00, 19.99)   # the back of the rail, behind the pusher; the mouth
#                             # is the other end and nothing here touches it
LEDGE_AT = 8.00               # a slab pushed in here raises the ledge - and the servo box
ARM_BANDS = ((-55.49, -43.24), (-43.00, -39.10))   # 12.25, then 3.90 past two triangles
PUSHER_BANDS = (27.00, 48.00)    # two bands, each in its own gap between the ribs
PUSHER_LENGTH_BAND = -70.00      # between the pin slot and the pushing face
PIN_SLOT = (-83.248, -80.903)    # the pin's slot as the file has it: 2.345 wide
SLOT = 2.55                      # what its far wall is opened to. The 2.55 mm pin
#                                # wanted 2.80; this is the same 0.25 of play round
#                                # the 2.30 one, and the near wall, which the pin
#                                # pushes against, does not move either way
SLOT_X = (18.706, 74.994)        # how far the slot runs across the pusher
SLOT_BACK = 1.00                 # and how much nearer the pusher's back edge it
#                                # sits than the file has it, which leaves 2.25 mm
#                                # of plate behind it rather than 3.25. The pin
#                                # bears on the other wall, so that plate carries
#                                # the return and nothing else
SECOND_SLOT = 5.00               # a second slot, this much further in. The pin in
#                                # that one holds the pusher 5 mm further back
BORE = (-63.10, -10.00, 1.380, 1.550)    # the arm's pin hole, opened for the print
SHAFT = (-12.00, 79.00, 1.2765, 1.150)   # and the pin's shaft, pulled in to meet it

# How the travel follows from the lane, at anglePush 81 with the arm clamped
# 46.9 degrees back at rest.
STROKE_PER_MM = 1.291        # mm of stroke per mm of crank
STROKE_PER_MM_77 = 1.2451    # and at the standard unit's anglePush 77, square at rest
TAKE_UP = 1.90               # the face sits this far behind the stack at rest
OVERTRAVEL = 1.63            # and runs this far past the exit at full advance
PUSHER_SHORTEN = 10.00       # off the pushing face, which is what frees the rail
RAIL_REACH = 34.675          # the tail stops RAIL_REACH - stroke/2 short of the front
RAIL_SWUNG_BACK = 2.79       # and this much further again, the arm being clamped back


def plan(piece=PIECE, overtravel=OVERTRAVEL, take_up=TAKE_UP,
         shorten=PUSHER_SHORTEN, second=SECOND_SLOT, name='small', named=False):
    """Turn the piece's three dimensions into every number the cuts need.

    The depth and the height follow the piece exactly. The width does not: it
    follows the piece only while the piece is wide enough that the electronics
    are not the limit, which is from 53 mm across upwards. Below that the module
    bay, the channel its plugs reach into and the servo's pocket set the width,
    and the lane stays at 54.0 whatever the piece.
    """
    across, along, thick = piece
    notes = []

    room = sum(hi - lo for lo, hi in WIDTH_BANDS)
    want = LANE[0] - (across + PLAY[0])
    if want < -1e-9:
        raise SystemExit('a piece %.1f mm across wants a lane wider than the standard '
                         '%.1f mm, and nothing here can add material' % (across, LANE[0]))
    x_cut = round(min(want, room), 3)
    lane_w = LANE[0] - x_cut
    if want - x_cut > 1e-9:
        notes.append('the lane stays %.2f mm wide, %.2f wider than the piece asks for: '
                     '%.2f mm is the whole of the width that is neither the module bay '
                     'nor the servo pocket' % (lane_w, lane_w - across - PLAY[0], room))

    want = LANE[1] - (along + PLAY[1])
    if want < -1e-9:
        raise SystemExit('a piece %.1f mm along the lane wants it deeper than the '
                         'standard %.1f mm' % (along, LANE[1]))
    y_cut = round(min(want, DEPTH_BAND[1] - DEPTH_BAND[0]), 3)
    lane_d = LANE[1] - y_cut

    if thick < PUSHER_FACE:
        notes.append('a piece %.1f mm thick is shorter than the %.1f mm pushing face, '
                     'so the pusher can ride over it instead of moving it'
                     % (thick, PUSHER_FACE))
    lift = round(max(0.0, thick + PLAY[2] - LANE[2]), 3)
    if lift:
        notes.append('the ledge goes up %.2f mm to let a %.1f mm piece under it, and the '
                     'servo box rises with it, so the arm does too: the pin then hangs '
                     '%.2f mm into the pusher 4.71 mm slot instead of %.2f'
                     % (lift, thick, PIN_IN_SLOT - lift, PIN_IN_SLOT))

    standard_stroke = round(CRANK * STROKE_PER_MM_77, 3)
    settled = dict(piece=(across, along, thick), x_cut=x_cut, y_cut=y_cut, lift=lift,
                   take_up=take_up, second=second, name=name, notes=notes,
                   lane=(lane_w, lane_d, LANE[2] + lift))

    if not (x_cut or y_cut or lift):
        notes.append('this is the piece the parts in input/images are already cut for, '
                     'so the recipe for it is empty and the parts for it are those '
                     'files; --piece 40x30x7 --name small is the Swiss napolitain')
        settled.update(nothing=not named, copies=named, rail_cut=0.0, shorten=0.0,
                       crank=CRANK, arm_cut=0.0, stroke=standard_stroke,
                       overtravel=round(standard_stroke - lane_d - take_up, 2))
        return settled

    if not y_cut:
        notes.append('the lane keeps its depth, so the travel is the standard\'s: the '
                     'arm, the rail and the pushing face are left alone, and anglePush '
                     'stays at its default 77 with the arm square at rest')
        settled.update(rail_cut=0.0, shorten=0.0, crank=CRANK, arm_cut=0.0,
                       stroke=standard_stroke,
                       overtravel=round(standard_stroke - lane_d - take_up, 2))
        return settled

    crank = round((lane_d + take_up + overtravel) / STROKE_PER_MM, 2)
    stroke = round(crank * STROKE_PER_MM, 3)
    arm_cut = round(CRANK - crank, 3)
    arm_room = sum(hi - lo for lo, hi in ARM_BANDS)
    if arm_cut < -1e-9:
        raise SystemExit('this lane wants a crank of %.2f mm, longer than the arm has '
                         'at %.2f' % (crank, CRANK))
    if arm_cut - arm_room > 1e-9:
        raise SystemExit('this lane wants a crank of %.2f mm, and the bar between the '
                         'arm holes gives up only %.2f of its %.2f; a larger '
                         '--overtravel asks for a longer crank'
                         % (crank, arm_room, CRANK))
    if overtravel < 0.54:
        notes.append('%.2f mm past the exit is less than any arm this has been printed '
                     'with: the shortest that dispensed had 0.54' % overtravel)
    notes.append('set anglePush to 81 on this unit and clamp the arm about 47 degrees '
                 'back from square at rest, which is what the %.2f mm off the rail '
                 'depends on' % min(RAIL_REACH - stroke / 2 + RAIL_SWUNG_BACK,
                                    RAIL_BAND[1] - RAIL_BAND[0]))
    settled.update(rail_cut=round(min(RAIL_REACH - stroke / 2 + RAIL_SWUNG_BACK,
                                      RAIL_BAND[1] - RAIL_BAND[0]), 3),
                   shorten=shorten, crank=crank, arm_cut=arm_cut, stroke=stroke,
                   overtravel=overtravel)
    return settled


def share(total, bands):
    """Spread a width cut over the bands, as evenly as each one's room allows.

    An even split is what keeps the window in the back wall near the lane's
    centre, since one band lies below it and the other above.
    """
    take = [0.0] * len(bands)
    left = total
    while left > 1e-9:
        open_ = [n for n, (lo, hi) in enumerate(bands) if hi - lo - take[n] > 1e-9]
        if not open_:
            break
        step = left / len(open_)
        for n in open_:
            this = min(step, bands[n][1] - bands[n][0] - take[n])
            take[n] += this
            left -= this
    return [round(t, 3) for t in take]


def recipes(p):
    """The three recipes the plan asks for, in the form main() applies."""
    if p.get('nothing'):
        return []
    if p.get('copies'):
        # the empty recipe, under a name of its own: the same mesh, re-encoded
        return [(part, '%s-%s' % (part, p['name']), [])
                for part in ('body', 'pusher', 'arm')]
    body = []
    for (lo, _), take in zip(WIDTH_BANDS, share(p['x_cut'], WIDTH_BANDS)):
        if take:
            body.append(('cut', 'x', lo, round(lo + take, 3)))
    if p['y_cut']:
        body.append(('cut', 'y', DEPTH_BAND[0], DEPTH_BAND[0] + p['y_cut']))
    if p['rail_cut']:
        body.append(('cut', 'y', RAIL_BAND[0], RAIL_BAND[0] + p['rail_cut']))
    if p['lift']:
        body.append(('lift', 'z', LEDGE_AT, p['lift']))

    pusher = []
    if p['x_cut']:
        for start in PUSHER_BANDS:
            pusher.append(('cut', 'x', start, start + p['x_cut'] / 2))
    if p['shorten']:
        pusher.append(('cut', 'y', PUSHER_LENGTH_BAND,
                       PUSHER_LENGTH_BAND + p['shorten']))
    # the far wall out first, which widens the slot, then the near wall back,
    # which brings it to width again: neither order folds a face, and this one
    # never has the slot narrower than it ends up
    near = PIN_SLOT[1] - SLOT_BACK
    pusher.append(('plane', 'y', PIN_SLOT[0], round(near - SLOT - PIN_SLOT[0], 3)))
    if SLOT_BACK:
        pusher.append(('plane', 'y', PIN_SLOT[1], round(-SLOT_BACK, 3)))
    if p['second']:
        pusher.append(('slit', SLOT_X[0], round(SLOT_X[1] - p['x_cut'], 3),
                       round(near - SLOT + p['second'], 3),
                       round(near + p['second'], 3)))

    arm = []
    left = p['arm_cut']
    for lo, hi in ARM_BANDS:
        if left <= 1e-9:
            break
        take = min(left, hi - lo)
        arm.append(('cut', 'x', lo, round(lo + take, 3)))
        left -= take
    arm.append(('bore',) + BORE)

    return [('body', 'body-%s' % p['name'], body),
            ('pusher', 'pusher-%s' % p['name'], pusher),
            ('arm', 'arm-%s' % p['name'], arm),
            ('pin', 'pin-%s' % p['name'], [('shaft',) + SHAFT])]


def describe(p, parts):
    """What the plan comes to, before anything is cut."""
    print('a piece %.1f x %.1f x %.1f mm: across the lane, along it, and thick'
          % p['piece'])
    if parts:
        bands = len([op for op in parts[2][2] if op[0] == 'cut'])
        print('   lane     %6.2f x %6.2f x %5.2f   (the standard lane is '
              '%.2f x %.2f x %.2f)' % (p['lane'] + LANE))
        print('   body     %6.2f x %6.2f x %5.2f'
              % (p['lane'][0] + 3.0, 110.0 - p['y_cut'] - p['rail_cut'],
                 105.0 + p['lift']))
        print('   pusher   %6.2f x %6.2f%s'
              % (p['lane'][0] - 1.10, 56.0 - p['shorten'],
                 ', %.2f off its pushing face' % p['shorten'] if p['shorten']
                 else ', its length as it comes'))
        print('   slot     %6.2f wide for the 2.30 mm pin, %.2f nearer the back edge'
              % (SLOT, SLOT_BACK))
        print('            which holds the pusher %.2f further forward through the '
              'whole swing: %.1f deg on the arm\'s clamp at this crank'
              % (SLOT_BACK, math.degrees(SLOT_BACK / p['crank'])))
        if p['second']:
            print('   slot 2   %6.2f further in again, so the pin in that one holds it '
                  '%.2f back' % (p['second'], p['second']))
            print('            instead, %.1f deg the other way; the stroke is the same '
                  'either way' % math.degrees(p['second'] / p['crank']))
        print('   arm      %6.2f between its holes, %s'
              % (p['crank'], '%.2f out of the bar in %d band%s'
                 % (p['arm_cut'], bands, '' if bands == 1 else 's') if p['arm_cut']
                 else 'as it comes; only its pin hole is opened'))
        print('   stroke   %6.2f, with %.2f of take-up behind the stack and %.2f past '
              'the exit' % (p['stroke'], p['take_up'], p['overtravel']))
    else:
        print('   lane     %6.2f x %6.2f x %5.2f, the lane it already has'
              % p['lane'])
        print('   stroke   %6.2f at a crank of %.2f, with %.2f of take-up behind the '
              'stack and %.2f past the exit'
              % (p['stroke'], p['crank'], p['take_up'], p['overtravel']))
    for note in p['notes']:
        print('   note: %s' % note)
    print()


def options(argv):
    """--piece 40x30x7, --name small, and the three numbers of the travel."""
    out = dict(piece=PIECE, overtravel=OVERTRAVEL, take_up=TAKE_UP,
               shorten=PUSHER_SHORTEN, second=SECOND_SLOT, name='small',
               named='--name' in argv)
    keys = {'--piece': 'piece', '--name': 'name', '--overtravel': 'overtravel',
            '--take-up': 'take_up', '--pusher-shorten': 'shorten',
            '--second-slot': 'second'}
    for flag, key in keys.items():
        if flag not in argv:
            continue
        if argv.index(flag) + 1 >= len(argv):
            raise SystemExit('%s wants a value' % flag)
        value = argv[argv.index(flag) + 1]
        if key == 'piece':
            numbers = value.replace(',', 'x').replace('X', 'x').split('x')
            if len(numbers) != 3:
                raise SystemExit('--piece wants three numbers, as 40x30x7')
            out['piece'] = tuple(float(v) for v in numbers)
        elif key == 'name':
            out['name'] = value
        else:
            out[key] = float(value)
    if out['piece'] != PIECE and '--name' not in argv:
        raise SystemExit('--piece %s wants a --name as well, so that what it writes '
                         'does not land on another variant\'s files: '
                         '--piece 40x30x7 --name small is the Swiss napolitain'
                         % 'x'.join('%g' % v for v in out['piece']))
    return out

def main():
    check_only = '--check' in sys.argv
    settings = plan(**options(sys.argv))
    parts = recipes(settings)
    if '--union' in sys.argv:
        count = int(sys.argv[sys.argv.index('--union') + 1])
        which = ('body-%s' % settings['name'] if '--standard' not in sys.argv
                 else 'body')
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
    describe(settings, parts)
    if not parts:
        for part in ('body', 'pusher', 'arm', 'pin'):
            m = measure(load(os.path.join(IMAGES, 'spenser-%s.stl' % part)))
            print('spenser-%s.stl: %d triangles, %.0f mm3, %s%s' % (
                part, m['tris'], m['volume'],
                ' x '.join('%.2f..%.2f' % s for s in m['span']),
                '' if m['open_edges'] == 0 else '  (%d open edges)' % m['open_edges']))
        print('\nnothing written. Those four files are the design and this only ever '
              'reads them;\nto have the same mesh under another name, '
              '--name <slug> writes it out re-encoded.')
        return
    seen = set()
    for name, target_name, recipe in parts:
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
            elif op[0] == 'beyond':
                _, axis, at, amount, gate_axis, gate = op
                stepped, ramp, facets = lift_beyond(tris, axis, at, amount,
                                                    gate_axis, gate)
                checked, skipped, wrong = verify_beyond(tris, stepped, at, amount,
                                                        gate, ramp)
                if wrong:
                    raise SystemExit('%s: the step at %s = %.2f beyond %s = %.2f does not '
                                     'hold up: %d of %d lines disagree, first at x %.2f '
                                     'y %.2f' % ((target_name, axis, at, gate_axis, gate,
                                                  len(wrong), checked) + wrong[0][:2]))
                print('   stepped %s up %.2f mm at %s = %.2f, beyond %s = %.2f'
                      % (axis, amount, axis, at, gate_axis, gate))
                print('   %d triangles ramp it over %s %.2f..%.2f; %d lines either side '
                      'agree, %d through the ramp not looked at'
                      % (facets, gate_axis, ramp[0], ramp[1], checked, skipped))
                tris = stepped
            elif op[0] == 'slit':
                _, xa, xb, y0, y1 = op
                slotted, removed, columns = slit(tris, xa, xb, y0, y1)
                checked, inside, skipped, wrong = verify_slit(tris, slotted,
                                                              xa, xb, y0, y1)
                if wrong:
                    raise SystemExit('%s: the slot y %.3f..%.3f does not hold up: %d '
                                     'of %d lines disagree, first at x %.2f y %.2f'
                                     % ((target_name, y0, y1, len(wrong),
                                         checked + inside) + wrong[0][:2]))
                was, now = measure(tris), measure(slotted)
                lost = was['volume'] - now['volume']
                if abs(lost - removed) > 0.05:
                    raise SystemExit('%s: the slot y %.3f..%.3f took %.3f mm3, and the '
                                     'box it cut is %.3f'
                                     % (target_name, y0, y1, lost, removed))
                if now['open_edges'] != was['open_edges']:
                    raise SystemExit('%s: the slot y %.3f..%.3f left the mesh open: '
                                     '%d edges against %d'
                                     % (target_name, y0, y1, now['open_edges'],
                                        was['open_edges']))
                print('   cut a second slot %.2f mm wide at y %.3f..%.3f, running '
                      'x %.3f..%.3f over %d profiles'
                      % (y1 - y0, y0, y1, xa, xb, columns))
                print('   it took %.0f mm3, which is the box to 0.05; %d lines inside '
                      'it meet nothing, %d outside it agree, %d along its walls not '
                      'looked at' % (removed, inside, checked, skipped))
                tris = slotted
            elif op[0] == 'shaft':
                _, cx, cy, radius, to = op
                thinner, moved = widen_hole(tris, cx, cy, radius, to)
                checked, skipped, wrong, wall = verify_shaft(
                    tris, thinner, cx, cy, radius, to)
                if wrong:
                    raise SystemExit('%s: thinning the shaft at (%.2f, %.2f) does not '
                                     'hold up: %d of %d lines disagree, first at '
                                     'x %.2f y %.2f'
                                     % ((target_name, cx, cy, len(wrong),
                                         checked) + wrong[0][:2]))
                print('   pulled the shaft at (%.2f, %.2f) in from %.3f to %.3f mm '
                      'across' % (cx, cy, radius * 2, to * 2))
                print('   %d vertices moved, its wall now %.3f..%.3f from the axis; '
                      '%d lines elsewhere agree, %d in the ring it gave up not looked at'
                      % (moved, wall[0], wall[1], checked, skipped))
                tris = thinner
            elif op[0] == 'bore':
                _, cx, cy, radius, to = op
                wider, moved = widen_hole(tris, cx, cy, radius, to)
                checked, skipped, wrong, wall = verify_hole(
                    tris, wider, cx, cy, radius, to)
                if wrong:
                    raise SystemExit('%s: opening the bore at (%.2f, %.2f) does not '
                                     'hold up: %d of %d lines disagree, first at '
                                     'x %.2f y %.2f'
                                     % ((target_name, cx, cy, len(wrong),
                                         checked) + wrong[0][:2]))
                print('   opened the bore at (%.2f, %.2f) from %.3f to %.3f mm across'
                      % (cx, cy, radius * 2, to * 2))
                print('   %d vertices moved, its wall now %.3f..%.3f from the axis; '
                      '%d lines elsewhere agree, %d in the ring it took not looked at'
                      % (moved, wall[0], wall[1], checked, skipped))
                tris = wider
        after = measure(tris)
        target = os.path.join(IMAGES, 'spenser-%s.stl' % target_name)
        if os.path.normcase(os.path.abspath(target)) in SOURCES:
            raise SystemExit('refusing to write %s: the four parts it is cut from are '
                             'the design, and this only reads them'
                             % os.path.basename(target))
        save(target, tris)
        print('   -> %s: %d triangles, %.0f mm3, %s' % (
            os.path.relpath(target, ROOT).replace('\\', '/'), after['tris'],
            after['volume'], ' x '.join('%.2f..%.2f' % s for s in after['span'])))
        extra = after['open_edges'] - before['open_edges']
        print('   %s' % ('watertight' if after['open_edges'] == 0 else
                         'open edges: %d, %+d against the source'
                         % (after['open_edges'], extra)))
    if not check_only:
        print('\nthe standard pin is left as it is: spenser-pin.stl is the design')


if __name__ == '__main__':
    main()
