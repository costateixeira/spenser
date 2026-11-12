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

These are the same parts with the lane cut 19.25 mm narrower, 9 mm
shallower, and the rail 20.2 mm shorter, so they take a piece **up to
40 × 30 mm**, at the same 5.5 to 7.5 mm thick. Measure a piece before
printing: 30 mm is the limit along the push.

Two things change on the build. Set `anglePush=81` on this unit, against
the default of 77. And fit the arm so that at rest it sits about 47° back
from pointing straight across the lane, rather than square to it: that moves
the whole travel back and is what lets the body be this short. The check is
that at rest the pushing face ends up just behind the chocolate stack. At
full advance the tail pokes 1.7 mm out of the mouth, which is intended. The
pin is the same part as before and needs no drilling here: its hole in the
arm is 3 mm in these files, against 2.76 on the standard arm, which prints
under size and binds on the 2.55 mm pin.

| Part | Description | Downloads |
|------|-------------|-----------|
| **Body** | A lane 41.75 × 31 mm instead of 61 × 40; 44.75 × 80.8 × 107 mm overall. The ledge that holds the pusher down sits 2 mm higher, to clear the arm, and the servo's box — its ear seat and the floor of its pocket — comes back down by the same 2 mm, so that the arm does not rise with it. | [STL](spenser-body-small.stl) |
| **Pusher** | 40.65 × 46 mm, to match the narrower lane, with the pin slot opened to 2.8 mm. | [STL](spenser-pusher-small.stl) |
| **Arm** | 28.75 mm between its holes instead of 41, which gives a 37.11 mm stroke at `anglePush=81`. | [STL](spenser-arm-small.stl) |
| **Pin** | The same part as above. | [STL](spenser-pin.stl) |
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
