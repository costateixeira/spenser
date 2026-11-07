Esta é a especificação completa do Spenser, um companheiro FHIR para programadores. 


**O Spenser é um dispensador de chocolate que suporta uma interface FHIR para requisitar chocolates (como medicamentos), bem como para ajustar e monitorizar o inventário.**

Esta especificação de código aberto fornece tudo o que é necessário para criar o seu próprio Spenser: 
* Hardware (peças para impressão 3D + componentes eletrónicos + peças para impressão 3D)
* Software (para o chip ESP32)

**Esta documentação e este conjunto de artefactos ainda estão em desenvolvimento.**  
{:.stu-note}

**FHIR® e o ícone da chama são marcas registadas da HL7 e são utilizados com a permissão da HL7. A utilização da marca FHIR não constitui um aval do conteúdo deste produto por parte da HL7**

### Contexto

* Os programadores precisam de chocolate. Toda a gente precisa de chocolate.
* O chocolate pode ser considerado terapêutico - ou profilático. Por isso, o Spenser considera o chocolate um medicamento.


  Shrime, M. G., Bauer, S. R., McDonald, A. C., Chowdhury, N. H., Coltart, C. E., & Ding, E. L. (2011).  
  *Flavonoid-rich cocoa consumption affects multiple cardiovascular risk factors in a meta-analysis of short-term studies.*  
  *The Journal of Nutrition, 141*(11), 1982–1988.  
  [https://doi.org/10.3945/jn.111.145482](https://doi.org/10.3945/jn.111.145482)  


<br>
A conceção e a implementação deste produto foram sujeitas a testes unitários - muitas unidades foram consumidas para testar o funcionamento e o efeito do sistema.

