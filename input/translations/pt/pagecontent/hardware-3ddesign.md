Seguem-se as peças 3D usadas para construir o **Spenser**.


### Descrição

<br clear="all">

| Peça | Imagem | Descrição | Transferências |
|------|-------|-------------|-----------|
| **Corpo** | ![](spenser-body.png){:width="120px"} | Segura a pilha de chocolates, o servomotor e as guias de deslizamento, sobre a sua própria base. | [STL](spenser-body.stl) |
| **Empurrador** | ![](spenser-pusher.png){:width="120px"} | Desliza ao longo das guias e empurra um chocolate para fora. | [STL](spenser-pusher.stl) |
| **Braço** | ![](spenser-arm.png){:width="120px"} | Fixa-se à cruzeta do servo e move o empurrador. | [STL](spenser-arm.stl) |
| **Pino** | ![](spenser-pin.png){:width="120px"} | Eixo que liga o braço ao empurrador. | [STL](spenser-pin.stl) |
{:.table-bordered}

### Para chocolates mais pequenos {#for-smaller-chocolates}

A pista acima aceita um pedaço até 60 × 39 mm, o que serve um napolitain
belga. Um napolitain suíço é mais pequeno — um Lindt Napolitain tem cerca de
40 × 25 mm — e fica com espaço para se mexer. A folga de 9 mm ao longo do
empurrão é a que importa: basta para um pedaço escorregar para a frente por
baixo da parede de retenção, onde o empurrador o encontra de topo.

Estas são as mesmas peças com a pista cortada 19,25 mm mais estreita, 9 mm
menos funda e a guia 20,2 mm mais curta, pelo que aceitam um pedaço **até
40 × 30 mm**, com a mesma espessura de 5,5 a 7,5 mm. Meça um pedaço antes
de imprimir: 30 mm é o limite ao longo do empurrão.

Três coisas mudam na construção. Defina `anglePush=81` nesta unidade, em vez
do valor por omissão de 77. Monte o braço de modo a ficar, em repouso, cerca
de 47° recuado em relação à perpendicular à pista, e não a esquadria: isso
recua todo o percurso e é o que permite o corpo ser tão curto. A verificação
é que, em repouso, a face de empurrar fique logo atrás do empilhamento de
chocolate. E abra o furo do pino no braço a 2,6 mm — é impresso como um
furo-guia de 1,25 mm, onde o pino de 2,55 mm não entra. No fim do curso a
cauda sai 1,7 mm pela boca, o que é intencional; o pino é a mesma peça de
antes.

| Peça | Descrição | Transferências |
|------|-------------|-----------|
| **Corpo** | Uma pista de 41,75 × 31 mm em vez de 61 × 40; 44,75 × 80,8 × 107 mm no total. A saliência que segura o empurrador fica 2 mm mais alta, para dar passagem ao braço, e o apoio onde assentam as orelhas do servo volta a descer os mesmos 2 mm, para que o braço não suba com ele. | [STL](spenser-body-small.stl) |
| **Empurrador** | 40,65 × 46 mm, para corresponder à pista mais estreita, com a ranhura do pino aberta a 2,8 mm. | [STL](spenser-pusher-small.stl) |
| **Braço** | 28,75 mm entre os furos em vez de 41, o que dá um curso de 37,11 mm com `anglePush=81`. | [STL](spenser-arm-small.stl) |
| **Pino** | A mesma peça de cima. | [STL](spenser-pin.stl) |
{:.table-bordered}

### Lista de materiais

**As quantidades indicadas são para o dispensador de 2 posições.**

| Artigo   | Descrição | Quantidade |
|---|---|---------|
| Corpo | Segura os chocolates, o motor e as guias de deslizamento | 2 |
| Braço | Braço rotativo fixado ao servo | 2 |
| Pino  | Liga o braço ao empurrador | 2  |
| Empurrador  | Empurra um chocolate para fora  | 2  |
{:.table-bordered}
