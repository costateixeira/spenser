#!/usr/bin/env python3
"""Resize the printed parts for a smaller piece of chocolate.

    python tools/resize/build.py                  # the Belgian mignonette: nothing
                                                  #   to cut, these parts are it
    python tools/resize/build.py --piece 40x30x7 --name small --flip
                                                  # the Swiss napolitain, which is
                                                  #   what the -small files are
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

  lane            61.0 x 40.0 mm  ->  43.50 x 31.0
  body            64 x 110 x 105  ->  46.50 x 80.8 x 105
  pusher          59.9 x 56.0     ->  42.40 x 46.0
  arm, pin holes  41.0 mm apart   ->  26.75
  stroke          51.05 mm        ->  33.76
  servo           cable to the magazine  ->  turned round, cable to the back,
                                      and its whole bay 6.50 mm back with it
  cable           nothing to run on  ->  the magazine's side wall carried 13.00
                                      forward over the tower, window and all
  module bay      24.00 mm wide   ->  unchanged; it is what sets the width
  retaining ledge z 9.0..10.0     ->  unchanged, and 3.61 mm clear of the arm
  servo box       unchanged       ->  unchanged, like every height in the body
  pusher slot     2.345 mm        ->  2.55, 1.00 nearer the edge, and a second
                                      one 5.00 further in again
  arm pin bore    2.760 mm        ->  3.10, as far as the method goes
  pin shaft       2.550 mm        ->  2.30, the other half of the same fit
  firmware        anglePush 78.6, and the arm set 44.5 deg back at rest

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

So the lane goes 61 -> 43.50 and no further, the body 64 -> 46.50, and a 40 mm
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

The servo's cable leaves the end of its case away from the shaft, which on this
body points at the magazine, so it has to be led back over the tower and round.
--flip turns the servo end for end in its pocket, and the cable comes out at the
back of the unit instead, against the body's own back face and open air.

Almost nothing about the pocket is in the way of that. The bay is 23.60 mm for a
case 23.20 long, the two ear seats are 5.00 and 4.70, and the flange screws are
symmetric about the case to within a tenth of a millimetre, so the case drops in
either way round. The one thing that is in the way is the opening in the floor,
which clears the two bosses on the gear face, and those are as off-centre as the
shaft is: 6.00 mm of the bay lies one side of it and 17.60 the other.

So turning the case round carries the shaft 11.60 mm towards the magazine, and
the mechanism cannot have that. 6.50 of it comes back by sliding the whole bay
into the base behind the tower, which is all there is - 6.60 mm, and the last
tenth is left alone because a cut landing exactly on the body's back face opens
the mesh along it. 5.00 of what is left costs nothing at all, because the
pusher's second slot already holds it 5.00 further back; the pin goes in that
one rather than the first. The 0.10 still over is inside the take-up, which
ends up 1.80 mm rather than 1.90.

What is left to pay is the arm, and it is paid in stroke. At rest the arm points
back at the magazine, and its far end stops 4.68 mm short of the wall the stack
leans on. The axis has moved 5.10 mm that way, so the clamp comes forward until
the far end clears it again: 44.5 degrees back from square instead of 46.9,
which is anglePush 78.6 instead of 81. The stroke goes 34.53 -> 33.76 and the
overtravel past the exit takes the loss, 1.63 -> 0.95, the lane and the take-up
being fixed. 0.95 is still above the 0.54 an arm that dispensed ran on.

Sliding the bay is three moves, a fill and two carves. The bay goes back by
cutting that much more off the rail, which only shortens the body, and pushing
the same thickness in again at the one clean seam the tower has. That seam is a narrow one: in front of the floor opening the tower's
underside slopes away to meet the magazine, and a slope cannot be cut across, so
the only plane that works lies in the 0.30 mm between where the opening stops
and where the slope starts. Pushing a slab in there puts the body's length back
and leaves the bay, its near seat and the tower's back wall where the cut took
them. The far seat's inner wall then comes back to meet them, so the bay is the
length it was, and the slope's leading edge is pushed forward out of the way of
what follows. Then the floor. The opening cannot simply be widened to take the bosses where
they now are. They stand 6.70 mm apart and the opening is barely wider than
they are, so the two positions overlap without either containing the other:
anything that covered both would be nearly the whole of the floor between the
seats, and a 12.20 mm case would have 12.00 mm of opening to sit over. So the
old opening is filled and a new one cut where the bosses are - the gear boss
against the bay's far end and the idler behind it - which leaves the plate
material at both ends of the bay instead of none. Last, a hole for the flange
screw, the bay having carried the flange away from the one it used; that one is
left where it is, in the middle of a shelf, doing nothing.

Filling needs nothing built from scratch. A hole that is filled has no wall any
more - what was a surface becomes the inside of the solid - so the wall goes,
and what closes the part again is the two rims it stood on: each edge the wall
had in a face of the plate, spanned back to a point inside the ring. Those rims
were already shared with the plate's own faces around the hole, so each ends up
used twice, as it was. Every face is one the part already had, or spanned from
an edge it already had, and what it did is measured afterwards like everything
else: the
volume it puts back has to be the hole, a line where the hole was has to meet
the plate's two faces and nothing else, and every line beside it has to meet
what it met.

The carves are the same operation as the pusher's second slot, told which heights
it owns. A slot through a plate can take everything above its footprint; an
opening in one plate of a part that has a base under it cannot, so the carve is
given a band of z and keeps to it. Inside that band the rule is the one every cut
here obeys - the band has to be a prism, so that the cavity is a copy of its
cross-section - and a thickness that straddles the band is refused rather than
sliced, because the cavity would then stop part way up it and need a floor. That
is why the slope's edge is moved first: it puts both carves on flat plate.

Turned round, the lead leaves at the back of the tower and has the length of
it to cross to the module's header - about 38 mm where it had 12 - so the body
gives it something to run against. The magazine's side wall on the motor side
stops being full height at y 37.8, where the lane ends; --flip carries it 12.70
mm further forward, to where the module rail opposite stops, with that rail's
own window through it to feed the lead in, and ties it across to the tower's
inner rail. The wall stands outside the pocket, which ends at x 80.502, so it
is clear of the servo and its ears at every point of fitting them, and the tie
stands on the tower's top past the pocket's far wall, so it roofs nothing the
servo has to come down through.

It is a wall, not a channel. What it stands on is 1.5 mm wide and a three-wire
servo lead is about 3.6 by 1.3, so the lead runs on edge against the wall
rather than inside anything. Something it could lie flat in would have to hang
outboard of the body, which is a wider change than this one.

Standing a box on the part is the one thing here that adds material, and it
adds it the way the body itself is built and the way --union stands lanes in
each other's side walls: as a closed box of its own, sunk into what it stands
on rather than welded to it. Nothing that is there is cut, so every edge keeps
the two triangles it had and the part is exactly as watertight as it was; what
makes the box part of the body is that the two share solid material, which is
what a slicer unions. Welding would mean cutting the face underneath, and on a
body built as a union of overlapping boxes every such cut grazes a seam
somewhere and leaves slivers - four of them, when it was tried that way. So the
wall is five boxes rather than one carved shape: a sill the width of it, a leg
at each end of the window, a head spanning between the legs, and the tie. The
window is simply the gap the legs leave.

What is checked is the same kind of thing as everywhere else. Over each corner
of the footprint the part's top has to be the face the box stands on, which is
both that there is something to stand on and that there is nothing above it -
the corners rather than the middle, because a head is carried at its ends and
spans air between them. Nothing over the footprint may reach above that face.
The volume has to grow by the box. And afterwards the part's top has to be the
box's top everywhere over the footprint, and exactly what it was everywhere
else.

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

    Where a point does have to be interpolated, it is interpolated from
    whichever end of the edge sorts first, never from the end this face
    happens to have come at it by. Two faces sharing an edge run along it in
    opposite directions, that being what consistent winding means, and
    `a + t(b - a)` worked from one end is the same point as from the other only
    in exact arithmetic. In floating point they differ - by a ten-thousandth of
    a millimetre on a long thin face, where the interpolation is ill
    conditioned - and then one edge of the part carries two points where it
    should carry one, which is an edge used four times, or once, in a mesh that
    is otherwise closed. Fixing the end fixes the point.
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
            p, q, dp, dq = (a, b, da, db) if a < b else (b, a, db, da)
            t = dp / (dp - dq)
            out.append(tuple(p[k] + t * (q[k] - p[k]) for k in range(3)))
    return out


def _area(t):
    """A triangle's area, for telling a face that has flattened from one that has not."""
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    return (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 / 2.0


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


def _outside(tris, xa, xb, y0, y1, zlo=None, zhi=None, tol=1e-7):
    """The part minus a box: every face cut by the box's four side planes.

    With a z window, only what lies between those two heights is dropped, so
    the same footprint can take one plate out of a part and leave another
    under it.


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
        cz = sum(p[2] for p in poly) / n
        if (xa + tol < cx < xb - tol and y0 + tol < cy < y1 - tol
                and (zlo is None or zlo - 1e-9 <= cz <= zhi + 1e-9)):
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


def _windowed(pairs, zlo, zhi, clip=False):
    """The thicknesses a carve owns, out of a whole column.

    All of them, if there is no window. Otherwise those lying wholly inside
    it; one that straddles it is refused, because the cavity would then stop
    part way up a thickness and need a floor, and a floor is not something the
    cross-section of a prism can give it.

    Clipping instead of refusing is for comparing profiles rather than cutting
    them: what stands outside the box may well carry on above the window, and
    only the part inside it is the carve's business.
    """
    if zlo is None:
        return pairs
    if clip:
        kept = [(max(lo, zlo), min(hi, zhi)) for lo, hi in pairs]
        return [p for p in kept if p[1] - p[0] > 1e-9]
    for lo, hi in pairs:
        if hi > zlo + 1e-9 and lo < zhi - 1e-9 and not (zlo - 1e-9 <= lo
                                                        and hi <= zhi + 1e-9):
            raise ValueError('the band carries material %.3f..%.3f, which crosses '
                             'the window %.3f..%.3f: a window takes whole '
                             'thicknesses or none' % (lo, hi, zlo, zhi))
    return [p for p in pairs if zlo - 1e-9 <= p[0] and p[1] <= zhi + 1e-9]


def _welded(tris, tol=2e-4):
    """Points closer together than `tol` made into one, and degenerates dropped.

    Cutting a face by one plane and then cutting the pieces by another leaves
    points a ten-thousandth of a millimetre apart on what is one point of the
    part: the arithmetic that put them there was not the same arithmetic both
    times. Nothing can be done about that while cutting, and nothing needs to
    be - a ten-thousandth is already finer than anything this body is built to,
    the closest two surfaces come being the 0.001 seams between the boxes it is
    a union of. So after a carve, points that close are made into one point,
    which makes two faces that share an edge share it exactly, and a face left
    with two corners in the same place is dropped. Dropping it keeps the part
    closed: its two long edges are the same edge traversed both ways and cancel,
    and the short one between those corners was its own.

    Points are bucketed on a grid of `tol` and looked for among the buckets
    next to their own, so a point near a bucket's edge still finds the point it
    belongs with.
    """
    seen = {}

    def one(p):
        at = tuple(int(math.floor(c / tol)) for c in p)
        for i in (0, -1, 1):
            for j in (0, -1, 1):
                for k in (0, -1, 1):
                    q = seen.get((at[0] + i, at[1] + j, at[2] + k))
                    if q is not None and all(abs(p[m] - q[m]) < tol for m in range(3)):
                        return q
        seen[at] = p
        return p

    out = []
    for t in tris:
        k = tuple(one(p) for p in t)
        if k[0] == k[1] or k[1] == k[2] or k[0] == k[2]:
            continue
        out.append(k)
    return out


def slit(tris, xa, xb, y0, y1, zlo=None, zhi=None, eps=1e-6):
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
    def outside_window(t):
        return zlo is not None and (max(p[2] for p in t) <= zlo + 1e-4
                                    or min(p[2] for p in t) >= zhi - 1e-4)

    standing = set()
    for t in tris:
        if max(p[1] for p in t) <= y0 + eps or min(p[1] for p in t) >= y1 - eps:
            continue
        if outside_window(t):
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
        if outside_window(t):
            continue
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
        spans.append(_windowed([(column[n], column[n + 1])
                               for n in range(0, len(column), 2)], zlo, zhi))
    for side, at in ((spans[0], xa - 0.07), (spans[-1], xb + 0.07)):
        column = _column(tris, at, middle)
        outer = _windowed([(column[n], column[n + 1])
                          for n in range(0, len(column), 2)], zlo, zhi, clip=True)
        if len(outer) != len(side) or any(abs(p - q) > 1e-4
                                         for u, v in zip(outer, side)
                                         for p, q in zip(u, v)):
            raise ValueError('the profile at x = %.3f is not the one the slot starts '
                             'in: %r against %r' % (at, outer, side))

    levels = sorted({round(v, 6) for s in spans for pair in s for v in pair})
    out = _outside(tris, xa, xb, y0, y1, zlo, zhi)
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
    return _welded(out), removed, len(edges) - 1


def _flat(t):
    """A face's height and plan area, if it lies flat, and nothing if it stands."""
    n = normal(t)
    if abs(n[2]) < 0.5:
        return None
    return t[0][2], abs(((t[1][0] - t[0][0]) * (t[2][1] - t[0][1])
                         - (t[2][0] - t[0][0]) * (t[1][1] - t[0][1])) / 2.0), n[2]


def _held(wall, caps, zhi, eps=1e-4):
    """What a hole held, from the flat faces that closed it above and below.

    Only a face lying flat carries any height - an upright wall carries none -
    so this is the plan area of each flat face times the height it lies at,
    counted positively where it closes the hole from above and negatively from
    below. Which way the wall itself is wound then does not come into it, and
    the same sum serves a hole straight through, where the two fans are all
    there is, and a pocket, whose own floor stands in for the lower fan.
    """
    total = 0.0
    for t in caps:
        at, area, _ = _flat(t)
        total += area * (at if abs(at - zhi) < eps else -at)
    for t in wall:
        lies = _flat(t)
        if lies:
            total -= math.copysign(1.0, lies[2]) * lies[0] * lies[1]
    return abs(total)


def plug(tris, xa, xb, y0, y1, zlo, zhi, cx, cy, eps=1e-4):
    """Fill a hole through a plate, or a pocket sunk into one.

    A hole that is filled has no wall any more: what was a surface becomes the
    inside of the solid. So the wall goes, and what closes the part again is
    the rim it stood on - each edge the wall had in either face of the plate,
    spanned back to (cx, cy), which has to be a point the whole rim can see.
    Those rims are already shared with the plate's own faces around the hole,
    so each ends up used twice, as it was.

    A hole straight through has two of them and gets two fans. A pocket sunk
    part way in, which is what a screw's hole in a seat turns out to be, has
    one, and its floor comes away with the wall, being a face lying inside the
    two heights; one fan then closes it. What it held is measured rather than
    reckoned - the wall and the fans together are a closed surface, and what
    that surface encloses is what has just been filled - so the two cases need
    no telling apart, and the check outside catches it if the heights given do
    not bracket a plate at all.

    Where the fan is cut afterwards matters. Close to (cx, cy) its triangles
    are narrow and nearly parallel, and a wall drawn through them there leaves
    vertices a thousandth of a millimetre apart on what should be one edge. So
    the point is put where the next carve will take it away, and what is left
    of the fan is cut far enough out that its triangles are wide.

    What the box takes is every face wholly inside it and wholly between the
    two heights: the wall, and anything the hole carries with it, such as the
    step this one has where its near end runs into the seat beside it. The
    pocket's own walls stand far higher and are left where they are.
    """
    wall, rest = [], []
    for t in tris:
        if (all(xa - eps < p[0] < xb + eps and y0 - eps < p[1] < y1 + eps
                and zlo - eps < p[2] < zhi + eps for p in t)
                and (abs(normal(t)[2]) < 1e-4
                     or all(zlo + eps < p[2] < zhi - eps for p in t))):
            wall.append(t)
        else:
            rest.append(t)
    if not wall:
        raise ValueError('nothing stands inside x %.3f..%.3f, y %.3f..%.3f between '
                         'z %.3f and %.3f: there is no hole there to fill'
                         % (xa, xb, y0, y1, zlo, zhi))

    caps = []
    for t in wall:
        for n in range(3):
            a, b = t[n], t[(n + 1) % 3]
            for at in (zhi, zlo):
                if abs(a[2] - at) > eps or abs(b[2] - at) > eps:
                    continue
                caps.append(((cx, cy, at), a, b))
    if not caps:
        raise ValueError('nothing between z %.3f and %.3f has an edge in either '
                         'face: this is neither a hole through a plate nor a '
                         'pocket sunk into one' % (zlo, zhi))
    return rest + caps, _held(wall, caps, zhi), len(wall)


def verify_plug(before, after, xa, xb, y0, y1, zlo, zhi, step=0.23, margin=0.06):
    """Prove the plug: the hole closed, and nothing else touched.

    A line straight up where the hole was must now meet the plate's two faces
    where it meets them all around, and must have met neither before. A line
    anywhere else must meet what it met. Lines within a margin of the box's
    walls are left out, a line on a face being neither in nor out.
    """
    spanx = (min(p[0] for t in before for p in t), max(p[0] for t in before for p in t))
    spany = (min(p[1] for t in before for p in t), max(p[1] for t in before for p in t))
    wrong = []
    checked = closed = skipped = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            here, there = _column(after, x, y), _column(before, x, y)
            if xa - margin < x < xb + margin and y0 - margin < y < y1 + margin:
                was = [h for h in there if zlo - 1e-3 <= h <= zhi + 1e-3]
                now = [h for h in here if zlo - 1e-3 <= h <= zhi + 1e-3]
                if was and now and len(was) == len(now):
                    skipped += 1          # outside the hole: the plate as it was
                elif not was and len(now) == 2 and abs(now[0] - zlo) < 1e-3 \
                        and abs(now[1] - zhi) < 1e-3:
                    closed += 1           # inside it: plate where there was none
                else:
                    skipped += 1          # on the rim, or under the seats
            else:
                checked += 1
                if len(here) != len(there) or any(abs(p - q) > 1e-3
                                                  for p, q in zip(here, there)):
                    wrong.append((x, y, here, there))
            x += step
        y += step
    return checked, closed, skipped, wrong


def _twice(loop):
    """Twice the signed area of a closed outline, positive anticlockwise."""
    return sum(loop[n][0] * loop[(n + 1) % len(loop)][1]
               - loop[(n + 1) % len(loop)][0] * loop[n][1]
               for n in range(len(loop)))


def _turned(loop):
    """The outline anticlockwise, whichever way round it came."""
    return list(loop) if _twice(loop) > 0 else list(loop)[::-1]


def _inside(loop, px, py):
    """Is (px, py) within the closed outline? By counting crossings."""
    inside = False
    for n in range(len(loop)):
        (x1, y1), (x2, y2) = loop[n], loop[(n + 1) % len(loop)]
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) / (y2 - y1) * (x2 - x1):
            inside = not inside
    return inside


def _middle(loop):
    """The middle of the outline's bounding box."""
    return (round((min(p[0] for p in loop) + max(p[0] for p in loop)) / 2.0, 4),
            round((min(p[1] for p in loop) + max(p[1] for p in loop)) / 2.0, 4))


def outlines(tris, zlo, zhi, eps=1e-4):
    """Every hole's own outline, where it runs straight through one plate.

    A hole through a plate has a wall of upright faces, and the top edge of
    that wall, chained end to end, is the hole's outline. The two heights pick
    the walls out: a wall that carries on past the plate, a pocket's side or a
    seat's, has faces outside them and is left where it is. What comes back is
    one closed outline for each hole, anticlockwise.
    """
    step = {}
    for t in tris:
        if abs(normal(t)[2]) > 1e-4:
            continue
        if not all(zlo - eps < p[2] < zhi + eps for p in t):
            continue
        for n in range(3):
            a, b = t[n], t[(n + 1) % 3]
            if abs(a[2] - zhi) < eps and abs(b[2] - zhi) < eps:
                step.setdefault((round(a[0], 4), round(a[1], 4)),
                                (round(b[0], 4), round(b[1], 4)))
    loops, seen = [], set()
    for start in step:
        if start in seen:
            continue
        loop, at = [], start
        while at in step and at not in seen:
            seen.add(at)
            loop.append(at)
            at = step[at]
        if len(loop) > 2 and at == start:
            loops.append(_turned(loop))
    return loops


def outline(tris, px, py, zlo, zhi):
    """The outline of the one hole that goes round (px, py)."""
    found = [loop for loop in outlines(tris, zlo, zhi) if _inside(loop, px, py)]
    if len(found) != 1:
        raise ValueError('%d outlines between z %.3f and %.3f go round (%.3f, %.3f), '
                         'and exactly one has to'
                         % (len(found), zlo, zhi, px, py))
    return found[0]


def _kernel(loop, eps=1e-3):
    """The point the outline is best seen from, or nothing.

    Every edge has to be seen from it, which for an anticlockwise outline means
    lying to the left of all of them at once. Which such point is used matters,
    not only that there is one: the ray that zips the ground turns about it, and
    off to one side it sweeps the near edges slowly and the far ones in a rush,
    which leaves triangles so flat that they come out the wrong way round. So
    what is wanted is the point furthest from every edge at once - the middle of
    a circle, the middle of the lens where two circles run together - and it is
    found by walking the bounding box and then closing in on the best of it.
    """
    edges = [(loop[n], loop[(n + 1) % len(loop)]) for n in range(len(loop))]

    def clearance(x, y):
        return min(((b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0]))
                   / math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in edges)

    xs = [p[0] for p in loop]
    ys = [p[1] for p in loop]
    step = min(max(xs) - min(xs), max(ys) - min(ys)) / 24.0
    best, at = None, None
    y = min(ys)
    while y <= max(ys):
        x = min(xs)
        while x <= max(xs):
            deep = clearance(x, y)
            if best is None or deep > best:
                best, at = deep, (x, y)
            x += step
        y += step
    for _ in range(12):
        step /= 2.0
        for dx, dy in ((step, 0.0), (-step, 0.0), (0.0, step), (0.0, -step)):
            deep = clearance(at[0] + dx, at[1] + dy)
            if deep > best:
                best, at = deep, (at[0] + dx, at[1] + dy)
    return at if best > eps else None


def _between(outer, inner, apex):
    """Cover the ground inside `outer` and outside `inner` with triangles.

    Both outlines have to be ones the apex sees all of, and then a ray turning
    about the apex crosses each exactly once, so the two can be zipped: take
    their vertices in the order the ray reaches them, and each step closes one
    triangle against the vertex the other outline is resting on. Every edge of
    either outline is used once and once only, so the ground between them comes
    out covered exactly - which is what the areas prove afterwards.
    """
    def angles(loop):
        return [math.atan2(p[1] - apex[1], p[0] - apex[0]) for p in loop]

    # Where the two outlines are joined first matters: that seam has to be a
    # line lying in the ground between them, so the vertex it starts from is
    # the one of `outer` last reached before the ray reaches `inner`'s first.
    ai = angles(inner)
    start = min(range(len(inner)), key=lambda n: ai[n])
    i = list(inner[start:]) + list(inner[:start])
    behind = [(a - ai[start]) % (2.0 * math.pi) for a in angles(outer)]
    start = max(range(len(outer)), key=lambda n: behind[n])
    o = list(outer[start:]) + list(outer[:start])
    base = angles(o)[0]
    ao = [(a - base) % (2.0 * math.pi) for a in angles(o)]
    ai = [(a - base) % (2.0 * math.pi) for a in angles(i)]
    ao[0] = 0.0
    out = []
    m, n = len(o), len(i)
    j = k = 0
    while j < m or k < n:
        if k >= n:
            take = True
        elif j >= m:
            take = False
        else:
            take = ((ao[j + 1] if j + 1 < m else ao[0] + 2.0 * math.pi)
                    <= (ai[k + 1] if k + 1 < n else ai[0] + 2.0 * math.pi))
        if take:
            out.append((o[j % m], o[(j + 1) % m], i[k % n]))
            j += 1
        else:
            out.append((i[(k + 1) % n], i[k % n], o[j % m]))
            k += 1
    return out


def panel(tris, x0, x1, y0, y1, zlo, zhi, hole, side=1.5):
    """Put a plate back into a slot, with an outline left open through it.

    Every carve here cuts a box, and the holes the servo needs are round, so a
    round hole that has to move cannot just be cut where it now belongs. What
    can be done is to cut the box wide of it and put the plate back with the
    right outline left open: the box takes the floor away and this stands a
    plate of the floor's own thickness in its place, with the hole through it.

    It is added the way `boss` adds a box and the way the body itself is built,
    as a closed solid of its own lapping over what is already there rather than
    welded to it, so nothing standing is cut and every edge keeps the two
    triangles it had. The lap is what makes it one piece with the floor around
    it: the two share solid material, which is what a slicer unions.

    The plate is two flat faces, a wall round its edge and a wall round the
    hole. The faces are the ground between the two outlines, zipped about a
    point that can see the hole's (see `_between`); the plate's own edge is
    first cut into lengths of about `side`, so the triangles reaching across to
    the hole are not slivers. What is proved here is the covering - every
    triangle anticlockwise, and their areas adding up to the plate less the
    hole - and what is proved outside is the solid.
    """
    ring = _turned(hole)
    # The plate's edge is cut into lengths of about the hole's own, so that the
    # ray zipping the two sweeps them at the same rate and no triangle between
    # them comes out flat enough to turn over.
    side = min(side, max(0.1, sum(math.hypot(ring[(n + 1) % len(ring)][0] - ring[n][0],
                                             ring[(n + 1) % len(ring)][1] - ring[n][1])
                                  for n in range(len(ring))) / len(ring)))
    rect = _turned([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    edge = []
    for n in range(4):
        a, b = rect[n], rect[(n + 1) % 4]
        steps = max(4, int(math.hypot(b[0] - a[0], b[1] - a[1]) / side))
        for s in range(steps):
            edge.append((a[0] + (b[0] - a[0]) * s / steps,
                         a[1] + (b[1] - a[1]) * s / steps))
    for p in ring:
        if not (x0 < p[0] < x1 and y0 < p[1] < y1):
            raise ValueError('the outline reaches (%.3f, %.3f), outside the plate '
                             'x %.3f..%.3f y %.3f..%.3f that has to carry it'
                             % (p[0], p[1], x0, x1, y0, y1))
    apex = _kernel(ring)
    if apex is None:
        raise ValueError('no point inside the outline can see the whole of it, so '
                         'the ground around it cannot be zipped')
    ground = _between(edge, ring, apex)
    want = (_twice(edge) - _twice(ring)) / 2.0
    got = 0.0
    for a, b, c in ground:
        area = ((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2.0
        if area <= 0.0:
            raise ValueError('a triangle of the plate comes out inside out near '
                             '(%.3f, %.3f): the two outlines do not zip'
                             % (a[0], a[1]))
        got += area
    if abs(got - want) > 1e-6 * max(1.0, want):
        raise ValueError('the plate\'s triangles cover %.6f mm2 where the plate less '
                         'its hole is %.6f: they overlap, or leave a gap'
                         % (got, want))

    out = list(tris)
    for a, b, c in ground:
        out.append(((a[0], a[1], zhi), (b[0], b[1], zhi), (c[0], c[1], zhi)))
        out.append(((c[0], c[1], zlo), (b[0], b[1], zlo), (a[0], a[1], zlo)))
    for loop, inward in ((edge, False), (ring, True)):
        for n in range(len(loop)):
            a, b = loop[n], loop[(n + 1) % len(loop)]
            if inward:
                a, b = b, a
            out.append(((a[0], a[1], zlo), (b[0], b[1], zlo), (b[0], b[1], zhi)))
            out.append(((a[0], a[1], zlo), (b[0], b[1], zhi), (a[0], a[1], zhi)))
    return _welded(out), want * (zhi - zlo), len(ground) * 2 + (len(edge) + len(ring)) * 2


def verify_panel(before, after, x0, x1, y0, y1, zlo, zhi, hole,
                 step=0.23, margin=0.08):
    """Prove the plate: solid where it stands, open through the hole, else untouched.

    Over the plate's own ground a line straight up has to meet two faces more
    than it did, at the plate's two heights. Through the hole it has to meet
    exactly what it met, which is nothing, the box having taken it away. A line
    anywhere else has to meet what it met. Lines within a margin of either
    outline are left out, a line on a face being neither in nor out.
    """
    spanx = (min(p[0] for t in before for p in t), max(p[0] for t in before for p in t))
    spany = (min(p[1] for t in before for p in t), max(p[1] for t in before for p in t))
    wrong = []
    checked = standing = through = skipped = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            if x0 - margin < x < x1 + margin and y0 - margin < y < y1 + margin:
                here = sorted(h for h in _column(after, x, y)
                              if zlo - 1e-3 <= h <= zhi + 1e-3)
                was = sorted(h for h in _column(before, x, y)
                             if zlo - 1e-3 <= h <= zhi + 1e-3)
                if (not (x0 + margin < x < x1 - margin and y0 + margin < y < y1 - margin)
                        or min(math.hypot(x - p[0], y - p[1]) for p in hole) < margin):
                    skipped += 1
                elif _inside(hole, x, y):
                    if here == was:
                        through += 1
                    else:
                        wrong.append((x, y, here, was))
                else:
                    want = sorted(was + [zlo, zhi])
                    if len(here) == len(want) and all(abs(p - q) < 1e-3
                                                      for p, q in zip(here, want)):
                        standing += 1
                    else:
                        wrong.append((x, y, here, want))
            else:
                checked += 1
                here, was = _column(after, x, y), _column(before, x, y)
                if len(here) != len(was) or any(abs(p - q) > 1e-3
                                                for p, q in zip(here, was)):
                    wrong.append((x, y, here, was))
            x += step
        y += step
    return checked, standing, through, skipped, wrong


def boss(tris, xa, xb, y0, y1, at, to, sink=1.0, lap=0.0, hang=False, slope=None,
         eps=5e-4):
    """Stand a box on the part: the one operation here that adds material.

    It adds it the way the body itself is built and the way `union` stands
    lanes in each other's side walls - as a closed box of its own, sunk into
    what it stands on rather than welded to it. Nothing that is there is cut,
    so every edge keeps the two triangles it had and the part is exactly as
    watertight as it was; what makes the box part of the body is that the two
    share solid material, which is what a slicer unions. Welding instead would
    mean cutting the face under it, and on a body built as a union of
    overlapping boxes every such cut grazes a seam somewhere and leaves
    slivers.

    What is checked is that the box has something to stand on and nothing to
    foul. Over each corner of the footprint the part's top surface has to be
    the face at `at`, which is both at once: it is there, and there is nothing
    above it. The corners rather than the middle, because a lintel is carried
    at its ends and spans air between them. Everywhere over the footprint the
    part must stop at or below `at`, or the box would run into something.

    A box may also run into a wall at the `xa` end, which is the same idea
    sideways: `lap` is how far past that wall's face it goes, and over that
    much of the footprint nothing is asked about `at`, because there the box
    is meant to be inside material. What is asked instead is that the material
    really is a wall the box's own height - its surface met under the box's
    base and not again below the box's top - so an end that laps is carried as
    surely as one standing on a face, and the two share solid material rather
    than a face.

    A box that `hang`s has nothing under it at all: `at` is its own underside
    rather than a face it stands on, and it is held by what it laps into, so
    it must lap. The part of the body this one belongs to is built that way
    throughout - the bay's floor and the bezel on the front of its wall both
    start at z 25.000 with air below them - so there is no face to stand on
    there and standing on the one under all of it, the lane's floor, would
    close the front of the body down to the ground.

    `slope` gives that underside a second height, at the `y1` edge, so it is a
    plane falling across the box rather than flat. It is what carries a bevel
    on: the ledge under the bay has one, and a box put beside it with a level
    bottom reads as a floor hanging in the body instead of as the same ledge
    going further. The underside stays planar, so the box is still six flat
    faces, and the two end walls are trapezia rather than rectangles.
    """
    if hang and not lap:
        raise ValueError('a box that hangs has to lap into something: nothing else '
                         'would hold it')
    base = at if hang else at - sink
    far = base if slope is None else slope

    def under(y):
        return base + (far - base) * (y - y0) / (y1 - y0)

    ca = xa + lap
    if lap:
        # the underside at the corner, not a thousandth in, so that a sloping
        # one is not asked to be clear of the face it starts on
        for y, low in ((y0 + 1e-3, base), (y1 - 1e-3, far)):
            x = xa + lap / 2.0
            column = _column(tris, x, y)
            if (not column or max(column) < to - eps
                    or any(low + eps < p < to - eps for p in column)):
                raise ValueError('the box laps %.3f into the wall at x = %.3f, but over '
                                 '(%.3f, %.3f) the part is not solid from %.3f to %.3f: '
                                 'its surface is met at %s'
                                 % (lap, ca, x, y, low, to,
                                    ', '.join('%.3f' % p for p in column) or 'nothing'))
    for x, y in ([] if hang else [(xb, y0), (xb, y1)] if lap else
                 [(ca, y0), (xb, y0), (ca, y1), (xb, y1)]):
        x = min(max(x, ca + 1e-3), xb - 1e-3)
        y = min(max(y, y0 + 1e-3), y1 - 1e-3)
        column = _column(tris, x, y)
        if not column or abs(max(column) - at) > eps:
            raise ValueError('the part stops at %s over the corner (%.3f, %.3f), not at '
                             'z = %.3f: a box has to stand on a face, with nothing above'
                             % ('%.3f' % max(column) if column else 'nothing', x, y, at))
    step = max(0.17, min(xb - ca, y1 - y0) / 4.0)
    y = y0 + step / 2.0
    while y < y1:
        low = under(y) if hang else at
        x = ca + step / 2.0
        while x < xb:
            column = _column(tris, x, y)
            if column and max(column) > low + eps:
                raise ValueError('the part reaches z = %.3f at (%.3f, %.3f), above the '
                                 'face at %.3f the box stands on'
                                 % (max(column), x, y, low))
            x += step
        y += step

    c = [(xa, y0), (xb, y0), (xb, y1), (xa, y1)]
    out = list(tris)
    quad = [(p[0], p[1], under(p[1])) for p in c][::-1]
    out += [(quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])]
    quad = [(p[0], p[1], to) for p in c]
    out += [(quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])]
    for n in range(4):
        a, b = c[n], c[(n + 1) % 4]
        out += [((a[0], a[1], under(a[1])), (b[0], b[1], under(b[1])), (b[0], b[1], to)),
                ((a[0], a[1], under(a[1])), (b[0], b[1], to), (a[0], a[1], to))]
    return out, (xb - xa) * (y1 - y0) * ((to - base) + (to - far)) / 2.0


def filed(tris, xa, xb, y0, y1, now, flat, knee, floor, tol=1e-4):
    """One flat face taken up onto another plane, the way a file would do it.

    `now` is the plane the face is to lie on, as `(c, m)` for z = c + m*y; it
    does not turn in x, which is what a bevel on this body is. Every point of
    the part that is under it, inside the footprint and over `floor`, moves
    straight up onto it, which takes the face and everything the file would
    have taken with it. It only comes up as far as `flat` - the underside of
    what sits on the face - so in front of `knee`, where the new plane is over
    that, the face comes up flat instead.

    Nothing is cut and nothing is added, so the mesh is exactly as closed as
    it was; what changes is where its points are. The faces that met the old
    one stretch to follow it, which is the same move `move_plane` makes and
    carries the same risk, so the same proof is taken: no face may come out
    inside out.

    The part is split across at `knee` first, so the face has points there to
    turn on. Without them a triangle spanning the turn cuts the corner, and
    the widest span on this face is 11 mm, which would miss it by 2.
    """
    split = []
    for t in tris:
        poly = list(t)
        if all(abs(p[1] - knee) < tol for p in poly):
            split.append(poly)
            continue
        for below in (True, False):
            piece = _clip(poly, 1, knee, below)
            if len(piece) >= 3:
                split.append(piece)
    start = []
    for poly in split:
        start += _fan(poly)

    def onto(y):
        return min(flat, now[0] + now[1] * y)

    moved, hits, flattened = [], 0, 0
    for t in start:
        new = []
        for p in t:
            if (floor < p[2] < onto(p[1]) + tol
                    and xa - tol <= p[0] <= xb + tol
                    and y0 - tol <= p[1] <= y1 + tol):
                hits += 1
                new.append((p[0], p[1], onto(p[1])))
            else:
                new.append(p)
        new = tuple(new)
        n1, n2 = normal(t), normal(new)
        if n2 == (0.0, 0.0, 0.0) or abs(n2[2]) > 0.999999 and _area(new) < 1e-9:
            # the whole face went onto the plane: it had been under the part's
            # own surface and is now in it, with no thickness left to bound
            flattened += 1
            continue
        if n1 != (0.0, 0.0, 0.0) and sum(u * v for u, v in zip(n1, n2)) < 0:
            raise ValueError('filing onto z = %.3f %+.3f y turns a face inside out, '
                             'at %r' % (now[0], now[1], new))
        moved.append(new)
    if not hits:
        raise ValueError('nothing lies under z = %.3f %+.3f y inside x %.3f..%.3f, '
                         'y %.3f..%.3f' % (now[0], now[1], xa, xb, y0, y1))
    return _welded(moved), hits, flattened


def verify_filed(before, after, xa, xb, y0, y1, now, flat, floor, step=0.29,
                 margin=0.08):
    """Prove it: inside the footprint the part's underside is the new plane.

    A line up through it has to meet the part first at the new plane, or not
    at all, once what is under `floor` is left out; a line outside has to meet
    it exactly where it did. Lines within a margin of a side are left out, a
    line on a wall being neither in nor out.
    """
    spanx = (min(p[0] for t in before for p in t), max(p[0] for t in before for p in t))
    spany = (min(p[1] for t in before for p in t), max(p[1] for t in before for p in t))
    wrong = []
    checked = filed_n = skipped = 0
    y = spany[0] + 0.113
    while y < spany[1]:
        x = spanx[0] + 0.137
        while x < spanx[1]:
            if (xa - margin < x < xa + margin or xb - margin < x < xb + margin
                    or y0 - margin < y < y0 + margin or y1 - margin < y < y1 + margin):
                skipped += 1
            elif xa < x < xb and y0 < y < y1:
                filed_n += 1
                over = min(flat, now[0] + now[1] * y)
                under = [p for p in _column(after, x, y) if floor < p < over - 1e-3]
                if under:
                    wrong.append((x, y, under, []))
            else:
                checked += 1
                here, was = _column(after, x, y), _column(before, x, y)
                if len(here) != len(was) or any(abs(p - q) > 1e-3
                                                for p, q in zip(here, was)):
                    wrong.append((x, y, here, was))
            x += step
        y += step
    return checked, filed_n, skipped, wrong


def verify_boss(before, after, xa, xb, y0, y1, at, to, step=0.23, margin=0.06):
    """Prove the box: the part's top is its top where it stands, and nowhere else.

    A box that overlaps rather than welds meets a line more times than the
    face it replaced did, so what is checked is not the whole column but the
    top of it: over the footprint the part must now stop at the box's top, and
    anywhere else it must stop exactly where it stopped. Lines within a margin
    of the box's walls are left out, a line on a face being neither in nor out.
    """
    spanx = (min(p[0] for t in before for p in t), max(p[0] for t in before for p in t))
    spany = (min(p[1] for t in before for p in t), max(p[1] for t in before for p in t))
    wrong = []
    checked = stood = skipped = 0
    y = spany[0] + 0.137
    while y < spany[1]:
        x = spanx[0] + 0.113
        while x < spanx[1]:
            here, there = _column(after, x, y), _column(before, x, y)
            top = max(here) if here else None
            was = max(there) if there else None
            if xa < x < xb and y0 < y < y1:
                if top is None or abs(top - to) > 1e-3:
                    wrong.append((x, y, [top], [to]))
                else:
                    stood += 1
            elif (xa - margin < x < xb + margin and y0 - margin < y < y1 + margin):
                skipped += 1
            else:
                checked += 1
                if (top is None) != (was is None) or (
                        top is not None and abs(top - was) > 1e-3):
                    wrong.append((x, y, [top], [was]))
            x += step
        y += step
    return checked, stood, skipped, wrong


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


_CELL = 2.0
_GRIDS = []


def _grid(tris):
    """Faces bucketed by where they stand in plan, so a line need not try them all.

    Every check here casts lines straight up through the part and asks what
    they meet, tens of thousands of them for each carve, and a line can only
    meet a face standing over the ground it passes through. Bucketing the faces
    by that ground turns each line from a trawl of the whole part into a look
    at one bucket. A face goes in every bucket its own plan extent touches, so
    nothing a line could meet is ever missed, and what comes back is exactly
    what trying them all came back with.

    The buckets are kept against the list they were built from, by identity, so
    that a pass comparing two lists builds each one once. The list itself is
    held as well, or another list could land on the same identity later.
    """
    for held, cells in _GRIDS:
        if held is tris:
            return cells
    cells = {}
    for t in tris:
        lo = (int(math.floor(min(p[0] for p in t) / _CELL)),
              int(math.floor(min(p[1] for p in t) / _CELL)))
        hi = (int(math.floor(max(p[0] for p in t) / _CELL)),
              int(math.floor(max(p[1] for p in t) / _CELL)))
        for i in range(lo[0], hi[0] + 1):
            for j in range(lo[1], hi[1] + 1):
                cells.setdefault((i, j), []).append(t)
    _GRIDS.append((tris, cells))
    del _GRIDS[:-4]
    return cells


def _column(tris, x, y):
    """Heights at which a line straight up through (x, y) meets the surface."""
    out = []
    for (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) in _grid(tris).get(
            (int(math.floor(x / _CELL)), int(math.floor(y / _CELL))), ()):
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


def verify_slit(before, after, xa, xb, y0, y1, zlo=None, zhi=None,
                step=0.31, margin=0.06):
    """Prove the slot: the cavity empty, and every line beside it where it was.

    A line straight up inside the box must now meet no surface at all - or,
    where the carve was given a window, exactly the surfaces it met outside
    that window and none of those within it - and one outside the box must meet
    the surface at the heights it met it before, since nothing moved. Lines within a margin of the box's own walls are left out,
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
                here = _column(after, x, y)
                want = [] if zlo is None else [
                    h for h in _column(before, x, y)
                    if not zlo - 1e-3 <= h <= zhi + 1e-3]
                if len(here) != len(want) or any(
                        abs(p - q) > 1e-3 for p, q in zip(here, want)):
                    wrong.append((x, y, here, want))
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
# Turning the servo round in its pocket, so that its cable leaves at the back
# of the unit instead of towards the magazine. Nothing about the pocket is in
# the way of that except the opening in its floor: the bay, both ear seats and
# the screws are symmetric about the case, but the opening clears the two
# bosses on the servo's gear face and those are as off-centre as the shaft is.
# The case is not symmetric about its shaft either - 6.00 mm of the bay lies
# one side of it and 17.60 the other - so a case turned end for end carries the
# shaft 11.60 mm towards the magazine, which the mechanism cannot have. The bay
# goes back into the base behind the tower to give most of it back.
FLIP_FRAME = (17.500, 20.198)  # Every number from here to the end of the cable wall
#                              # was measured on the small body, which is the standard
#                              # one with the whole 17.500 mm of width taken out of it
#                              # and 20.198 off its rail. A piece that cuts less leaves
#                              # the same features that much further out and further
#                              # back, so the recipe is offset by the difference and
#                              # the flip is a change to any body, not only that one.
FLIP_BAY = 7.000               # Of that width this much came out below the module
#                              # bay's outer wall, in the band at x 40..47, and the
#                              # rest above it. So the bay's own wall moves by one
#                              # amount and everything outboard of the slot by the
#                              # other, and the slot between them changes width.
SLOT_WIDE = 11.525             # It is this wide before anything is cut, and the band
SLOT_SHUT = 1.50               # at x 74..84.50 takes up to 10.50 of it. The bay's outer
#                              # face is only taken out to meet the rail when what is
#                              # left is narrower than this - a crack, which on the
#                              # small body is the 1.025 the band cannot reach. Wider
#                              # than that, moving the face would stand a block of
#                              # solid the height of the body in the slot and take the
#                              # room beside the module's headers with it, so the slot
#                              # is left and the wall is prolonged across it instead.
BAY = (3.102, 26.702)         # the case bay, between the ear seats: 23.60 for a
#                             # case 23.20 long
FLIP_SLIDE = 6.50             # how far back the bay goes: all but a tenth of the
#                             # base behind the tower, which leaves its back wall
#                             # level with the body's own back face. The last tenth
#                             # is left because a cut landing exactly on that face
#                             # opens the mesh along it
SHAFT_AT = 9.102              # the servo axis, 6.00 from one end of that bay
TOWER_BACK = 16.797           # the tower's back wall, this far up the standard body,
#                             # which is as far back as the bay can be taken
OPENING = (68.447, 80.452)    # the floor opening, as wide as the one in the file:
#                             # a fifth of a millimetre inside each pocket wall. It
#                             # is two overlapping circles, 12.005 across on the
#                             # shaft and 5.68 on the boss beside it
IDLER = 6.700                 # which stands this far along from the shaft, and
IDLER_WIDE = 2.840            # wants this much of radius round it
OPENING_END = 18.704          # where the opening stops, which is the tower's one
#                             # clean seam: in front of it the floor's underside slopes
BUTTRESS = 19.002             # away, from here to the magazine
BUTTRESS_FORWARD = 4.50       # so that edge is pushed this far forward, and both
#                             # carves then land on flat plate
SCREWS = (0.599, 28.906)      # the flange screws' holes, at x 74.356
SCREW = (74.356, 1.600)       # and 1.60 across
FLOOR_UNDER = 17.500          # the floor's underside, and
FLOOR_Z = (16.00, 19.248)     # the heights the floor opening owns: up to the top
#                             # of the floor and no further, so that the far seat's
#                             # wall, which stands in the same plane as the opening's
#                             # far end, is left out of it
SEAT_Z = (17.00, 23.10)       # and the heights the far screw's hole goes through
# Three holes the servo needs through a plate, and all three are round: the
# floor opening its two bosses drop through, the far flange screw's hole, and
# the screwdriver's hole in the base, under the shaft. Every carve here cuts a
# box, so a round hole that has to move is read off the part first, filled, and
# punched again where it now belongs with its own outline open through it.
FLOOR_PLATE = (17.500, 19.248)   # the floor plate the opening runs through
SEAT_PLATE = (17.500, 23.089)    # the floor and the far seat together, which the
#                                # flange screw's hole runs through
BASE_PLATE = (0.000, 1.498)      # and the base, which the screwdriver's hole does
BASE_CUT = (-0.500, 2.000)       # and the box for it is cut from below the base to
#                                # clear air above, so that no face of the base lies
#                                # within a float's width of a wall of the box
FAR_SCREW = (74.3245, 28.9025)   # the design's far flange screw hole, which the bay
#                                # slides out from under: its outline is punched again
#                                # where the flange now is, and the old one filled
DRIVER = (74.5005, 9.3020)       # the screwdriver's hole in the base. The design has
#                                # it 0.20 off the axis and 0.05 off in x; punched
#                                # again, it is put on the axis
PLATE_LAP = 0.35                 # how far a plate put back laps over what is there
SCREW_WIDE = 0.050               # and how far wide of its outline the box for the screw
#                                # is cut. Cut to the outline exactly, its sides land on
#                                # the stranded hole's own wall, that being the same
#                                # circle at the same x, and in the seat's top face
#                                # there they cross a sliver - two edges a hundredth of
#                                # a thousandth apart - which no plane can cut cleanly
# A wall for the cable. Turned round, the servo's lead leaves at the back of
# the tower and has the length of it to cross, so it is given something to run
# against: the module rail's own wall, repeated on the other side of the body.
# The magazine's side wall on the motor side stops being full height at y 37.8,
# where the lane ends; this carries it 13.00 mm further forward, to exactly
# where the module rail opposite stops, with the same window through it to feed
# the lead.
RAIL_X = (81.000, 82.500)     # that wall, whose top at z 32.501 the work stands on
RAIL_Y = (24.702, 37.707)     # and how far forward it goes: far enough to stand in
#                             # the same plane as the module bay's own walls, so the
#                             # front of the body turns one corner here rather than
#                             # a step 0.298 deep. It stands outside the pocket,
#                             # which ends at x 80.502, so it is clear of the servo
#                             # and its ears at every point of fitting them
RAIL_AT = 32.501              # the face it stands on
RAIL_SILL = 33.310            # the window's sill and head, both the module rail's own
RAIL_HEAD = 74.320
RAIL_TOP = 100.000            # and its top, which is the rail's too
RAIL_WINDOW = (28.730, 36.796)   # the window itself, the rail's own again
# The rail the wall stands on ends at y 37.707, and the magazine's own side wall
# is full height from y 37.805 back. Between the two the body has 0.098 mm of
# nothing, which runs from the top of the retaining ledge to the top of the
# wall and shows on the outside of the body as a slit the height of it. Inboard
# of x 81.500 the rail itself fills that gap as far as its own top, and the
# wall carried forward now reaches the rail's end, so what is left is the
# outer half millimetre of it, from the ledge up. A box fills that.
SEAM_X = 81.500               # from here out to the body's own face
SEAM_Y = (37.707, 37.805)     # the slit itself, between the rail and the magazine
SEAM_AT = 9.998               # the ledge's top, which is what it stands on
BRIDGE_X = 67.025             # the tie across to the tower's inner rail. It stands on
BRIDGE_Y = 31.500             # the tower's top where that is solid right across, which
#                             # is past the pocket's far wall at y 31.404, so it roofs
#                             # nothing the servo has to go down through
BRIDGE_AT = 32.500            # the tower's top, a thousandth below the wall's
# And the wall the lead actually runs behind, which faces the other way: across
# the body, parallel to the magazine's front and back faces, in the plane the
# module's own slot is in. The lead lies behind it, between it and the
# magazine's front face at y 37.805, held there rather than resting on an edge.
CHAN_Y = (24.702, 25.702)     # The wall the lead runs behind stands in the plane of
#                             # the module bay's own outer wall and is the thickness
#                             # of it, so that the front of the body reads as one
#                             # face rather than a set of steps.
CHAN_AT = 32.500              # It comes down to the top of the motor slot, which is
#                             # where the rail dividing that slot from the module's
#                             # channel ends and where the step the magazine's side
#                             # wall makes ends, and it stands on those two faces, sunk
#                             # into each the usual millimetre. Between them it is a
#                             # lintel over the slot, and that is how the lead gets
#                             # behind it: the case ends at y 20.2, well in front of
#                             # the wall, and the lead crosses under it in the slot,
#                             # which is clear from the seat at z 23.089 up to the
#                             # lintel's underside.
CHAN_TOP = 100.000            # and it carries on up to the top, with the walls beside it
CHAN_WALL = 66.000            # The module bay's outer wall stopped a millimetre short
CHAN_RIB = 67.025             # of that rail, leaving a slot the height of the body
#                             # between the bay and everything the cable uses. Its
#                             # outer face is taken out to the rail's own, which closes
#                             # the slot and leaves the bay twice the wall thickness on
#                             # that side. Only that face moves, so nothing the module
#                             # sits against changes.
BEZEL_AT = 25.000             # The bezel - the rib at the front of each bay wall that
#                             # the module goes in against - is a millimetre thick and
#                             # stands in the wall's own plane, from here at its front
#                             # face, sloping back with the floor under it, up to
#                             # z 68.310. Where the slot is left open the bezel stops
#                             # at it and the wall over it only starts at the top of
#                             # the motor slot, which leaves a notch in the front of
#                             # the body the width of the slot and 6.5 deep. So the
#                             # bezel is carried across the slot at its own height and
#                             # on up to the top, hung off the wall it laps as the
#                             # bezel beside it is, and the wall over the motor slot
#                             # laps into that in turn.
CHAN_LAP = 1.000              # how far it does, where the two meet over the rail
MOTOR_X = (67.000, 81.600)    # The underside under the motor is its own bevel: one
MOTOR_BEVEL = ((23.502, 17.500), (37.802, 10.500))   # flat face running between these
MOTOR_BOX = 17.500            # two, which is the seat's underside at its front and
MOTOR_FLOOR = 10.200          # 7.00 lower at the back of the body. It falls half as
#                             # fast as the bevel under the bay and sits well under it,
#                             # cut that shallow so the overhang would print without
#                             # supports. It is filed up onto the bay's plane instead,
#                             # as far as the motor's own box, which sits on it: in
#                             # front of where the two meet the face comes up flat at
#                             # the box's underside. The footprint is wide of the face
#                             # on every side, and the floor is only what the proof
#                             # looks down to - over the retaining ledge at 9.998.
BAY_TOP = 27.310              # Under the bay is the ledge the module sits on, its top
BAY_BACK = 37.801             # here and its back here. Its underside is not level: it
BAY_BEVEL = 12.102            # is one plane falling from the bezel's own underside at
#                             # the front to here at the back, and that bevel is what
#                             # the body shows under the bay. The ledge stops at the
#                             # slot as the bezel does, so it is carried across in the
#                             # same way, bevel and all, and what stands over the slot
#                             # stands on it.
CHAN_END = 65.003             # The wall then laps the whole of that thickened wall,
#                             # from the rail's face back to the far side of it, so the
#                             # two share solid material rather than a face and the
#                             # front of the body is one face from here across.

ARM_TIP = 31.75               # the arm's far end, this far out from the axis
ARM_REACH = 24.218            # which puts it this far past the axis along the lane
REST = 46.87                  # at rest, clamped this far back from square
PUSH_END = 34.13              # and this far past square at full advance
LANE_BACK = 38.00             # the wall the stack leans on, which it must not touch
ARM_CLEAR = 0.50              # by this much at least

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
         shorten=PUSHER_SHORTEN, second=SECOND_SLOT, flip=False,
         name='small', named=False):
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
                   take_up=take_up, second=second, flip=flip, slide=0.0, shift=0.0,
                   rest=REST, angle_push=round(REST + PUSH_END, 1),
                   name=name, notes=notes, lane=(lane_w, lane_d, LANE[2] + lift))
    if not (x_cut or y_cut or lift or flip):
        notes.append('this is the piece the parts in input/images are already cut for, '
                     'so the recipe for it is empty and the parts for it are those '
                     'files; --piece 40x30x7 --name small is the Swiss napolitain')
        settled.update(nothing=not named, copies=named, rail_cut=0.0, shorten=0.0,
                       crank=CRANK, arm_cut=0.0, stroke=standard_stroke,
                       overtravel=round(standard_stroke - lane_d - take_up, 2))
        return settled

    if not y_cut:
        settled.update(rail_cut=0.0, shorten=0.0, crank=CRANK, arm_cut=0.0,
                       stroke=standard_stroke,
                       overtravel=round(standard_stroke - lane_d - take_up, 2))
        if flip:
            flipped(settled, lane_d, take_up, second, notes)
            notes.append('the lane keeps its depth, so the arm and the pushing face are '
                         'left alone; the rail gives up only the %.2f mm the bay slides '
                         'into, and the clamp comes forward to %.1f degrees all the same'
                         % (settled['slide'], settled['rest']))
        else:
            notes.append('the lane keeps its depth, so the travel is the standard\'s: '
                         'the arm, the rail and the pushing face are left alone, and '
                         'anglePush stays at its default 77 with the arm square at rest')
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
    if not flip:
        notes.append('set anglePush to 81 on this unit and clamp the arm about 47 '
                     'degrees back from square at rest, which is what the %.2f mm off '
                     'the rail depends on'
                     % min(RAIL_REACH - stroke / 2 + RAIL_SWUNG_BACK,
                           RAIL_BAND[1] - RAIL_BAND[0]))
    rail_cut = round(min(RAIL_REACH - stroke / 2 + RAIL_SWUNG_BACK,
                         RAIL_BAND[1] - RAIL_BAND[0]), 3)
    settled.update(rail_cut=rail_cut, shorten=shorten, crank=crank, arm_cut=arm_cut,
                   stroke=stroke, overtravel=overtravel)
    if flip:
        flipped(settled, lane_d, take_up, second, notes)
    return settled


def flipped(settled, lane_d, take_up, second, notes):
    """What turning the servo round costs, and what pays for it.

    The shaft moves because the case is not symmetric about it. Sliding the
    whole bay back into the base behind the tower gives back all but a few
    millimetres of that, and those few come off the pusher, by way of the
    second slot, which holds it that much further back for nothing. What is
    left to pay is the arm: at rest it points back at the magazine, and the
    axis has moved that way, so the clamp comes forward until its far end
    clears the wall the stack leans on. That is the whole of the cost, and it
    is paid in stroke.
    """
    shift = round(BAY[0] + BAY[1] - 2 * SHAFT_AT, 3)
    slide = round(min(FLIP_SLIDE, TOWER_BACK - RAIL_BAND[0] - settled['rail_cut']), 3)
    if slide <= 0:
        raise SystemExit('this lane leaves no base behind the tower for the bay to '
                         'slide into: the rail is already cut back to it')
    net = round(shift - slide, 3)
    crank = settled['crank']

    corner = ARM_REACH - ARM_TIP * math.sin(math.radians(REST))
    room = LANE_BACK - ARM_CLEAR - (SHAFT_AT + net) - corner
    if room >= ARM_TIP:
        rest = REST
    else:
        rest = round(math.degrees(math.asin(room / ARM_TIP)), 2)
    if rest > REST:
        rest = REST
    stroke = round(crank * (math.sin(math.radians(rest))
                            + math.sin(math.radians(PUSH_END))), 3)
    up = round(take_up - net + second, 3)
    over = round(stroke - lane_d - up, 3)
    takes = share(settled['x_cut'], WIDTH_BANDS)
    settled.update(slide=slide, shift=shift, net=net, rest=rest,
                   angle_push=round(rest + PUSH_END, 1), stroke=stroke,
                   take_up=up, overtravel=over,
                   across=round(FLIP_FRAME[0] - settled['x_cut'], 3),
                   along=round(FLIP_FRAME[1] - settled['rail_cut'], 3),
                   bay=round(FLIP_BAY - takes[0], 3),
                   slot=round(SLOT_WIDE - takes[1], 3))
    settled['shut'] = settled['slot'] <= SLOT_SHUT
    if up < 0:
        raise SystemExit('turned round, the shaft moves %.2f mm and the pusher\'s '
                         'second slot gives back %.2f, which leaves the face %.2f '
                         'inside the stack at rest' % (net, second, -up))
    if over < 0:
        raise SystemExit('turned round, the swing the arm has room for leaves a '
                         'stroke of %.2f mm, and the lane and the take-up want '
                         '%.2f' % (stroke, lane_d + up))
    notes.append('the servo goes in turned round, cable to the back; its shaft moves '
                 '%.2f mm towards the magazine and the bay slides %.2f back into the '
                 'base behind the tower, so the pusher sees %.2f, which the second '
                 'slot at %.2f takes out' % (shift, slide, net, second))
    if over < 0.54:
        notes.append('%.2f mm past the exit is less than any arm this has been printed '
                     'with: the shortest that dispensed had 0.54' % over)


def clear_of(box, standing, tol=5e-3):
    """A box's sides moved clear of any vertex they would land near.

    `standing` is the x and y of every vertex the cut can reach, interleaved.
    A side whose nearest one falls in the band - near it, but not on it - which
    is the caller's own test for a side that will sliver, is taken
    two bands further out, which leaves the vertex it was grazing well behind.
    Outward always, so a box only ever grows and still holds whatever it was
    cut to hold, and the step repeats, because the move can set the side
    beside a vertex of its own. It gives up after a dozen tries and leaves the
    side where it is, for the caller's own check to refuse.

    A side already on a vertex is left there: the cut goes through a point the
    mesh has, which is the clean case, and moving it off would change parts
    this already cuts well. Onto the nearest vertex rather than past it would
    be the neater move for the rest, but it is not safe on this mesh - a side
    landed exactly on one opened it, the clip leaving degenerate pieces at the
    point - so a side that has to move is kept away from vertices instead.
    """
    out = list(box)
    for n in range(4):
        far = n % 2
        for _ in range(12):
            at = out[n]
            off = min(abs(v - at) for v in standing[n // 2::2])
            if not 1e-4 < off < tol:
                break
            out[n] = at + 2 * tol if far else at - 2 * tol
    return tuple(out)


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
    if p['rail_cut'] or p['flip']:
        body.append(('cut', 'y', RAIL_BAND[0],
                     RAIL_BAND[0] + p['rail_cut'] + p['slide']))
    if p['lift']:
        body.append(('lift', 'z', LEDGE_AT, p['lift']))
    if p['flip']:
        body += turn_round(p['slide'], p['across'], p['along'], p['lift'])
        body += motor_bevel(p['across'], p['along'], p['lift'])
        body += cable_rail(p['across'], p['along'], p['lift'], p['bay'], p['shut'])

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


def turn_round(slide, across=0.0, along=0.0, up=0.0):
    """The pocket, with its bay `slide` further back and its floor opened the
    other way.

    The three offsets carry the recipe from the frame its numbers were measured
    in to the one this piece cuts: `across` and `along` are what this piece
    leaves of the width and of the rail that the small body gave up, and `up` is
    what the ledge was raised by for a thicker piece, which the servo box rose
    with. All three are zero for that body, and the recipe is then what it was.

    Three moves, a fill and two carves, in that order. The bay goes back by
    cutting that much more off the rail - which only shortens the body - and then
    pushing the same thickness in again at the one clean seam the tower has,
    between the end of the floor opening and the start of the slope under it,
    which puts the length back and leaves the bay, its near seat and the tower's
    back wall behind where they were. The far seat's inner wall then comes back to
    meet them, so the bay is the length it was, and the slope's leading edge is
    pushed forward, out of the way of what follows.

    Then the floor. The opening cannot just be widened to take the bosses where
    they now are: they stand 6.70 mm apart and the opening is barely wider than
    they are, so the two positions overlap without either containing the other,
    and anything covering both would be most of the floor. So the old one is
    filled and a new one cut where the bosses now are - the gear boss against the
    bay's far end, the idler behind it - which leaves the plate material at both
    ends of the bay rather than none. Last, a hole for the flange screw, the bay
    having carried the flange away from the one it used.
    """
    far = BAY[1] + along - slide
    seam = round((OPENING_END + BUTTRESS) / 2.0 + along - slide, 3)
    screw = round(SCREWS[0] + along - slide + (SCREWS[1] - SCREWS[0]), 4)
    shaft = round(far - (SHAFT_AT - BAY[0]), 3)         # where it is, turned round
    axis = round((OPENING[0] + OPENING[1]) / 2.0 + across, 4)   # the x it stands on
    old = (round(BAY[0] + along - slide, 3), round(OPENING_END + along - slide, 3))
    turn = round(BAY[0] + BAY[1] + 2.0 * along - 2.0 * slide, 3)
    #                                                   # the y the servo turns about,
    #                                                   # doubled: the bay's middle
    hole = (FAR_SCREW[0] + across, FAR_SCREW[1] + along)        # the stranded screw
    cap = (DRIVER[0] + across, round(DRIVER[1] + along - slide, 3))   # and driver hole
    floor = (FLOOR_PLATE[0] + up, FLOOR_PLATE[1] + up)
    seat = (SEAT_PLATE[0] + up, SEAT_PLATE[1] + up)
    return [('lift', 'y', seam, slide),
            ('plane', 'y', BAY[1] + along, round(-slide, 3)),
            ('plane', 'y', BUTTRESS + along, BUTTRESS_FORWARD),
            ('read', axis, round(SHAFT_AT + along - slide, 3),
             floor[0], floor[1], 'opening'),
            ('read', hole[0], hole[1], seat[0], seat[1], 'screw'),
            ('read', cap[0], cap[1], BASE_PLATE[0], BASE_PLATE[1], 'driver'),
            ('plug', OPENING[0] + across - 0.5, OPENING[1] + across + 0.5,
             old[0] - 0.5, old[1] + 0.5,
             FLOOR_UNDER + up, floor[1], axis, round(shaft - IDLER, 3)),
            ('punch', 'screw', False, None, screw,
             SEAT_Z[0] + up, SEAT_Z[1] + up, seat[0], seat[1],
             PLATE_LAP, SCREW_WIDE),
            ('punch', 'opening', True, axis, round(turn - (old[0] + old[1]) / 2.0, 4),
             FLOOR_Z[0] + up, FLOOR_Z[1] + up, floor[0], floor[1],
             PLATE_LAP, 0.000),
            ('punch', 'driver', False, axis, shaft,
             BASE_CUT[0], BASE_CUT[1], BASE_PLATE[0], BASE_PLATE[1],
             PLATE_LAP, 0.000),
            ('plug', hole[0] - 1.5, hole[0] + 1.5, hole[1] - 1.5, hole[1] + 1.5,
             seat[0], seat[1], hole[0], hole[1]),
            ('plug', cap[0] - 3.0, cap[0] + 3.0,
             round(cap[1] - 3.0, 3), round(cap[1] + 3.0, 3),
             BASE_PLATE[0], BASE_PLATE[1], cap[0], cap[1])]


def motor_bevel(across=0.0, along=0.0, up=0.0):
    """The bevel under the motor filed onto the one under the module bay."""
    def through(a, b):
        m = (b[1] - a[1]) / (b[0] - a[0])
        return round(a[1] - m * (a[0] + along) + up, 6), round(m, 9)

    was = through(*MOTOR_BEVEL)
    now = through((CHAN_Y[0], BEZEL_AT), (BAY_BACK, BAY_BEVEL))
    knee = round((MOTOR_BOX + up - now[0]) / now[1], 3)
    return [('file', MOTOR_X[0] + across, MOTOR_X[1] + across,
             MOTOR_BEVEL[0][0] + along - 0.1, MOTOR_BEVEL[1][0] + along + 0.1,
             was, now, MOTOR_BOX + up, knee, MOTOR_FLOOR + up)]


def cable_rail(across=0.0, along=0.0, up=0.0, bay=0.0, shut=True):
    """A wall for the cable to run against, as six boxes and one moved face.

    The magazine's side wall carried forward over the tower, with the module
    rail's window in it, and a tie across to the tower's inner rail. Four boxes
    make the wall - a sill the width of it, a leg at each end of the window,
    and a head spanning between the legs - and the fifth is the tie. Built that
    way rather than cut, the window is simply the gap the legs leave, so
    nothing has to be carved out of a wall 1.5 mm thick.

    That wall faces along x, so on its own it only gives the lead an edge to
    rest against. What confines the lead is the last box: a wall facing the
    other way, across the body, parallel to the magazine's front and back
    faces and in the plane the module's own slot is in. The lead runs behind
    it, in the 12.10 between it and the magazine's front face, which takes a
    three-wire lead lying flat. It comes down to the top of the motor slot and
    stands on the two faces that end there, and over the slot between them it
    is a lintel, which is what the lead crosses under on its way behind.

    Either way it starts at the far side of the module bay's own wall and laps
    into it, so the front of the body is one face from there to the far side
    of the one carried forward. What lies between is a slot, the height of the
    body, between the bay's wall and the rail: 11.525 mm before anything is
    cut, and whatever the width band leaves of it after. The wall is prolonged
    straight across it.

    The moved face is the bay's outer one, and it only moves when `shut` -
    when the slot is down to a crack, as it is on the small body, where the
    band leaves 1.025 mm it cannot reach. Taking the face out then closes the
    crack for nothing. On a wider one it would stand a block of solid the
    height of the body in the slot and take the room beside the module's
    headers with it, so the slot is left open behind the wall. Three boxes
    take its place. The first is the ledge under the bay carried across the
    slot, hung off the bay wall at the height of the bezel's underside; the
    second is the bezel carried across on top of that, standing on it and
    running to the top of the body, which is why that one does not lap - what
    joins it to the bay's own bezel is the ledge under both; and the third is
    the wall over the motor slot, standing on that
    slot's top as before and lapping into the second. So the front of the body
    has no notch under it and the module's ledge runs the width of the bay and
    the slot, while above the ledge the slot is still open.

    The offsets are turn_round's: what this piece leaves of the width and of
    the rail the small body gave up, and what the ledge was raised by. `bay`
    is the width one again for the module bay's own wall, which sits below the
    slot and so moves by a different amount from everything outboard of it.
    """
    x0, x1 = RAIL_X[0] + across, RAIL_X[1] + across
    y0, y1 = RAIL_Y[0] + along, RAIL_Y[1] + along
    w0, w1 = RAIL_WINDOW[0] + along, RAIL_WINDOW[1] + along
    rib = BRIDGE_X + across
    ops = [('boss', SEAM_X + across, x1, SEAM_Y[0] + along, SEAM_Y[1] + along,
            SEAM_AT + up, RAIL_TOP + up),
           ('boss', x0, x1, y0, y1, RAIL_AT + up, RAIL_SILL + up),
           ('boss', x0, x1, y0, w0, RAIL_SILL + up, RAIL_HEAD + up),
           ('boss', x0, x1, w1, y1, RAIL_SILL + up, RAIL_HEAD + up),
           ('boss', x0, x1, y0, y1, RAIL_HEAD + up, RAIL_TOP + up),
           ('boss', rib, x0, BRIDGE_Y + along, y1, BRIDGE_AT + up, RAIL_SILL + up)]
    wall = CHAN_WALL + bay
    end = CHAN_END + bay
    if shut:
        ops.append(('plane', 'x', wall, round(rib - wall, 3)))
        ops.append(('boss', end, x0, CHAN_Y[0] + along, CHAN_Y[1] + along,
                    CHAN_AT + up, CHAN_TOP + up, round(rib - end, 3)))
    else:
        ops.append(('boss', end, rib, CHAN_Y[0] + along, BAY_BACK + along,
                    BEZEL_AT + up, BAY_TOP + up, round(wall - end, 3), True,
                    BAY_BEVEL + up))
        ops.append(('boss', wall, rib, CHAN_Y[0] + along, CHAN_Y[1] + along,
                    BAY_TOP + up, CHAN_TOP + up))
        ops.append(('boss', rib - CHAN_LAP, x0, CHAN_Y[0] + along, CHAN_Y[1] + along,
                    CHAN_AT + up, CHAN_TOP + up, CHAN_LAP))
    return ops


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
    if p['flip']:
        print('   servo    turned round, cable to the back: the bay %.2f mm further '
              'back' % p['slide'])
        print('            and the shaft %.2f forward of where it is, which the '
              'second slot at %.2f takes off the pusher'
              % (p['net'], p['second']))
        print('   cable    the magazine\'s side wall carried %.2f mm forward over '
              'the tower,' % (RAIL_Y[1] - RAIL_Y[0]))
        print('            to z %.0f with the module rail\'s own window in it, and '
              'tied across to the tower\'s inner rail'
              % RAIL_TOP)
        print('            and a wall %.2f thick across the body at y %.3f, from the '
              'top of the motor slot at z %.3f to z %.0f'
              % (CHAN_Y[1] - CHAN_Y[0], CHAN_Y[0], CHAN_AT, CHAN_TOP))
        if p['shut']:
            print('            with the module bay\'s outer wall taken out %.3f mm to '
                  'the rail beside it, closing what was left of the slot' % p['slot'])
        else:
            print('            prolonged over the %.2f mm slot beside the module bay, '
                  'which is left open behind it' % p['slot'])
        print('   arm      clamped %.1f degrees back at rest instead of %.1f, so '
              'anglePush is %.1f' % (p['rest'], REST, p['angle_push']))
        print('            which is what keeps its far end off the wall the stack '
              'leans on: %.2f mm clear' % (LANE_BACK - (SHAFT_AT + p['net'])
                                           - (ARM_REACH - ARM_TIP
                                              * math.sin(math.radians(REST)))
                                           - ARM_TIP * math.sin(math.radians(p['rest']))))
    for note in p['notes']:
        print('   note: %s' % note)
    print()


def options(argv):
    """--piece 40x30x7, --name small, and the three numbers of the travel."""
    out = dict(piece=PIECE, overtravel=OVERTRAVEL, take_up=TAKE_UP,
               shorten=PUSHER_SHORTEN, second=SECOND_SLOT, flip='--flip' in argv,
               name='small', named='--name' in argv)
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
        taken = {}
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
            elif op[0] == 'file':
                _, xa, xb, y0, y1, was, now, flat, knee, floor = op
                rubbed, hits, more = filed(tris, xa, xb, y0, y1, now, flat, knee, floor)
                checked, done, skipped, wrong = verify_filed(
                    tris, rubbed, xa, xb, y0, y1, now, flat, floor)
                if wrong:
                    raise SystemExit('%s: filing the face at x %.3f..%.3f does not hold '
                                     'up: %d of %d lines disagree, first at x %.2f '
                                     'y %.2f' % ((target_name, xa, xb, len(wrong),
                                                  checked + done) + wrong[0][:2]))
                was_m, now_m = measure(tris), measure(rubbed)
                if now_m['open_edges'] != was_m['open_edges']:
                    raise SystemExit('%s: filing the face at x %.3f..%.3f left the mesh '
                                     'open: %d edges against %d'
                                     % (target_name, xa, xb, now_m['open_edges'],
                                        was_m['open_edges']))
                print('   filed the face on z = %.3f %+.6f y up onto z = %.3f %+.6f y, '
                      'flat at %.3f in front of y %.3f: %.0f mm3 off'
                      % (was[0], was[1], now[0], now[1], flat, knee,
                         was_m['volume'] - now_m['volume']))
                print('   %d points moved, %d faces flattened into it; %d '
                      'lines over it now meet it there, %d elsewhere are as they were, '
                      '%d near a side not looked at'
                      % (hits, more, done, checked, skipped))
                tris = rubbed
            elif op[0] == 'boss':
                xa, xb, y0, y1, at, to = op[1:7]
                lap = op[7] if len(op) > 7 else 0.0
                hang = op[8] if len(op) > 8 else False
                slope = op[9] if len(op) > 9 else None
                stood, added = boss(tris, xa, xb, y0, y1, at, to, lap=lap, hang=hang,
                                    slope=slope)
                checked, standing, skipped, wrong = verify_boss(
                    tris, stood, xa + lap, xb, y0, y1, at, to)
                if wrong:
                    raise SystemExit('%s: the wall at y %.3f..%.3f does not hold up: '
                                     '%d of %d lines disagree, first at x %.2f y %.2f'
                                     % ((target_name, y0, y1, len(wrong),
                                         checked + standing) + wrong[0][:2]))
                was, now = measure(tris), measure(stood)
                made = now['volume'] - was['volume']
                if abs(made - added) > 0.05:
                    raise SystemExit('%s: the wall at y %.3f..%.3f added %.3f mm3, and '
                                     'the box it stands is %.3f'
                                     % (target_name, y0, y1, made, added))
                if now['open_edges'] != was['open_edges']:
                    raise SystemExit('%s: the wall at y %.3f..%.3f left the mesh open: '
                                     '%d edges against %d'
                                     % (target_name, y0, y1, now['open_edges'],
                                        was['open_edges']))
                print('   %s a box %.2f x %.2f %s z %.3f%s, up to %.3f%s'
                      % ('hung' if hang else 'stood', xb - xa, y1 - y0,
                         'from' if hang else 'on the face at', at,
                         '' if slope is None else ' falling to %.3f' % slope, to,
                         ', lapping %.2f into the wall at its end' % lap if lap else ''))
                print('   it added %.0f mm3, which is the box to 0.05; %d lines over it '
                      'now stop at its top, %d elsewhere stop where they did, %d along '
                      'its walls not looked at'
                      % (added, standing, checked, skipped))
                tris = stood
            elif op[0] == 'plug':
                xa, xb, y0, y1, zlo, zhi, cx, cy = op[1:]
                filled, gained, faces = plug(tris, xa, xb, y0, y1, zlo, zhi, cx, cy)
                checked, closed, skipped, wrong = verify_plug(
                    tris, filled, xa, xb, y0, y1, zlo, zhi)
                if wrong:
                    raise SystemExit('%s: filling the opening at y %.3f..%.3f does '
                                     'not hold up: %d of %d lines beside it '
                                     'disagree, first at x %.2f y %.2f'
                                     % ((target_name, y0, y1, len(wrong),
                                         checked) + wrong[0][:2]))
                was, now = measure(tris), measure(filled)
                made = now['volume'] - was['volume']
                if abs(made - gained) > 0.05:
                    raise SystemExit('%s: filling the opening at y %.3f..%.3f added '
                                     '%.3f mm3, and the hole it closed is %.3f'
                                     % (target_name, y0, y1, made, gained))
                if now['open_edges'] != was['open_edges']:
                    raise SystemExit('%s: filling the opening at y %.3f..%.3f left '
                                     'the mesh open: %d edges against %d'
                                     % (target_name, y0, y1, now['open_edges'],
                                        was['open_edges']))
                print('   filled the opening at y %.3f..%.3f, taking its %d wall '
                      'faces away and capping both rims' % (y0, y1, faces))
                print('   it put back %.0f mm3, which is the hole to 0.05; %d lines '
                      'through it now meet the plate, %d elsewhere agree, %d on its '
                      'rim or under the seats not looked at'
                      % (gained, closed, checked, skipped))
                tris = filled
            elif op[0] == 'read':
                px, py, zlo, zhi, name = op[1:]
                taken[name] = outline(tris, px, py, zlo, zhi)
                print('   read the outline of the hole round (%.3f, %.3f) between '
                      'z %.3f and %.3f: %d vertices, %.3f mm2'
                      % (px, py, zlo, zhi, len(taken[name]),
                         _twice(taken[name]) / 2.0))
            elif op[0] == 'punch':
                name, over, tx, ty, czlo, czhi, zlo, zhi, lap, wide = op[1:]
                if name not in taken:
                    raise SystemExit('%s: no outline was read under %r' % (target_name, name))
                ring = taken[name]
                if over:
                    ring = [(-p[0], -p[1]) for p in ring]
                was_mid = _middle(ring)
                dx = 0.0 if tx is None else tx - was_mid[0]
                dy = ty - was_mid[1]
                ring = [(round(p[0] + dx, 4), round(p[1] + dy, 4)) for p in ring]
                box = (min(p[0] for p in ring) - wide, max(p[0] for p in ring) + wide,
                       min(p[1] for p in ring) - wide, max(p[1] for p in ring) + wide)
                standing = [p[k] for p in (q for t in tris for q in t)
                            if not (czlo is not None
                                    and (p[2] <= czlo + 1e-4 or p[2] >= czhi - 1e-4))
                            for k in (0, 1)]
                was = box
                box = clear_of(box, standing)
                if box != was:
                    print('   its box moved %s off vertices it would have grazed: '
                          'x %.4f..%.4f y %.4f..%.4f, was x %.4f..%.4f y %.4f..%.4f'
                          % ((name,) + box + was))
                for k, at, which in ((0, box[0], 'x'), (0, box[1], 'x'),
                                     (1, box[2], 'y'), (1, box[3], 'y')):
                    off = [abs(v - at) for v in standing[k::2]]
                    if off and 1e-4 < min(off) < 5e-3:
                        raise SystemExit('%s: a side of the box for the %s would stand '
                                         'at %s = %.4f, %.6f from a vertex already '
                                         'there: near enough to cut a face into slivers '
                                         'and not near enough to be snapped onto it'
                                         % (target_name, name, which, at, min(off)))
                cleared, removed, columns = slit(tris, box[0], box[1], box[2],
                                                 box[3], czlo, czhi)
                checked, inside, skipped, wrong = verify_slit(
                    tris, cleared, box[0], box[1], box[2], box[3], czlo, czhi)
                if wrong:
                    raise SystemExit('%s: clearing the way for %s at y %.3f..%.3f does '
                                     'not hold up: %d of %d lines disagree, first at '
                                     'x %.2f y %.2f'
                                     % ((target_name, name, box[2], box[3], len(wrong),
                                         checked + inside) + wrong[0][:2]))
                was, now = measure(tris), measure(cleared)
                if abs((was['volume'] - now['volume']) - removed) > 0.05:
                    raise SystemExit('%s: clearing the way for %s took %.3f mm3 and the '
                                     'box is %.3f'
                                     % (target_name, name,
                                        was['volume'] - now['volume'], removed))
                if now['open_edges'] != was['open_edges']:
                    raise SystemExit('%s: clearing the way for %s left the mesh open: '
                                     '%d edges against %d'
                                     % (target_name, name, now['open_edges'],
                                        was['open_edges']))
                print('   cleared a box %.3f x %.3f for the %s, at x %.3f..%.3f '
                      'y %.3f..%.3f: %.0f mm3, the box to 0.05'
                      % (box[1] - box[0], box[3] - box[2], name,
                         box[0], box[1], box[2], box[3], removed))
                stood, added, facets = panel(cleared, box[0] - lap, box[1] + lap,
                                             box[2] - lap, box[3] + lap,
                                             zlo, zhi, ring)
                checked, standing, through, skipped, wrong = verify_panel(
                    cleared, stood, box[0] - lap, box[1] + lap, box[2] - lap,
                    box[3] + lap,
                    zlo, zhi, ring)
                if wrong:
                    raise SystemExit('%s: the plate round the %s does not hold up: %d '
                                     'of %d lines disagree, first at x %.2f y %.2f, '
                                     '%r against %r'
                                     % ((target_name, name, len(wrong),
                                         checked + standing + through) + wrong[0]))
                was, now = measure(cleared), measure(stood)
                made = now['volume'] - was['volume']
                if abs(made - added) > 0.05:
                    raise SystemExit('%s: the plate round the %s put back %.3f mm3 and '
                                     'the plate less its hole is %.3f'
                                     % (target_name, name, made, added))
                if now['open_edges'] != was['open_edges']:
                    raise SystemExit('%s: the plate round the %s left the mesh open: '
                                     '%d edges against %d'
                                     % (target_name, name, now['open_edges'],
                                        was['open_edges']))
                print('   put the plate back round it in %d facets, lapping %.2f over '
                      'what is there: %.0f mm3, the plate less its hole to 0.05'
                      % (facets, lap, added))
                print('   %d lines over the plate now stop at its faces, %d through '
                      'the hole still meet nothing, %d elsewhere are as they were, '
                      '%d near a wall not looked at'
                      % (standing, through, checked, skipped))
                tris = stood
            elif op[0] == 'slit':
                xa, xb, y0, y1 = op[1:5]
                zlo, zhi = op[5:7] if len(op) > 5 else (None, None)
                slotted, removed, columns = slit(tris, xa, xb, y0, y1, zlo, zhi)
                checked, inside, skipped, wrong = verify_slit(
                    tris, slotted, xa, xb, y0, y1, zlo, zhi)
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
                print('   cut a %.2f mm opening at y %.3f..%.3f, running '
                      'x %.3f..%.3f%s, over %d profiles'
                      % (y1 - y0, y0, y1, xa, xb,
                         '' if zlo is None else ', between z %.3f and %.3f'
                         % (zlo, zhi), columns))
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
