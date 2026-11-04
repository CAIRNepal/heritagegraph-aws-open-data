# HeritageGraph: Open Knowledge Graph Dataset for Cultural Heritage

HeritageGraph is an open RDF knowledge graph dataset for cultural heritage, published on the Registry of Open
Data on AWS. Its first use case is **Nepal**: release v1.0.0 covers **1,652 monuments of Nepal**: temples, *patis* and *sattals*
(rest houses), Buddhist monastic buildings, stone water spouts (*dhunge dhara*), *chaityas* and others. For each
monument it records names (in English and Nepali), identifiers, location and coordinates, architecture, condition
and threats, the events in its history, the objects it houses, and its main deity and religious tradition.

The graph is built from the monument records of the
[Digital Archive of Nepalese Arts and Monuments (DANAM)](https://danam.cats.uni-heidelberg.de), Heidelberg
University, and modelled with the [HeritageGraph ontology](https://cairnepal.github.io/heritagegraphontology/),
which is aligned with CIDOC-CRM and PROV-O. Every monument links back to the DANAM page it was derived from.
It is published by [CAIR-Nepal](https://cair-nepal.org) through the AWS Open Data Sponsorship Program.

| | |
|---|---|
| Registry page | <https://registry.opendata.aws/cair-nepal-heritage-graph> (once published) |
| S3 bucket | `s3://cair-nepal-heritage-graph/` (Region `us-east-1`, public, no AWS account needed) |
| Tutorial | [Get to Know a Dataset: HeritageGraph](cair-nepal-heritage-graph/get-to-know-a-dataset.ipynb) |
| Source code | [CAIRNepal/HeritageGraphDataset](https://github.com/CAIRNepal/HeritageGraphDataset) (builder, queries, tests) |
| Ontology | [cairnepal.github.io/heritagegraphontology](https://cairnepal.github.io/heritagegraphontology/) |
| Contact | info@cair-nepal.org |

This repository holds the dataset's documentation (this file) and the tutorial notebook. It does not hold the
data itself. The Registry of Open Data entry is maintained in
[CAIRNepal/open-data-registry](https://github.com/CAIRNepal/open-data-registry).

---

## Contents

1. [Bucket layout](#1-bucket-layout)
2. [Accessing the data](#2-accessing-the-data)
3. [What the graph contains](#3-what-the-graph-contains)
4. [Data dictionary](#4-data-dictionary)
5. [Example queries](#5-example-queries)
6. [Limitations](#6-limitations)
7. [Releases and versioning](#7-releases-and-versioning)
8. [Licence](#licence)
9. [Citation](#9-citation)
10. [This repository](#10-this-repository)

---

## 1. Bucket layout

The bucket has one top-level prefix per release. A release prefix is never changed after it is published, so you
can pin your work to a version.

```text
s3://cair-nepal-heritage-graph/
└── v1.0.0/
    ├── heritagegraph-nepal.ttl       19.5 MB   RDF Turtle
    ├── heritagegraph-nepal.jsonld    35.4 MB   JSON-LD
    ├── heritagegraph-nepal.nt.gz      7.5 MB   gzipped N-Triples, for bulk loading
    ├── metadata.json                  3.9 KB   Schema.org / DCAT description: counts, namespaces, checksums
    └── checksums.sha256               355 B    SHA-256 of each file
```

The three serializations contain the same 221,364 triples. Download whichever suits your tools:

| File | Format | Best for |
|---|---|---|
| `heritagegraph-nepal.ttl` | [Turtle](https://www.w3.org/TR/turtle/) | Python (`rdflib`), reading by eye |
| `heritagegraph-nepal.jsonld` | [JSON-LD](https://www.w3.org/TR/json-ld11/) | web applications, JSON tooling |
| `heritagegraph-nepal.nt.gz` | [N-Triples](https://www.w3.org/TR/n-triples/), gzip | streaming; bulk loading into a triplestore (Amazon Neptune, Apache Jena Fuseki, GraphDB) |

## 2. Accessing the data

The bucket is public: use unsigned requests and no AWS credentials.

**AWS CLI**

```bash
aws s3 ls s3://cair-nepal-heritage-graph/v1.0.0/ --no-sign-request
aws s3 cp s3://cair-nepal-heritage-graph/v1.0.0/heritagegraph-nepal.ttl . --no-sign-request
aws s3 sync s3://cair-nepal-heritage-graph/v1.0.0/ ./heritagegraph-nepal-v1.0.0/ --no-sign-request

# verify the download
cd heritagegraph-nepal-v1.0.0 && sha256sum -c checksums.sha256   # macOS: shasum -a 256 -c checksums.sha256
```

**HTTPS** (also works from a browser; CORS allows `GET` from any origin)

```text
https://cair-nepal-heritage-graph.s3.us-east-1.amazonaws.com/v1.0.0/heritagegraph-nepal.ttl
```

**Python**

```python
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from rdflib import Graph

s3 = boto3.client("s3", region_name="us-east-1", config=Config(signature_version=UNSIGNED))
body = s3.get_object(Bucket="cair-nepal-heritage-graph", Key="v1.0.0/heritagegraph-nepal.ttl")["Body"].read()

g = Graph()
g.parse(data=body, format="turtle")
print(len(g), "triples")   # 221364
```

**Amazon Neptune.** The Neptune bulk loader reads from an S3 bucket in the same Region as the cluster. Copy
`heritagegraph-nepal.nt.gz` into your own bucket in your cluster's Region, then load it with format `ntriples`.

## 3. What the graph contains

Counts for release v1.0.0.

| | count | notes |
|---|---:|---|
| Triples | 221,364 | |
| Monuments | 1,652 | all `hg:ArchitecturalStructure`; a monument can have more than one type |
| &nbsp;&nbsp;Temples | 730 | `hg:Temple` |
| &nbsp;&nbsp;Patis / Sattals | 273 / 101 | rest houses (`hg:RestHouse`) |
| &nbsp;&nbsp;Buddhist monastic buildings | 215 | `hg:BuddhistMonument` |
| &nbsp;&nbsp;Stone water spouts | 132 | `hg:DhungeDhara` |
| &nbsp;&nbsp;Chaityas | 71 | `hg:Chaitya` |
| &nbsp;&nbsp;Other | 164 | no more specific type |
| Events | 5,098 | 1,996 historical events, 1,808 productions, 695 destructions, 284 transfers of custody, 300 ritual events (128 consecrations, 87 enshrinements) |
| Objects housed in monuments | 7,154 | 3,116 iconographic objects (1,542 *murtis*, 6 *paubhas*), 292 architectural elements, 3,748 other; a few objects have two types. (`metadata.json` reports 8,806 because it also counts the monuments.) |
| Condition assessments | 1,592 | 1,577 linked to a monument |
| Places | 1,021 | tola, municipality, district, province |
| Deities | 355 | main deities named by DANAM |
| Point geometries | 1,626 | WGS84 latitude/longitude and GeoSPARQL WKT |

Coverage follows DANAM, which documents mainly the Kathmandu Valley (Province 3), with smaller groups of records in
western Nepal (e.g. Dullu, Jumla, Ajaymeru). DANAM records were collected on 16 March 2026.

## 4. Data dictionary

### Namespaces

| Prefix | IRI | Used for |
|---|---|---|
| `hg:` | `https://cair-nepal.org/heritagegraph/` | HeritageGraph ontology classes and properties |
| `res:` | `https://data.cairnepal.org/heritage/resource/` | instances (monuments, events, objects, places, deities) |
| `crm:` | `http://www.cidoc-crm.org/cidoc-crm/` | CIDOC-CRM |
| `prov:` | `http://www.w3.org/ns/prov#` | provenance |
| `geo:` | `http://www.w3.org/2003/01/geo/wgs84_pos#` | WGS84 latitude / longitude |
| `geosparql:` | `http://www.opengis.net/ont/geosparql#` | geometries (WKT) |
| `aat:` | `http://vocab.getty.edu/aat/` | Getty Art & Architecture Thesaurus |
| `schema:` | `https://schema.org/` | names, URLs |
| `dcterms:` | `http://purl.org/dc/terms/` | titles, descriptions, identifiers |

Instance IRIs have the form `res:monument/<DANAM resource ID>`, `res:event/<monument ID>_<n>`,
`res:object/<object number>`, `res:assessment/<monument ID>`, `res:place/<name>`, `res:deity/<name>`. They do not
resolve on the web yet.

### Monument (`hg:ArchitecturalStructure`, also `crm:E22_Human-Made_Object`)

| Property | Value | Example |
|---|---|---|
| `rdf:type` | `hg:Temple`, `hg:Pati`, `hg:Sattal`, `hg:BuddhistMonument`, `hg:DhungeDhara`, `hg:Chaitya` …; grouping classes `hg:ReligiousStructure`, `hg:RestHouse`, `hg:WaterStructure` | `hg:Temple` |
| `rdfs:label`, `dcterms:title` | name, transliterated | "Illātvāḥ Gaṇeśa Mandira" |
| `schema:name` | name in Nepali | "इल्लात्वा: गणेश मन्दिर" |
| `schema:alternateName` | other name | "Illatva Ganesh Temple" |
| `hg:danamCode` | DANAM code | "SKH0310" |
| `dcterms:identifier` | DANAM resource ID | "a2a8efa0-…" |
| `owl:sameAs` | alternative IRI by DANAM code | `res:monument/SKH0310` |
| `geo:lat`, `geo:long` | WGS84 coordinates | 27.7301, 85.4623 |
| `geosparql:hasGeometry` | geometry node with `geosparql:asWKT` | `POINT(85.4623 27.7301)` |
| `hg:hasCurrentLocation`, `crm:P53_has_former_or_current_location` | place node (see below) | |
| `hg:hasArchitecturalStyle`, `crm:P2_has_type` | style as an `hg:ArchitecturalStyle#…` value and as a Getty AAT concept | `hg:ArchitecturalStyle#Pagoda`, `aat:300004829` |
| `hg:roofType`, `hg:brickType`, `hg:monumentShape` | text, as DANAM gives it | "Hip roof" |
| `hg:numStoreys`, `hg:numRoofs` | integer | 3, 2 |
| `hg:conditionStatus` | Good, Restored, Damaged, Ruined (can have two values) | "Restored" |
| `hg:existenceStatus` | `hg:ExistenceStatus#Extant`, `#PartiallyExtant`, `#Ruined` | |
| `hg:hasConditionAssessment`, `crm:P34i_was_assessed_by` | condition assessment node (see below) | |
| `hg:hasMainDeity` | deity node (`hg:Deity`, with `rdfs:label`) | `res:deity/ganesa` |
| `hg:hasReligiousTradition` | text, as DANAM gives it; can combine values | "Hindu", "Buddhist, Hindu", "Unspecified" |
| `hg:hasEvent`, `crm:P12i_was_present_at` | event nodes (see below) | |
| `hg:containsObject`, `crm:P46_is_composed_of` | object nodes (see below) | |
| `dcterms:references` | sources and inscriptions listed by DANAM | |
| `prov:wasDerivedFrom`, `schema:url` | the DANAM page | `https://danam.cats.uni-heidelberg.de/report/…` |
| `prov:generatedAtTime` | when the record was collected | 2026-03-16T09:15:42 |

### Event (`crm:E5_Event` and an `hg:` subclass)

Types: `hg:HistoricalEvent`, `hg:Production` (`crm:E12_Production`), `hg:DestructionEvent` (`crm:E6_Destruction`),
`hg:TransferOfCustody` (`crm:E10_Transfer_of_Custody`), `hg:RitualEvent`, `hg:Consecration`, `hg:Enshrinement`.

| Property | Value |
|---|---|
| `rdfs:label` | DANAM's title for the event |
| `dcterms:description`, `rdfs:comment` | DANAM's description |
| `hg:isEventOf`, `crm:P12_occurred_in_the_presence_of` | the monument |
| `hg:eventIndex` | position in the monument's list of events |
| `hg:extractionMethod` | how the event was obtained (`source_table`: from DANAM's event table) |
| `prov:wasAttributedTo`, `prov:wasGeneratedBy` | the agent and activity that built the graph |

Events have **no dates** in this release (see [Limitations](#6-limitations)).

### Object (`crm:E22_Human-Made_Object` and an `hg:` subclass)

Types: `hg:IconographicObject` (including `hg:Murti`, `hg:Paubha`), `hg:ArchitecturalElement`, `hg:HumanMadeObject`.
Linked to its monument by `hg:isObjectOf` / `crm:P46i_forms_part_of`; DANAM object number in `dcterms:identifier`;
label, description and comment as for events.

### Condition assessment (`hg:ConditionAssessment`, also `crm:E14_Condition_Assessment`)

| Property | Value |
|---|---|
| `crm:P34_concerned` | the monument |
| `crm:P35_has_identified` | condition state (`crm:E3_Condition_State`) |
| `hg:conditionType` / `hg:hasConditionType` | `hg:Good`, `hg:Restored`, `hg:Damaged`, `hg:Ruined` |
| `hg:identifiedThreats` | text, comma-separated: Erosion, Encroachment, Water damages, Wall cracks, Road widening, Plants … |
| `crm:P3_has_note` | assessment text |

### Place (`hg:Place`, also `schema:Place`)

| Property | Value |
|---|---|
| `rdfs:label` | "Ĩllā Ṭola, Shankharapur Municipality" |
| `hg:tola`, `hg:municipality`, `hg:district`, `hg:province` | text; province is a number (3 = Bagmati) |

Places are not linked into a hierarchy in this release; the levels are text values on each place.

## 5. Example queries

Monuments with coordinates and municipality:

```sparql
PREFIX hg:   <https://cair-nepal.org/heritagegraph/>
PREFIX geo:  <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?code ?name ?municipality ?lat ?long WHERE {
  ?m a hg:ArchitecturalStructure ; rdfs:label ?name ; geo:lat ?lat ; geo:long ?long .
  OPTIONAL { ?m hg:danamCode ?code }
  OPTIONAL { ?m hg:hasCurrentLocation/hg:municipality ?municipality }
} LIMIT 20
```

Damaged or ruined monuments and the threats recorded for them:

```sparql
PREFIX hg:   <https://cair-nepal.org/heritagegraph/>
PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?condition ?threats WHERE {
  ?m rdfs:label ?name ; hg:conditionStatus ?condition ; crm:P34i_was_assessed_by ?a .
  ?a hg:identifiedThreats ?threats .
  FILTER(STR(?condition) IN ("Damaged", "Ruined"))
} LIMIT 20
```

Temples by main deity:

```sparql
PREFIX hg:   <https://cair-nepal.org/heritagegraph/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?deity (COUNT(?m) AS ?temples) WHERE {
  ?m a hg:Temple ; hg:hasMainDeity/rdfs:label ?deity .
} GROUP BY ?deity ORDER BY DESC(?temples) LIMIT 15
```

More queries are in [`queries/`](https://github.com/CAIRNepal/HeritageGraphDataset/tree/main/queries) in the
HeritageGraphDataset repository. Those are written for the graph its builder now produces (the next release);
some use terms that v1.0.0 does not have (for example `hgn:` properties and `crm:P89_falls_within` place links).

## 6. Limitations

- **No event dates.** DANAM's event tables carry no dates, so no event has one. Dates appear in the event
  descriptions, in several calendar eras (CE, Nepal Saṃvat, Vikrama Saṃvat, Śaka); they are not yet extracted.
- **Event and object types come from keyword rules**, not manual review. Some are wrong (for example some
  reconstructions are typed `hg:DestructionEvent` or `hg:TransferOfCustody`). Labels and descriptions are DANAM's own.
- **Place names are not normalised.** The same municipality can appear under two spellings (e.g. "Lalitpur" and
  "Lalitpur Metropolitan City").
- **Multi-valued fields.** Where DANAM lists several values, the graph keeps them: 213 monuments have two condition
  values, and religious traditions and threats can be combined strings.
- **Source quirks are kept, not corrected.** Two records share the DANAM code `NWK0410`; some DANAM object numbers
  are reused.
- **Coverage follows DANAM**, mainly the Kathmandu Valley.
- **Instance IRIs do not resolve** on the web yet.

The [HeritageGraphDataset README](https://github.com/CAIRNepal/HeritageGraphDataset#8-limitations) tracks these and
the fixes planned for the next release.

## 7. Releases and versioning

Releases follow semantic versioning for knowledge graphs:

- **MAJOR** (`v2.0.0`): changes that can break queries (namespace or class/property changes, removed predicates).
- **MINOR** (`v1.1.0`): additions that keep existing queries working (new monuments or regions, new optional
  properties).
- **PATCH** (`v1.0.1`): corrections without new scope (typos, coordinate fixes).

Each release is published under its own prefix and is not changed afterwards. Release notes and policy:
[RELEASES.md](https://github.com/CAIRNepal/HeritageGraphDataset/blob/main/RELEASES.md).

| Release | Date | Notes |
|---|---|---|
| v1.0.0 | 2026-10-17 | first release |

<a id="licence"></a>
## 8. Licence

HeritageGraph is released under the
**[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)**
licence. You may share and adapt the data, including commercially, as long as you give credit and release what you
build from it under the same licence.

> Note: `metadata.json` in release v1.0.0 wrongly lists CC BY 4.0. The licence is CC BY-SA 4.0, as stated in the
> graph itself (`res:dataset dcterms:license`); `metadata.json` will be corrected in the next release.

The monument records, descriptions and images are the work of DANAM, Heidelberg University
(<https://danam.cats.uni-heidelberg.de>). Every monument links to the DANAM page it was derived from. Please credit
DANAM as the source of the content and CAIR-Nepal for the knowledge graph.

## 9. Citation

> CAIR-Nepal (2026). *HeritageGraph: Open Knowledge Graph Dataset for Cultural Heritage* (Version v1.0.0)
> [Data set]. https://registry.opendata.aws/cair-nepal-heritage-graph

Please also cite DANAM, and the HeritageGraph ontology as given in its
[CITATION.cff](https://github.com/CAIRNepal/heritagegraphontology/blob/main/CITATION.cff).

## 10. This repository

```text
├── README.md                                   dataset documentation (this file)
├── cair-nepal-heritage-graph/
│   ├── get-to-know-a-dataset.ipynb             tutorial notebook (AWS "Get to Know a Dataset" template)
│   └── requirements.txt
├── tools/test_s3_public.py                     checks anonymous read, listing, write-block and CORS on the bucket
├── ONBOARDING.md                               AWS Open Data onboarding checklist
└── DECISIONS.md                                decision log
```

Run the tutorial:

```bash
pip install -r cair-nepal-heritage-graph/requirements.txt
jupyter lab cair-nepal-heritage-graph/get-to-know-a-dataset.ipynb
```

Check the bucket's public access (no AWS credentials used):

```bash
pip install requests
python tools/test_s3_public.py v1.0.0/heritagegraph-nepal.ttl --origin https://heritagegraph.cair-nepal.org
```
