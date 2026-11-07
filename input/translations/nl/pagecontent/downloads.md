

### Firmware

De huidige firmware voor een Spenser-unit wordt gepubliceerd op
[costateixeira.github.io/spenser/firmware/](https://costateixeira.github.io/spenser/firmware/), met de release notes
van de build die daar wordt aangeboden, de twee images, en het manifest dat een unit leest:

* `firmware.bin` - de code
* `spiffs.bin` - het dashboard en de handleiding voor agents
* `manifest.json` - wat een unit elk uur controleert om een nieuwe build op te merken

Een unit updatet zichzelf van daaruit: hij toont een melding op zijn eigen dashboard
als er een build klaarstaat, en installeert die als u daarom vraagt, nadat hij heeft
getoond wat erin zit. De pagina [Interfaces](interfaces.html) beschrijft de
update-routes, en de eerste keer flashen moet via een kabel, omdat dat de chip opnieuw
partitioneert.
