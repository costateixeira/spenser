Esta página documenta todas as interfaces que uma unidade Spenser expõe: as FHIR,
a API HTTP privada que usa para a sua própria configuração e as interfaces que
nem sequer são HTTP. É a referência por trás da página
[Utilizar o Spenser](usage.html), e a fonte de verdade é a CapabilityStatement
que cada unidade publica no seu próprio `/metadata`.

Uma unidade está acessível na rede local como `http://spenser.local`, que anuncia
por mDNS, ou no endereço que o router lhe atribuir.

### O que precisa de chave {#what-needs-a-key}

Ler uma unidade é livre: a sua CapabilityStatement, as suas dispensas, as suas
prescrições, o seu inventário e o seu painel estão disponíveis para quem lhe
conseguir chegar. Tudo o que *altera* uma unidade precisa da chave dessa unidade:
dispensar, definições, Wi-Fi, stock e atualizações de firmware. Essas rotas
respondem `401` com um OperationOutcome quando a chave falta.

A chave é gerada no primeiro arranque da unidade e impressa na sua consola série
em todos os arranques. Viaja como `Authorization: Bearer <key>`, como cabeçalho
`X-Spenser-Key`, ou como `?key=` para um cliente que não consiga definir
cabeçalhos. `GET /key` devolve-a durante cinco minutos após um reinício e em
qualquer momento enquanto a unidade estiver em modo de configuração, que é a
janela de que o proprietário dispõe e um transeunte não. Uma unidade a servir o
seu próprio ponto de acesso aceita tudo sem chave, porque ali não há rede para
defender.

`rest.security.description` na CapabilityStatement de cada unidade diz o mesmo,
para que um cliente o possa descobrir.

### Dois papéis {#two-roles}

O Spenser é um **servidor** FHIR e um **cliente** FHIR ao mesmo tempo, e a
diferença importa quando se decide para onde enviar alguma coisa.

* **Como servidor**, aceita uma prescrição publicada diretamente nele e dispensa
  de imediato. Publicar no dispositivo é, em si, a autorização para dispensar.
* **Como cliente**, consulta um servidor de prescrições à procura de prescrições
  que deva aviar, e comunica o que fez. Aqui, uma prescrição *não* é uma
  instrução, e o Spenser só age sobre prescrições que tenham sido tornadas
  acionáveis.

Ambos os papéis estão declarados na sua
[CapabilityStatement](CapabilityStatement-SpenserFHIRCapabilityStatement.html).

### Atores {#actors}

| Ator | O que faz |
|---|---|
| [Unidade Spenser](ActorDefinition-SpenserUnit.html) | dispensa, como servidor FHIR e como cliente FHIR |
| [Emissor de Prescrições](ActorDefinition-OrderPlacer.html) | pede chocolate e decide se uma prescrição é acionável |
| [Servidor de Prescrições](ActorDefinition-OrderServer.html) | guarda as prescrições até uma unidade as recolher, e recebe os seus relatos |
| [Proprietário da Unidade](ActorDefinition-UnitOwner.html) | detém a chave e configura, reabastece e atualiza a unidade |
| [Publicador de Atualizações](ActorDefinition-UpdatePublisher.html) | publica o manifesto e as imagens que uma unidade instala |

### O que torna uma prescrição acionável {#what-makes-an-order-actionable}

Seguindo a orientação Clinical Orders Workflow da HL7, uma MedicationRequest
parada num servidor é uma autorização, não uma ordem. O Spenser só a avia quando
uma de duas coisas é verdadeira:

1. **Uma tag.** A MedicationRequest traz `meta.tag`
   `http://terminology.hl7.org/CodeSystem/common-tags#actionable`.
   Veja [Prescrição tornada acionável por uma tag](MedicationRequest-ActionableDarkOrder.html).
2. **Uma Task.** Uma Task com o estado `requested` aponta para a MedicationRequest
   em `Task.focus`.
   Veja [Task a pedir que uma prescrição seja aviada](Task-FulfillPlainMilkOrder.html),
   que torna [esta prescrição simples](MedicationRequest-PlainMilkOrder.html)
   acionável.

Estes **não são dois modos do dispositivo**. O Spenser procura ambas em cada
verificação e age sobre a que aparecer. Quando uma prescrição chega pelas duas
vias ao mesmo tempo, a Task tem precedência, e a prescrição continua a ser
dispensada exatamente uma vez. Uma unidade pode ser restringida a uma via com a
definição `orderMode`, o que é útil para demonstrar a diferença e pouco mais.

Quem fecha a prescrição depende da via usada:

| via | o que o Spenser define | o que deixa em paz |
|---|---|---|
| tag, sem Task | a MedicationRequest como `completed` | |
| uma Task | a Task como `completed`, com a dispensa em `Task.output` | a MedicationRequest, que continua `active` |

A segunda linha é deliberada. Com uma Task a coordenar o trabalho, fechar a
MedicationRequest é tarefa de quem a emitiu, não de quem a avia, e uma Task
concluída é a deixa para o emissor o fazer.

### Interface FHIR {#fhir-interface}

Servida pelo próprio dispositivo.

| Interação | Precisa de chave | Significado |
|---|---|---|
| `GET /metadata` | | CapabilityStatement desta unidade, que declara ambos os papéis, os parâmetros de pesquisa, a operação e o esquema de segurança |
| `POST /MedicationRequest` | sim | cria uma prescrição, o que a dispensa |
| `GET /MedicationRequest` e `/{id}` | | as prescrições que esta unidade aceitou |
| `POST /$dispense` | sim | dispensa numa só chamada, respondendo com a MedicationDispense |
| `GET /MedicationDispense` e `/{id}` | | o que esta unidade dispensou ou recusou |
| `GET /InventoryReport` | | stock atual, uma listagem por calha |
| `POST /InventoryReport` | sim | define o stock a partir de um relatório |

**A criação comporta-se como uma criação.** Não é preciso fornecer um `id`: a
unidade atribui um quando o omite, que é o que um servidor FHIR deve fazer. A
resposta é `201` com um cabeçalho `Location` que aponta para a prescrição criada,
um `ETag` e a
[MedicationRequest](MedicationRequest-ActionableDarkOrder.html) criada como corpo.
`Prefer: return=minimal` e `Prefer: return=OperationOutcome` são ambos
respeitados. A prescrição é guardada, pelo que pode ser lida mais tarde.

**A dispensa é um recurso separado**, em `/MedicationDispense/{id}-dispense`
quando saiu um pedaço, ou em `/MedicationDispense/{id}-declined` quando a calha
estava vazia. Quando o que pretende é a dispensa e não a prescrição, use a
operação: `POST /$dispense` recebe uma MedicationRequest, ou Parameters que a
contenham, e responde `200` com a
[MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.html). Uma
operação relata-se a si própria no recurso que devolve, pelo que uma calha vazia
continua a ser um `200`, com
[uma dispensa recusada](MedicationDispense-DeclinedDispenseOutOfStock.html). O R5
removeu `MedicationDispense.statusReason`, pelo que uma recusa traz o seu motivo
em `notPerformedReason`, que é um `CodeableReference`.

**As pesquisas são pesquisas a sério.** Ambos os repositórios respeitam `_id`,
`status`, `subject` e `_count`, e as dispensas respeitam também
`authorizingPrescription`. Uma referência corresponde por inteiro ou apenas pelo
seu id, pelo que `subject=Patient/123` e `subject=123` encontram os mesmos
registos. Os parâmetros estão declarados na CapabilityStatement, e a ligação self
do Bundle regista o que a unidade percebeu.

**Os registos sobrevivem a um reinício.** As prescrições, as dispensas e o stock
são guardados no sistema de ficheiros da unidade e não em memória, pelo que
reiniciá-la, ou atualizá-la, não apaga o que ela fez. Os registos mais antigos são
descartados quando um repositório enche.

`GET /MedicationDispense` é também a forma de perguntar a uma unidade o que tem
andado a fazer. Além das próprias dispensas, o Bundle traz uma entrada com
`search.mode` definido como `outcome`: um OperationOutcome cuja severidade,
`issue.diagnostics` e `issue.details.text` descrevem a última verificação do
servidor de prescrições, incluindo que vias a unidade está a aceitar e há quanto
tempo foi ver.

**Os erros são sempre um OperationOutcome** com `application/fhir+json`. Não há um
segundo formato de erro em parte alguma da interface FHIR.

O stock é comunicado como um
[InventoryReport](InventoryReport-SetDarkTo17.html), e pode ser definido da mesma
forma, quer como `snapshot`, quer como `difference`.

### Tempo {#time}

Uma dispensa traz `recorded`, `whenPrepared` e `whenHandedOver`, e uma recusa traz
`recorded`, logo que a unidade tenha chegado a um servidor NTP. Até lá, esses
elementos são omitidos em vez de adivinhados: um carimbo temporal ausente significa
que a unidade não tinha relógio, nunca que o evento aconteceu na época Unix. O
mesmo se aplica a `InventoryReport.reportedDateTime`.

### Atualizações {#updates}

Tanto o firmware como os ficheiros web de uma unidade podem ser substituídos por
Wi-Fi, e é isso que torna suportável um dispensador remoto. O chip mantém duas
áreas de aplicação, pelo que um carregamento é escrito naquela que não está em
execução e a unidade reinicia a partir dela; uma imagem nova só é marcada como boa
depois de ter estado a funcionar durante um minuto com rede, e a anterior continua
disponível para reverter.

| Rota | Significado |
|---|---|
| `GET /ota/status` | versão, área em execução, o quão cheia está, disponibilidade de reversão, relógio, último resultado |
| `POST /ota/firmware` | a imagem do firmware como corpo do pedido |
| `POST /ota/filesystem` | a imagem do sistema de ficheiros, que contém os ficheiros web |
| `POST /ota/file?path=/index.html` | um ficheiro, sem reinício |
| `POST /ota/check` | obtém o manifesto da versão e comunica o que está à espera |
| `POST /ota/install` | aceita o que a verificação encontrou |
| `GET /ota/status` | comunica também `updateAvailable`, `availableVersion` e há quanto tempo foi ver |
| `POST /ota/rollback` | volta à imagem anterior |

As compilações são publicadas ao lado desta especificação, em
[costateixeira.github.io/spenser/firmware/](https://costateixeira.github.io/spenser/firmware/), que é onde uma unidade
procura por omissão. Essa página lista o que mudou na compilação que está a servir
e tem ao lado os binários e o manifesto. Um manifesto descreve uma compilação para
a unidade:

```json
{ "version": "1.2.0",
  "firmware": "https://.../firmware.bin",
  "filesystem": "https://.../spiffs.bin" }
```

```
GET /setSettings?updateUrl=https://.../manifest.json&updateCheckMinutes=15
```

Uma unidade procura a cada 15 minutos por omissão, e `/ota/status` indica quando
procurou pela última vez e quando voltará a procurar. Um intervalo medido em horas
não permitiria ver isto a funcionar, e um manifesto tem menos de um kilobyte.

Procurar e aceitar são coisas separadas. `updateMode=notify`, a predefinição, faz
com que uma verificação comunique o que está à espera e pare aí: `/ota/status`
traz então `updateAvailable` e `availableVersion`, o painel mostra um aviso que
diz "New firmware available" com um botão Install, e nada reinicia sem lhe ser
pedido.

Uma unidade verifica a cada 15 minutos por omissão, e **lembra-se do que encontrou**.
O aviso sobrevive a um corte de energia, porque uma atualização que estava à espera
antes de a ficha sair continua à espera depois, e um aviso que desaparece com um
reinício é um aviso a que ninguém dá seguimento. Apaga-se sozinho quando uma
verificação posterior não encontra nada mais recente, ou quando a unidade já está
a executar a versão que foi oferecida.

**O que uma atualização contém pode ser lido antes de a aceitar.** O manifesto traz
notas de versão; a unidade guarda-as, serve-as em `/ota/status` como
`availableNotes` e `availableNotesUrl`, e o painel mostra-as numa janela quando se
prime Install, com a lista completa à distância de uma ligação. Instalar às cegas
não é uma opção que se deva dar a quem faz a manutenção.

Uma versão publicada traz o commit a partir do qual foi compilada, como
`1.2.0+a1b2c3d`. É isso que permite a uma unidade distinguir uma compilação da
seguinte, e dar o assunto por encerrado depois de instalar uma. `updateMode=install`
faz com que a unidade a aceite sozinha, o que convém a uma unidade a que ninguém
consegue chegar. Tudo o que não seja a palavra exata `install` conta como notify,
pelo que uma definição mal escrita não consegue transformar uma frota numa frota
que se atualiza sem avisar.

Cada unidade indica o que está a executar como `software.version` na sua
CapabilityStatement e como `firmwareVersion` nas suas definições, para que seja
possível distinguir as unidades de uma frota.

### O que o Spenser pede a um servidor de prescrições {#what-spenser-asks-of-an-order-server}

Aponte uma unidade para um servidor e, em cada verificação, ela faz duas pesquisas
e escreve de volta o que aconteceu:

```
GET  {server}/Task?status=requested&_include=Task:focus&_count=5
GET  {server}/MedicationRequest?_tag=http://terminology.hl7.org/CodeSystem/common-tags|actionable&status=active&intent=instance-order&_count=5
POST {server}/MedicationDispense
PUT  {server}/Task/{id}
PUT  {server}/MedicationRequest/{id}
```

O `_include` importa: o Spenser resolve `Task.focus` a partir das entradas desse
mesmo Bundle em vez de obter cada prescrição separadamente, pelo que uma Task cujo
focus não venha com ela é comunicada como um problema e ignorada.

`_count=5` importa quando se testa. Só os primeiros cinco resultados de cada
pesquisa são considerados por verificação, pelo que, com uma fila mais longa, uma
dada prescrição pode não ser apanhada numa determinada verificação.

Tanto `http://` como `https://` funcionam. Os certificados não são validados, por
isso trate a ligação como qualquer outro tráfego local não autenticado.

### Prescrições que pode copiar {#orders-you-can-copy}

O IG contém-nas como exemplos formais:

* [Prescrição tornada acionável por uma tag](MedicationRequest-ActionableDarkOrder.html)
* [Prescrição que não é acionável por si só](MedicationRequest-PlainMilkOrder.html)
* [Task a pedir que seja aviada](Task-FulfillPlainMilkOrder.html)
* [Dispensa comunicada de volta](MedicationDispense-DispenseForActionableDarkOrder.html)
* [Dispensa que não aconteceu](MedicationDispense-DeclinedDispenseOutOfStock.html)
* [Definir inventário](InventoryReport-SetDarkTo17.html) e
  [acrescentar ao inventário](InventoryReport-Add5Milk.html)

A menor prescrição útil, emitida no servidor de prescrições:

```json
{
  "resourceType": "MedicationRequest",
  "meta": {
    "tag": [
      { "system": "http://terminology.hl7.org/CodeSystem/common-tags",
        "code": "actionable" }
    ]
  },
  "status": "active",
  "intent": "instance-order",
  "medication": {
    "concept": {
      "coding": [
        { "system": "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
          "code": "chocolate-dark",
          "display": "Dark Chocolate" }
      ]
    }
  },
  "subject": { "reference": "Patient/123" },
  "dosageInstruction": [ { "text": "One bite" } ]
}
```

O mesmo corpo sem `meta.tag` é o caso negativo: o Spenser tem de o deixar em paz.
Retire a tag, acrescente uma Task que aponte para ele, e volta a ser acionável
pela outra via.

Os medicamentos vêm do
[sistema de códigos SpenserMeds](CodeSystem-SpenserMeds.html): `chocolate-dark` e
`chocolate-milk`, um pedaço por prescrição. O R5 coloca o código em
`medication.concept`; uma prescrição publicada diretamente pode também usar a
grafia `medicationCodeableConcept` do R4, que este firmware ainda aceita.

### Interface não FHIR {#non-fhir-interface}

Tudo o que se segue é a API administrativa da própria unidade. É JSON ou texto
simples, não é FHIR e não se destina à troca de dados clínicos. Existe para
configurar uma unidade, para a conduzir durante uma demonstração e para servir o
painel integrado.

| Grupo | Endpoints |
|---|---|
| Prescrições | `/checkOrders` coloca uma verificação em fila e devolve `202`, `/orders` comunica a última verificação ao painel, `/forgetOrders` limpa a lista de prescrições já tratadas |
| Definições | `/settings`, `/setSettings`, `/resetSettings` |
| Atualizações | `/ota/status`, `/ota/firmware`, `/ota/filesystem`, `/ota/file`, `/ota/check`, `/ota/rollback` |
| A chave | `/key`, dentro da janela descrita acima |
| Stock e hardware | `/inventory`, `/setInventory`, `/resetInventory`, `/setServos`, `/flashServo1`, `/flashServo2`, `/setColor`, `/battery`, `/reset` |
| Wi-Fi e identidade | `/`, `/scan`, `/cfg`, `/save`, `/wifi-settings`, `/wifi-reset`, `/wifi-reboot-config`, `/getMac`, `/setMac`, `/clearMac` |
| Portal cativo | `/generate_204`, `/hotspot-detect.html`, `/fwlink`, `/ncsi.txt`, `/connecttest.txt` |

`/setSettings` aceita qualquer um de `serverUrl`, `orderMode` com os valores `both`,
`tag` ou `task`, `orderQuery`, `taskQuery`, `pollEnabled`, `pollSeconds` entre 5 e
3600, `writeBack`, `giveUpOnStockEmpty`, `updateUrl`, `updateCheckHours` e os
parâmetros dos servos. Responde com o documento completo das definições, que inclui
a versão do firmware e nunca inclui a chave.

Uma unidade verifica o seu servidor de prescrições a cada `pollSeconds`, 30 por
omissão, enquanto `pollEnabled` estiver ligado. `/checkOrders` força uma verificação
imediata. Responde antes de o trabalho estar feito, porque o trabalho HTTP acontece
no ciclo principal e nunca dentro de um gestor de pedidos, pelo que um cliente deve
esperar que a verificação termine em vez de assumir que já terminou.

`giveUpOnStockEmpty` decide o que acontece a uma prescrição que não pode ser aviada.
Desligado, a prescrição é comunicada uma vez como esgotada e fica aberta, de modo
que reabastecer a calha a avia numa verificação posterior. Ligado, é comunicada uma
vez e abandonada, e uma Task coordenadora passa a `failed`.

Tudo o que não tiver correspondência recorre a um ficheiro estático do sistema de
ficheiros do dispositivo, e é assim que o painel é servido. `OPTIONS` devolve `200`
para o preflight de CORS.

### Interfaces que não são HTTP {#interfaces-that-are-not-http}

* **mDNS.** A unidade anuncia-se como `spenser` com um serviço HTTP na porta 80, pelo
  que `http://spenser.local` funciona sem conhecer o seu endereço.
* **Ponto de acesso e portal cativo.** Sem Wi-Fi configurado, serve uma rede aberta e
  responde a todos os nomes DNS, pelo que um telemóvel ou portátil abre a página de
  configuração sozinho.
* **Série.** Registos a 115200 baud, incluindo todas as pesquisas de prescrições e
  escritas de volta.
* **O botão.** Uma pressão curta dispensa. Três segundos fazem um reinício suave. Dez
  segundos apagam as credenciais guardadas, e o LED fica vermelho enquanto se mantém
  premido, para avisar antes de o largar.

### Trabalhar com um agente de IA {#working-with-an-ai-agent}

Cada unidade serve um guia escrito para agentes de IA em
**`http://spenser.local/llms.txt`**. Descreve todos os endpoints, as formas exatas
aceites e produzidas, exemplos completos, um teste que exercita todo o ciclo e os
erros em que as pessoas costumam cair. Aponte um agente para esse URL e ele pode
escrever exemplos, testes ou um cliente sem adivinhar, contra a unidade que tem à
frente e não contra documentação que possa ter ficado desatualizada.

É detetável a partir do FHIR: a CapabilityStatement em `/metadata` indica-o em
`implementation.description`, de modo que um agente que comece no ponto de entrada
FHIR o encontra.

Duas coisas combinam bem com ele. O ficheiro `AGENTS.md` no repositório de código
trata do próprio repositório, de como compilar e gravar, de onde ficam as rotas e de
como executar os testes. A coleção Bruno em `bruno/` é uma versão executável desta
página: está dividida entre o servidor de prescrições de um lado e o dispositivo do
outro, e cada cenário faz as suas verificações sobre FHIR e não sobre prosa.
