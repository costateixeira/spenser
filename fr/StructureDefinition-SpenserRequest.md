# SpenserRequest - Spenser - a developer's companion v1.0.0

## Profil de ressource: SpenserRequest 

**Utilisations:**

* Exemples pour ce/t/te Profil: [MedicationRequest/ActionableDarkOrder](MedicationRequest-ActionableDarkOrder.md), [MedicationRequest/ActionableDarkOrderForOneUnit](MedicationRequest-ActionableDarkOrderForOneUnit.md), [MedicationRequest/PlainDarkOrderForOneUnit](MedicationRequest-PlainDarkOrderForOneUnit.md), [MedicationRequest/PlainMilkOrder](MedicationRequest-PlainMilkOrder.md) and [MedicationRequest/med-request-1234](MedicationRequest-med-request-1234.md)

Vous pouvez également vérifier [les usages dans le FHIR IG Statistics](https://packages2.fhir.org/xig/jct.fhir.spenser|current/StructureDefinition/SpenserRequest)

### Vues formelles du contenu du profil

 [Description des profils, des différentiels, des instantanés et de leurs représentations](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#structure-definitions). 

*  [Tableau des éléments clés](#tabs-key) 
*  [Tableau différentiel (differential)](#tabs-diff) 
*  [Tableau récapitulatif (snapshot)](#tabs-snap) 
*  [Statistiques/Références](#tabs-summ) 
*  [Tous](#tabs-all) 

#### Bindings terminologiques

#### Contraintes

Cette structure est dérivée de [MedicationRequest](http://hl7.org/fhir/R5/medicationrequest.html) 

#### Bindings terminologiques (différentiel)

#### Bindings terminologiques

#### Contraintes

Cette structure est dérivée de [MedicationRequest](http://hl7.org/fhir/R5/medicationrequest.html) 

 **Vue des éléments clés** 

#### Bindings terminologiques

#### Contraintes

 **Vue différentielle** 

Cette structure est dérivée de [MedicationRequest](http://hl7.org/fhir/R5/medicationrequest.html) 

#### Bindings terminologiques (différentiel)

 **Vue d'ensembleView** 

#### Bindings terminologiques

#### Contraintes

Cette structure est dérivée de [MedicationRequest](http://hl7.org/fhir/R5/medicationrequest.html) 

 

Autres représentations du profil : [CSV](../StructureDefinition-SpenserRequest.csv), [Excel](../StructureDefinition-SpenserRequest.xlsx), [Schematron](../StructureDefinition-SpenserRequest.sch) 



## Resource Content

```json
{
  "resourceType" : "StructureDefinition",
  "id" : "SpenserRequest",
  "url" : "http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest",
  "version" : "1.0.0",
  "name" : "SpenserRequest",
  "status" : "active",
  "date" : "2026-11-13T21:21:03+00:00",
  "publisher" : "José Costa Teixeira",
  "contact" : [{
    "name" : "José Costa Teixeira",
    "telecom" : [{
      "system" : "url",
      "value" : "https://github.com/costateixeira"
    }]
  },
  {
    "name" : "José Costa Teixeira",
    "telecom" : [{
      "system" : "email",
      "value" : "you-know.it@gmail.com",
      "use" : "work"
    }]
  }],
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "fhirVersion" : "5.0.0",
  "mapping" : [{
    "identity" : "workflow",
    "uri" : "http://hl7.org/fhir/workflow",
    "name" : "Workflow Pattern"
  },
  {
    "identity" : "script10.6",
    "uri" : "http://ncpdp.org/SCRIPT10_6",
    "name" : "Mapping to NCPDP SCRIPT 10.6"
  },
  {
    "identity" : "w5",
    "uri" : "http://hl7.org/fhir/fivews",
    "name" : "FiveWs Pattern Mapping"
  },
  {
    "identity" : "rim",
    "uri" : "http://hl7.org/v3",
    "name" : "RIM Mapping"
  },
  {
    "identity" : "v2",
    "uri" : "http://hl7.org/v2",
    "name" : "HL7 V2 Mapping"
  }],
  "kind" : "resource",
  "abstract" : false,
  "type" : "MedicationRequest",
  "baseDefinition" : "http://hl7.org/fhir/StructureDefinition/MedicationRequest",
  "derivation" : "constraint",
  "differential" : {
    "element" : [{
      "id" : "MedicationRequest",
      "path" : "MedicationRequest"
    },
    {
      "id" : "MedicationRequest.extension",
      "path" : "MedicationRequest.extension",
      "slicing" : {
        "discriminator" : [{
          "type" : "value",
          "path" : "url"
        }],
        "ordered" : false,
        "rules" : "open"
      }
    },
    {
      "id" : "MedicationRequest.extension:dispensingDevice",
      "path" : "MedicationRequest.extension",
      "sliceName" : "dispensingDevice",
      "min" : 0,
      "max" : "1",
      "type" : [{
        "code" : "Extension",
        "profile" : ["http://costateixeira.github.io/spenser/StructureDefinition/dispensingDevice"]
      }]
    },
    {
      "id" : "MedicationRequest.status",
      "path" : "MedicationRequest.status",
      "patternCode" : "active"
    },
    {
      "id" : "MedicationRequest.intent",
      "path" : "MedicationRequest.intent",
      "patternCode" : "instance-order"
    },
    {
      "id" : "MedicationRequest.medication",
      "path" : "MedicationRequest.medication",
      "binding" : {
        "strength" : "required",
        "valueSet" : "http://costateixeira.github.io/spenser/ValueSet/SpenserMedsVS"
      }
    },
    {
      "id" : "MedicationRequest.medication.concept.coding.code",
      "path" : "MedicationRequest.medication.concept.coding.code",
      "min" : 1
    },
    {
      "id" : "MedicationRequest.dispenseRequest.quantity.value",
      "path" : "MedicationRequest.dispenseRequest.quantity.value",
      "patternDecimal" : 1
    }]
  }
}

```
