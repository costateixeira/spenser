Two lanes, one for dark chocolate and one for milk. Everything marked **2x** is
done once for each lane.

Print the [3D parts](hardware-3ddesign.html), buy the
[electronics](hardware-bom.html), and put the [firmware](firmware.html) on the
controller first.

These drawings were made from the parts' 3D models, not photographed from a
finished unit. If something here does not match what is in your hands, please
[tell us](https://github.com/costateixeira/spenser/issues).
{:.stu-note}

<div class="assembly" markdown="0">

<figure class="assembly-step assembly-wide">
  <img src="assembly-00.svg" alt="The parts: two bodies, pushers, arms, pins, servos and horns, one Atom S3 Lite, one Atomic Motion base, one power bank, six screws and a screwdriver. A chocolate piece may be up to 60 by 39 mm, and 5.5 to 7.5 mm thick."/>
  <figcaption>Check that you have everything. The horns and screws come with the servos, and you also need a USB-C cable. A piece of chocolate must be no larger than 60 × 39 mm, and between 5.5 and 7.5 mm thick.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">1</span>
  <img src="assembly-01.svg" alt="A servo is lowered into the box on the body, with its shaft pointing down."/>
  <figcaption>Lower the servo into the box, shaft down, until its ears rest on the ledge. The shaft points at the tray.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">2</span>
  <img src="assembly-02.svg" alt="Two screws go through the servo's ears."/>
  <figcaption>Fix it with two screws through the ears. Snug, not tight: they are going into plastic.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">3</span>
  <img src="assembly-03.svg" alt="The Atom is pressed onto the end of the motion base away from the battery."/>
  <figcaption>Press the Atom onto the end of the Atomic Motion base away from the battery.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">4</span>
  <img src="assembly-04.svg" alt="The base slides down into the bay on the front of the tower, battery end first, with the Atom at the top."/>
  <figcaption>Slide the base down into the bay on the front of one tower, battery end first, so the Atom ends up at the top. The battery and the Atom's button face the tray, and the servo headers are on the side towards the servo. Only one body needs it.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">5</span>
  <img src="assembly-05.svg" alt="Two bodies stand side by side. One servo plug goes onto the header marked S4 and the other onto S3. A close-up shows a plug going onto the pins."/>
  <figcaption>Stand the bodies side by side. Push the dark lane's servo plug onto the header marked S4 and the milk lane's onto S3, which the firmware calls channels 3 and 2. The brown wire is ground: match it to the ground mark beside the header. A different choice can be set on the dashboard.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">6</span>
  <img src="assembly-06.svg" alt="A power bank is connected by a USB-C cable to the port on top of the Atom, and the base's power switch is turned on."/>
  <figcaption>Plug the power bank into the USB-C port on top of the Atom and switch the base on. Open the dashboard and press <strong>Move both to rest</strong>. Do not turn the servos by hand from now on. The base's own battery charges from the same cable.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">7</span>
  <img src="assembly-07.svg" alt="The pusher slides into the channel from the front. A close-up shows the ribs underneath."/>
  <figcaption>Slide the pusher into the channel from the front, ribs down and the long slot towards you.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">8</span>
  <img src="assembly-08.svg" alt="The horn is pressed into the arm. The arm slides under the servo box, and a screw is driven in from underneath the body."/>
  <figcaption>Press a horn into the groove in the arm. Slide the arm under the box and onto the shaft, then fix it with the horn screw, through the hole underneath the body.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">8</span>
  <img src="assembly-08b.svg" alt="Seen from above, the right position has the arm pointing to the front of the tray and the tower floor clear. The wrong position has the arm pointing at the tower and the pusher sticking out through the back."/>
  <figcaption>At rest, the arm points to the front and the pusher leaves the floor of the tower clear. If it does not, take the arm off and put it back on the shaft in the right position.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">9</span>
  <img src="assembly-09.svg" alt="The pin drops through the end of the arm and into the slot in the pusher. A close-up shows its head resting on the arm."/>
  <figcaption>Drop the pin through the arm and into the slot, head up. It has to slide freely along the slot. If it binds, file the slot a little wider.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">10</span>
  <img src="assembly-10.svg" alt="Seen from behind, the pusher comes out of the slot at the back of the tower, and a piece of chocolate leaves ahead of it."/>
  <figcaption>With the tower still empty, press <strong>Test dark cycle</strong> and <strong>Test milk cycle</strong> on the dashboard. The pusher should reach through the slot at the back, then return. Chocolate comes out here, so leave room for a cup.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">11</span>
  <img src="assembly-11.svg" alt="Pieces of chocolate are stacked flat into the top of the tower."/>
  <figcaption>Stack the chocolate flat into the top of the tower. The window at the back shows how much is left. Tell the unit how much you loaded, on the dashboard.</figcaption>
</figure>

<figure class="assembly-step">
  <img src="assembly-12.svg" alt="The finished dispenser with two lanes, next to a smiling person with a piece of chocolate."/>
  <figcaption>Done. Now <a href="usage.html">place an order</a>.</figcaption>
</figure>

</div>

These drawings are generated from the same STL files you print. To change one,
edit `tools/assembly/build.py` in the source repository and run it again.
