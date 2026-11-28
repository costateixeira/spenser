# Utilização - Spenser - a developer's companion v1.0.0

## Utilização

 
Esta página inclui traduções a partir da língua original em que o guia foi criado. Informações sobre estas traduções e instruções para fornecer feedback podem ser encontradas [aqui](translationinfo.md). 

O Spenser dispensa chocolate e trata o chocolate como um medicamento. Por isso, não se carrega num botão para obter um pedaço. Emite-se uma prescrição, e o dispensador decide se está autorizado a agir sobre ela.

Esta página percorre esse processo de fora para dentro. A página [Interfaces](interfaces.md) é a referência que está por trás dela.

### Para onde vai a prescrição

Com uma unidade pousada na sua secretária é possível falar diretamente. Com uma unidade noutro sítio não é, pelo que a organização que interessa é aquela em que as prescrições ficam num servidor FHIR e o dispensador as vai procurar.

O dispensador consulta o seu servidor de prescrições a cada trinta segundos. Emite lá uma prescrição e, em cerca de meio minuto, cai da máquina um pedaço de chocolate. Nada empurra nada para o dispensador, e nada precisa de saber onde ele está.

### A prescrição

Publique uma MedicationRequest no servidor de prescrições, usando os códigos de [SpenserMeds](CodeSystem-SpenserMeds.md): `chocolate-dark` ou `chocolate-milk`. Um pedaço de cada vez, que é a única quantidade permitida pelo perfil [SpenserRequest](StructureDefinition-SpenserRequest.md).

```
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

O exemplo completo está [aqui](MedicationRequest-ActionableDarkOrder.md). A parte que faz o trabalho é `meta.tag`.

### Porquê a tag

Uma MedicationRequest é uma autorização, não uma instrução. Alguém pode ter uma prescrição registada sem que ninguém pretenda que seja aviada agora mesmo, e um dispensador que se esvazia para cima da sala sempre que alguém escreve uma prescrição não tem grande utilidade para ninguém.

Por isso, o Spenser espera que lhe digam que uma prescrição está pronta para ser executada, o que a orientação Clinical Orders Workflow designa por prescrição acionável. Retire a tag do exemplo acima e obtém [uma prescrição que o Spenser ignora](MedicationRequest-PlainMilkOrder.md): continua a ser uma prescrição perfeitamente válida, só que ninguém pediu que fosse aviada.

### A outra forma de o dizer

Por vezes, a prescrição é escrita por uma pessoa e o pedido para a aviar chega mais tarde, ou de outro lado. É para isso que serve uma Task. Deixe a prescrição simples e publique [uma Task que aponta para ela](Task-FulfillPlainMilkOrder.md) com o estado `requested` e a prescrição em `Task.focus`.

As duas vias funcionam, e o dispensador procura ambas em cada consulta. Não é preciso configurá-lo para um modo ou para o outro. Se uma prescrição aparecer com uma tag e uma Task ao mesmo tempo, continua a ser dispensada uma só vez.

A diferença nota-se depois, em quem fecha o quê:

| | | |
| :--- | :--- | :--- |
| a tag | a prescrição como`completed` | nada |
| uma Task | a Task como`completed`, com a dispensa em`Task.output` | a prescrição, que continua`active` |

A segunda linha é deliberada. Quando é uma Task a coordenar o trabalho, concluir a prescrição é assunto de quem a emitiu, e uma Task concluída é o sinal para o fazer.

### O que volta

Cada pedaço de chocolate produz uma [MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.md) no servidor, que aponta de volta para a prescrição através de `authorizingPrescription`. É o registo de que algo aconteceu fisicamente, e é o que deve procurar quando quiser saber se a sua prescrição foi aviada:

```
GET {server}/MedicationDispense?_count=20

```

### Quando não é possível

Uma calha fica vazia. O Spenser di-lo em vez de ficar calado: publica [uma dispensa que não aconteceu](MedicationDispense-DeclinedDispenseOutOfStock.md), com o estado `declined` e o motivo em `notPerformedReason`. Comunica-o uma vez, não em cada consulta.

O que acontece depois à prescrição é uma definição. Por omissão, a prescrição fica aberta, de modo que reabastecer a calha a avia numa consulta posterior sem que ninguém tenha de publicar nada novamente. A alternativa é abandoná-la, e se uma Task estava a coordenar o trabalho, essa Task passa a `failed`.

### Observar uma unidade

O dispensador mantém o seu próprio registo do que fez, em FHIR, quer a prescrição tenha vindo de um servidor, quer lhe tenha sido entregue diretamente:

```
GET http://spenser.local/MedicationDispense

```

O Bundle contém as suas dispensas recentes, das mais novas para as mais antigas. Traz também uma entrada com `search.mode` igual a `outcome`: um OperationOutcome que diz como correu a última consulta, com que servidor falou, há quanto tempo, quantas prescrições encontrou e quantas aviou. Se não estiver a sair nada, leia essa entrada primeiro. Normalmente diz porquê, e distingue um dispensador que não consegue chegar ao seu servidor de outro que está a funcionar corretamente e a quem simplesmente não foi dado nada sobre o qual esteja autorizado a agir.

O ecrã do próprio dispensador mostra as mesmas duas coisas, que são as duas que importam: o que há em cada calha e o que fez a última verificação.

Nada do que foi descrito acima precisa de autorização. Alterar uma unidade precisa: dispensar manualmente, definições, stock, Wi-Fi e atualizações exigem todos a chave dessa unidade, que ela imprime na consola série ao arrancar e que entrega durante cinco minutos após um reinício. Ler o que ela fez nunca exige.

### As definições que importam

A maior parte da configuração de uma unidade diz respeito a servos, Wi-Fi e LED. Estas são as que alteram o comportamento das prescrições:

| | |
| :--- | :--- |
| Order server | o URL de base FHIR que consulta |
| Accepted routes | tanto uma tag como uma Task, que é a predefinição, ou restringida a uma delas para demonstrar a diferença |
| Check every | segundos entre consultas, 30 por omissão |
| Report back | se escreve a dispensa e o fecho no servidor |
| Give up when the lane is empty | abandonar uma prescrição que não pode ser aviada, ou mantê-la aberta até um reabastecimento |

### Quando está ao lado dele

Pode publicar uma prescrição diretamente no dispensador. Nesse caso não há tag nem Task, porque publicá-la manualmente é, em si, a decisão de dispensar, e ele responde com a MedicationDispense:

```
POST http://spenser.local/MedicationRequest

```

E há o botão na parte da frente, que dispensa sem FHIR nenhum.

Uma unidade fora de alcance continua a poder ter manutenção: tanto o seu firmware como os seus ficheiros web podem ser substituídos por Wi-Fi, e ela pode manter-se atualizada a partir de uma versão publicada. A página [Interfaces](interfaces.md) tem os pormenores.

**Para emergências, o Spenser tem um botão "Hit me" para dispensar algum chocolate.**
 **Esta funcionalidade deve ser usada com precaução.**

