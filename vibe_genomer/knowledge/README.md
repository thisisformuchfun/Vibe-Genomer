# Knowledge Module

Genomic reference databases and knowledge bases that ground the agent's reasoning in biological reality.

## Database Integrations

### `clinvar/`
**ClinVar**: Clinical variant interpretations
- Pathogenic/Benign classifications
- Clinical significance
- Reviewed by expert panels
- Phenotype associations

```python
from vibe_genomer.knowledge.clinvar import ClinVarDB

clinvar = ClinVarDB()
interpretation = clinvar.lookup_variant("chr17:43044295", "G", "A")
# Returns: {
#   "clinical_significance": "Pathogenic",
#   "review_status": "reviewed_by_expert_panel",
#   "conditions": ["Breast-ovarian cancer, familial"],
#   "clinvar_id": "VCV000123456"
# }
```

### `ensembl/`
**Ensembl**: Gene annotations and transcripts
- Gene coordinates
- Transcript models
- Protein sequences
- Cross-species homology

```python
from vibe_genomer.knowledge.ensembl import EnsemblDB

ensembl = EnsemblDB(species="human", build="GRCh38")
gene_info = ensembl.get_gene_by_name("BRCA1")
# Returns: {
#   "gene_id": "ENSG00000012048",
#   "chrom": "17",
#   "start": 43044295,
#   "end": 43125483,
#   "strand": "-",
#   "biotype": "protein_coding"
# }
```

### `ucsc/`
**UCSC Genome Browser**: Reference genomes and tracks
- Reference genome sequences (hg19, hg38, etc.)
- Conservation scores
- Repeat regions
- Regulatory elements

## Knowledge Base Structure

```
knowledge/
├── databases/           # Local cached databases
│   ├── clinvar.db      # SQLite cache
│   ├── ensembl.db
│   └── hgvs.db
├── reference_genomes/   # FASTA reference files
│   ├── hg19.fa
│   ├── hg38.fa
│   └── chm13.fa
└── embeddings/          # Vector databases for semantic search
    ├── genes.faiss
    ├── variants.faiss
    └── phenotypes.faiss
```

## Semantic Search

Vector embeddings enable natural language queries:

```python
kb = KnowledgeBase()
results = kb.semantic_search("genes involved in DNA repair")
# Returns: ["BRCA1", "BRCA2", "TP53", "ATM", ...]

results = kb.semantic_search("pathogenic variants causing breast cancer")
# Returns: [
#   {"gene": "BRCA1", "variant": "c.68_69delAG", "significance": "Pathogenic"},
#   {"gene": "BRCA2", "variant": "c.5946delT", "significance": "Pathogenic"},
#   ...
# ]
```

## Integration with Agent

```
User: "Is this variant pathogenic?"
  ↓
Agent → Knowledge: "Query ClinVar for chr17:43044295 G>A"
  ↓
Knowledge: Returns clinical significance + evidence
  ↓
Agent → Verification: Cross-check coordinates are valid
  ↓
Response: "Yes, pathogenic. ClinVar classifies this BRCA1 variant as pathogenic
           for hereditary breast/ovarian cancer (expert reviewed)."
```

## Update Mechanisms

Databases are updated regularly:
- ClinVar: Weekly automated downloads
- Ensembl: Per-release (every 3-4 months)
- Reference genomes: As new builds are released

```bash
vibe update-knowledge --database clinvar
vibe update-knowledge --database ensembl --release 110
vibe update-knowledge --reference-genome hg38
```

## Privacy Considerations

- All queries are local (no patient data sent to external APIs)
- Cache databases locally to minimize external requests
- For restricted databases (ClinGen, OMIM), use API keys with audit logging
