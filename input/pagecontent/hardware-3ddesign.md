Below are the 3D parts used to build **Spenser**.


### Description

<br clear="all">

| Part | Image | Description | Downloads |
|------|-------|-------------|-----------|
| **Body** | ![](spenser-body.png){:width="120px"} | Holds the chocolate stack, the servo motor and the slider rails, on its own base. | [STL](spenser-body.stl) |
| **Pusher** | ![](spenser-pusher.png){:width="120px"} | Slides along the rails and pushes one chocolate out. | [STL](spenser-pusher.stl) |
| **Arm** | ![](spenser-arm.png){:width="120px"} | Attaches to the servo horn and drives the pusher. | [STL](spenser-arm.stl) |
| **Pin** | ![](spenser-pin.png){:width="120px"} | Axle connecting the arm to the pusher. | [STL](spenser-pin.stl) |
{:.table-bordered}

### For smaller chocolates

The lane above takes a piece up to 60 × 39 mm, which suits a Belgian
napolitain. A Swiss one is smaller — a Lindt Napolitain is around 40 × 25 mm —
and has room to shift in it. The 9 mm of slack along the push is the one that
matters: it is enough for a piece to creep forward under the retaining wall,
where the pusher meets it edge on.

These are the same parts with the lane cut 17.5 mm narrower, 9 mm
shallower, and the rail 20.2 mm shorter, so they take a piece **up to
40 × 30 mm**, at the same 5.5 to 7.5 mm thick. Measure a piece before
printing: 30 mm is the limit along the push.

The depth is the one cut to the piece, and it is exact. The width is not: it
is set by the bay the Atomic Motion Base drops into, which is 24 mm wide for
a module 24 mm wide, and by the servo's pocket beside it at 12.26 mm for a
case 12.2 thick. Both stand between the same two side walls as the lane, and
nothing can come out of either, so 17.5 mm is the whole of the width these
parts can give up. A piece 40 mm across keeps 2.5 mm of side play in what is
left, and even a loose fit there would cost nothing: a 30 × 40 piece cannot
turn in a lane 31 mm deep however wide that lane is.

Two things change on the build. Set `anglePush=78.6` on this unit, against
the default of 77. And fit the arm so that at rest it sits about 44.5° back
from pointing straight across the lane, rather than square to it: that moves
the whole travel back and is what lets the body be this short. The check is
that at rest the pushing face ends up just behind the chocolate stack. The
26.7 mm comes off the back, behind the pusher, not off the mouth: the piece
leaves through the other end, and 6.5 mm of it goes back in again under the
servo, which is how its bay comes to sit against the back face. The servo
itself goes in turned end for end from the standard unit, so that its cable
leaves at the back; the pin then goes in the pusher's second slot, which takes
out the 5 mm the turned-round case moves the shaft by. The pin has its own part here and needs no
drilling: the hole in the arm is 3.1 mm in these files against 2.76 on the
standard arm, and the pin itself is 2.3 mm rather than 2.55. Both halves had
to move. A small hole prints under its size and a small shaft over its own,
and together they ate the 0.44 mm of clearance the drawing had, so the pin
would not enter; there is 0.79 mm now. The standard pin is unchanged — drill
the standard arm 2.6 mm if you are building that one.

For another size of piece, [`tools/resize/build.py`](https://github.com/costateixeira/spenser/blob/master/tools/resize/build.py) cuts these three
parts to fit it and prints what the travel comes to. A piece is given as
across the lane × along it × thick, so `--piece 40x30x7 --name small` is
this variant; with nothing after it the script takes the Belgian mignonette
the parts above are already cut for, and says there is nothing to cut.

| Part | Description | Downloads |
|------|-------------|-----------|
| **Body** | A lane 43.5 × 31 mm instead of 61 × 40; 46.5 × 80.8 × 105 mm overall. The module bay keeps its full 24 mm and the servo its 12.26, and no height in it moves at all: the ledge that holds the pusher down, the servo's box and the exit slot are all where the standard body has them. The servo goes in turned end for end, so its cable leaves at the back of the unit instead of towards the magazine, and its whole bay sits 6.5 mm further back so that the shaft stays near where it was. The lead then has the length of the tower to cross, so the magazine's side wall is carried 13.0 mm forward over it, as tall as the module rail opposite and with the same window through it, for the lead to run against. | [STL](spenser-body-small.stl) |
| **Pusher** | 42.4 × 46 mm, to match the narrower lane, with two pin slots 2.55 mm wide: the pin goes in either, and the second one, 5 mm further in, holds the pusher 5 mm further back through the whole swing, which is the one this body wants, the servo being turned round. | [STL](spenser-pusher-small.stl) |
| **Arm** | 26.75 mm between its holes instead of 41, which gives a 33.76 mm stroke at `anglePush=78.6`, matched to the shallower lane. | [STL](spenser-arm-small.stl) |
| **Pin** | 2.3 mm across its shaft instead of 2.55, which is the other half of the fit with the arm. | [STL](spenser-pin-small.stl) |
{:.table-bordered}

### Bill of Materials

**The quantities indicated are for the 2-position dispenser.**

| Item   | Description | Quantity |
|---|---|---------|
| Body | Holds the chocolates, the motor and the slider rails | 2 |
| Arm | Rotating arm attached to the servo | 2 |
| Pin  | Connects the arm to the pusher | 2  |
| Pusher  | Pushes a chocolate out  | 2  |
{:.table-bordered}
