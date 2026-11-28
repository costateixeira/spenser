# Transferências - Spenser - a developer's companion v1.0.0

## Transferências

 
Esta página inclui traduções a partir da língua original em que o guia foi criado. Informações sobre estas traduções e instruções para fornecer feedback podem ser encontradas [aqui](translationinfo.md). 

### Firmware

O firmware atual de uma unidade Spenser é publicado em [costateixeira.github.io/spenser/firmware/](https://costateixeira.github.io/spenser/firmware/), com as notas de versão da compilação que está a servir, as duas imagens e o manifesto que uma unidade lê:

* `firmware.bin` - o código
* `spiffs.bin` - o painel e o guia para agentes
* `manifest.json` - o que uma unidade verifica de hora a hora para dar conta de uma nova compilação

Uma unidade atualiza-se a partir daí: mostra um aviso no seu próprio painel quando há uma compilação à espera e instala-a quando lhe é pedido, depois de mostrar o que ela contém. A página [Interfaces](interfaces.md) descreve as rotas de atualização, e a primeira gravação de uma unidade tem de ser feita por cabo, porque reparticiona o chip.

