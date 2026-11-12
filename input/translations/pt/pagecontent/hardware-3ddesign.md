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

Estas são as mesmas peças com a pista cortada 7 mm mais estreita, 9 mm
menos funda e a guia 20,2 mm mais curta, pelo que aceitam um pedaço **até
40 × 30 mm**, com a mesma espessura de 5,5 a 7,5 mm. Meça um pedaço antes
de imprimir: 30 mm é o limite ao longo do empurrão.

A profundidade é a medida cortada ao pedaço, e é exacta. A largura não é, nem
pode ser: o encaixe onde desce a Atomic Motion Base, o canal onde entram as
fichas dos servos e o próprio alojamento do servo ficam todos entre as mesmas
duas paredes laterais da pista e ocupam 53 dos seus 61 mm, pelo que a única
largura livre é a faixa de 7 mm junto à saliência de retenção. Um pedaço de
40 mm de largura fica com 14 mm de folga lateral no que resta, o que não custa
nada: um pedaço de 30 × 40 não roda numa pista de 31 mm de fundo, por mais
larga que ela seja.

Duas coisas mudam na construção. Defina `anglePush=81` nesta unidade, em vez
do valor por omissão de 77. E monte o braço de modo a ficar, em repouso,
cerca de 47° recuado em relação à perpendicular à pista, e não a esquadria:
isso recua todo o percurso e é o que permite o corpo ser tão curto. A
verificação é que, em repouso, a face de empurrar fique logo atrás do
empilhamento de chocolate. No fim do curso a cauda fica pouco antes da boca, o
que é intencional. O pino é a mesma peça de antes e aqui não precisa de ser
furado: o seu orifício no braço tem 3 mm nestes ficheiros, contra 2,76 no
braço padrão, que é impresso abaixo da medida e aperta sobre o pino de
2,55 mm.

Para outro tamanho de pedaço, [`tools/resize/build.py`](https://github.com/costateixeira/spenser/blob/master/tools/resize/build.py) corta estas três
peças à medida dele e mostra o que fica o curso. O pedaço indica-se como
largura da pista × ao longo dela × espessura, pelo que
`--piece 40x30x7 --name small` é esta variante; sem nada depois do comando, o
script toma a mignonette belga para a qual as peças acima já estão cortadas e
diz que não há nada a cortar.

| Peça | Descrição | Transferências |
|------|-------------|-----------|
| **Corpo** | Uma pista de 54 × 31 mm em vez de 61 × 40; 57 × 80,8 × 105 mm no total. Mais nada nele se move: a saliência que segura o empurrador, a caixa do servo, a abertura de saída, o encaixe do módulo e o canal ao lado dele estão todos onde o corpo padrão os tem. | [STL](spenser-body-small.stl) |
| **Empurrador** | 52,9 × 46 mm, para corresponder à pista mais estreita, com a ranhura do pino aberta a 2,8 mm. | [STL](spenser-pusher-small.stl) |
| **Braço** | 26,75 mm entre os furos em vez de 41, o que dá um curso de 34,53 mm com `anglePush=81`, à medida da pista menos funda. | [STL](spenser-arm-small.stl) |
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
