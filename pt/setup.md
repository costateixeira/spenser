# Setup - Spenser - a developer's companion v1.0.0

## Setup

 
Esta página inclui traduções a partir da língua original em que o guia foi criado. Informações sobre estas traduções e instruções para fornecer feedback podem ser encontradas [aqui](translationinfo.md). 

A unidade está montada, com o firmware gravado e ligada. Falta pô-la numa rede e apontá-la ao sítio de onde virão as prescrições.

Há um facto que decide tudo o resto nesta página: **nunca é preciso nada ligar-se de fora a uma unidade.** Ela pode ser alcançada quando a rede o permite, e sai à procura de trabalho quando a rede não o permite. É por isso que um dispensador funciona na Wi-Fi de uma conferência, que é onde este tipo de demonstração costuma morrer.

### Primeiro arranque

Sem credenciais guardadas, a unidade é a sua própria rede Wi-Fi aberta. A rede chama-se `Spenser-` seguido dos dois últimos bytes do seu endereço MAC, por exemplo `Spenser-E3D4`, e esse é também o nome da unidade em todo o resto.

1. Ligue-se a`Spenser-XXXX`a partir de um telemóvel ou de um portátil. A unidade responde a qualquer nome de DNS que lhe perguntem, por isso a página de configuração abre normalmente sozinha. Se não abrir, aceda a[http://192.168.4.1](http://192.168.4.1).
1. Escolha uma rede da lista, indique a palavra-passe e guarde. A unidade reinicia e liga-se a ela.
1. A partir daí está em[http://spenser.local](http://spenser.local), ou no endereço que o router lhe tiver dado.

**Guarde a chave antes de sair do modo de configuração.** Tudo o que **altera** uma unidade precisa dela: dispensar, definições, stock, Wi-Fi e atualizações. `GET /key` devolve-a durante cinco minutos depois de um reinício, e a qualquer momento enquanto a unidade estiver em modo de configuração. Também é escrita na consola série, a 115200 baud, em cada arranque. Uma unidade que esteja a servir o seu próprio ponto de acesso aceita tudo sem chave, porque ali não há rede nenhuma a defender.

Manter o botão premido três segundos durante o arranque devolve o modo de configuração. Dez segundos apagam as credenciais guardadas; o LED fica vermelho enquanto o botão está premido, para avisar antes de o largar.

### Que arranjo escolher

| | |
| :--- | :--- |
| Na sua rede, com um servidor de prescrições | De ambas as formas: publicadas diretamente na unidade, ou emitidas no servidor e recolhidas |
| Na sua rede, sem servidor | Publicadas diretamente na unidade |
| No seu próprio ponto de acesso | Publicadas diretamente na unidade, por quem se tiver ligado a ela |
| Numa rede que isola os seus clientes | Emitidas num servidor de prescrições na Internet, e recolhidas |

#### A sua própria rede

Casa, escritório, laboratório. A unidade está na Wi-Fi, `spenser.local` resolve, e ambos os caminhos lhe estão abertos: publicar um MedicationRequest diretamente nela e sai um chocolate, ou colocar prescrições num servidor e deixar a unidade recolhê-las.

É este o arranjo com que se deve desenvolver, porque permite ver as duas metades.

#### Sem rede nenhuma

Deixe a unidade no seu próprio ponto de acesso e deixe as pessoas ligarem-se a `Spenser-XXXX`. A unidade está em `192.168.4.1`, ali não precisa de chave, e as prescrições publicadas nela são dispensadas de imediato. A troca completa é [pedir diretamente à unidade](ExampleScenario-DirectOrderScenario.md).

Faltam duas coisas sem ligação à Internet. Não há relógio, porque não há NTP, e por isso a unidade omite `whenHandedOver` e afins em vez de inventar uma hora. E não há servidor de prescrições, por isso não há nada para consultar; desligue a consulta periódica com `pollEnabled=0` para a unidade deixar de tentar.

#### Uma rede que isola os seus clientes

A Wi-Fi de conferências e de hotéis, e quase todas as redes para convidados, põem cada cliente na sua própria célula. Os clientes alcançam a Internet e mais nada. `spenser.local` não vai resolver, o endereço da unidade não vai responder, e nada lhe pode ser publicado.

A unidade não tem problema nenhum. Continua a sair.

Ponha um servidor de prescrições algures na Internet, aponte a unidade a ele, e deixe todos escreverem lá as suas prescrições. A unidade consulta o servidor, recolhe o trabalho que lhe é dirigido, dispensa, e comunica de volta o que fez. É [pedir através de um servidor de prescrições](ExampleScenario-TaskOrderScenario.md), e o isolamento de clientes é a razão de ser desse cenário.

Verifique isto antes da sessão e não durante: ligue-se à rede com dois dispositivos e tente alcançar um a partir do outro.

#### Uma partilha de rede do telemóvel

O mesmo que a sua própria rede, e sob o seu controlo, desde que o telemóvel também não esteja a isolar os clientes — alguns isolam. É o recurso habitual quando a Wi-Fi do local se revela isolada e o servidor de prescrições já está na Internet.

### Apontar a unidade a um servidor de prescrições

Tudo o que se segue precisa da chave.

```
KEY=... # da consola série, ou de GET /key

curl -H "X-Spenser-Key: $KEY" \
  "http://spenser.local/setSettings?serverUrl=https://example.org/fhir&orderMode=both&pollEnabled=1&pollSeconds=30&writeBack=1&giveUpOnStockEmpty=0"

```

* `orderMode` é `both` por omissão: a unidade aceita tanto prescrições com tag como Tasks. `tag` ou `task` restringem-na a uma só. Não são dois modos de funcionamento, apenas duas formas de uma prescrição se tornar acionável.
* `pollSeconds` está entre 5 e 3600, 30 por omissão. `GET /checkOrders` força uma verificação imediata, e devolve `202` antes de a verificação ter terminado.
* `giveUpOnStockEmpty` desligado deixa em aberto uma prescrição que não pôde ser aviada, de modo que reabastecer a pista a cumpre numa verificação posterior. Ligado, é comunicada uma vez e abandonada.

O painel em `http://spenser.local` define as mesmas coisas, e ainda o stock, os ângulos dos servos e as atualizações.

### Várias unidades na mesma sala

Cada unidade consulta o mesmo servidor e, de outro modo, recolheria as mesmas prescrições. Indique a que deve aviar a prescrição em `Task.requestedPerformer`, e na extensão `dispensingDevice` da própria prescrição; todas as outras unidades a ignoram.

Cada verificação considera apenas os cinco primeiros resultados. Uma fila mais longa do que isso no servidor pode ultrapassar uma verificação, o que convém saber antes de se formar uma fila numa demonstração.

### Quando não funciona

* **`spenser.local` não resolve.** Use o endereço do router ou da consola série. O mDNS é a parte com mais probabilidade de faltar, não a unidade.
* **Tudo responde `401`.** A chave falta ou está errada. Reinicie a unidade e leia `GET /key` nos cinco minutos seguintes.
* **As dispensas não têm data e hora.** O relógio não foi acertado: o NTP ainda não respondeu, ou não há caminho até ele. A unidade omite a hora em vez de a inventar.
* **As prescrições não são recolhidas.** Verifique `serverUrl`, verifique se `pollEnabled` está ligado, e lembre-se de que as prescrições já tratadas ficam registadas: `GET /forgetOrders` antes de repetir o mesmo cenário.
* **Um teste está sempre a competir com a unidade.** Desligue a consulta periódica com `pollEnabled=0` durante os testes e force as verificações, e volte a ligá-la no fim.
* **A página de configuração não abre sozinha.** Aceda a [http://192.168.4.1](http://192.168.4.1) estando ligado a `Spenser-XXXX`.

[Interfaces](interfaces.md) tem a referência por detrás de tudo isto: todas as rotas, o que precisa de chave, e o que faz cada definição.

