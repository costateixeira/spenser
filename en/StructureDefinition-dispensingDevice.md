# Dispensing device - Spenser - a developer's companion v1.0.0

## Extension: Dispensing device 

**Context of Use**

**Usage info**

**Usages:**

* Use this Extension: [SpenserRequest](StructureDefinition-SpenserRequest.md)
* Examples for this Extension: [MedicationRequest/ActionableDarkOrderForOneUnit](MedicationRequest-ActionableDarkOrderForOneUnit.md) and [MedicationRequest/PlainDarkOrderForOneUnit](MedicationRequest-PlainDarkOrderForOneUnit.md)

You can also check for [usages in the FHIR IG Statistics](https://packages2.fhir.org/xig/resource/jct.fhir.spenser|current/StructureDefinition/StructureDefinition-dispensingDevice.json)

### Formal Views of Extension Content

 [Description Differentials, Snapshots, and other representations](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#structure-definitions). 

 

Other representations of profile: [CSV](../StructureDefinition-dispensingDevice.csv), [Excel](../StructureDefinition-dispensingDevice.xlsx), [Schematron](../StructureDefinition-dispensingDevice.sch) 



## Resource Content

```json
{
  "resourceType" : "StructureDefinition",
  "id" : "dispensingDevice",
  "extension" : [{
    "url" : "http://hl7.org/fhir/StructureDefinition/structuredefinition-type-characteristics",
    "valueCode" : "can-bind"
  }],
  "url" : "http://costateixeira.github.io/spenser/StructureDefinition/dispensingDevice",
  "version" : "1.0.0",
  "name" : "DispensingDevice",
  "title" : "Dispensing device",
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
  "description" : "The Spenser unit that is to dispense this order, named by a logical reference: the unit's identifier in http://costateixeira.github.io/spenser/unit, which is its name, Spenser- and the last two bytes of its factory MAC.\n\nR5 has no element on MedicationRequest for this. MedicationRequest.performer and MedicationRequest.device take a DeviceDefinition, a kind of device, and dispenseRequest.dispenser takes only an Organization. A logical reference needs nothing on the server: the unit does not have to be registered as a Device for the order to name it.\n\nWhen a Task makes the order actionable, a Device in Task.requestedPerformer takes precedence over this extension. On an order with no Task, or a Task that names no unit, a unit acts on this extension: it skips an order that names another unit.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "fhirVersion" : "5.0.0",
  "mapping" : [{
    "identity" : "rim",
    "uri" : "http://hl7.org/v3",
    "name" : "RIM Mapping"
  }],
  "kind" : "complex-type",
  "abstract" : false,
  "context" : [{
    "type" : "element",
    "expression" : "MedicationRequest"
  }],
  "type" : "Extension",
  "baseDefinition" : "http://hl7.org/fhir/StructureDefinition/Extension",
  "derivation" : "constraint",
  "differential" : {
    "element" : [{
      "id" : "Extension",
      "path" : "Extension",
      "short" : "Dispensing device",
      "definition" : "The Spenser unit that is to dispense this order, named by a logical reference: the unit's identifier in http://costateixeira.github.io/spenser/unit, which is its name, Spenser- and the last two bytes of its factory MAC.\n\nR5 has no element on MedicationRequest for this. MedicationRequest.performer and MedicationRequest.device take a DeviceDefinition, a kind of device, and dispenseRequest.dispenser takes only an Organization. A logical reference needs nothing on the server: the unit does not have to be registered as a Device for the order to name it.\n\nWhen a Task makes the order actionable, a Device in Task.requestedPerformer takes precedence over this extension. On an order with no Task, or a Task that names no unit, a unit acts on this extension: it skips an order that names another unit."
    },
    {
      "id" : "Extension.extension",
      "path" : "Extension.extension",
      "max" : "0"
    },
    {
      "id" : "Extension.url",
      "path" : "Extension.url",
      "fixedUri" : "http://costateixeira.github.io/spenser/StructureDefinition/dispensingDevice"
    },
    {
      "id" : "Extension.value[x]",
      "path" : "Extension.value[x]",
      "min" : 1,
      "type" : [{
        "code" : "Reference",
        "targetProfile" : ["http://hl7.org/fhir/StructureDefinition/Device"]
      }]
    },
    {
      "id" : "Extension.value[x].reference",
      "path" : "Extension.value[x].reference",
      "max" : "0"
    },
    {
      "id" : "Extension.value[x].identifier",
      "path" : "Extension.value[x].identifier",
      "min" : 1
    },
    {
      "id" : "Extension.value[x].identifier.system",
      "path" : "Extension.value[x].identifier.system",
      "min" : 1,
      "fixedUri" : "http://costateixeira.github.io/spenser/unit"
    },
    {
      "id" : "Extension.value[x].identifier.value",
      "path" : "Extension.value[x].identifier.value",
      "min" : 1
    }]
  }
}

```
