# Verification Module

The **critical safety layer** that prevents genomic hallucinations.

## Philosophy

> "In biology, a hallucinated SNP is a misdiagnosis."

LLMs are powerful but can generate plausible-sounding nonsense. This module ensures that every genomic claim the agent makes is validated against biological ground truth.

## Validators

### `coordinate_validator.py`
Ensures genomic coordinates make sense:
- ✓ Chromosome exists in the reference genome
- ✓ Position is within chromosome bounds
- ✓ Start < End for intervals
- ✓ Coordinates match the specified build (hg19/hg38/etc)

Example:
```python
validator = CoordinateValidator(genome_build="hg38")
validator.validate("chr25:1000000-2000000")  # ❌ FAIL: chr25 doesn't exist
validator.validate("chr1:1000000-2000000")    # ✓ PASS
validator.validate("chr1:2000000-1000000")    # ❌ FAIL: start > end
```

### `variant_validator.py`
Validates variant calls and annotations:
- ✓ REF allele matches reference genome
- ✓ ALT allele is a valid DNA sequence
- ✓ Variant annotation is consistent (e.g., "missense" has a coding change)
- ✓ Clinical assertions match database records (ClinVar cross-check)

### `reference_checker.py`
Cross-references with authoritative databases:
- Ensembl gene coordinates
- RefSeq transcripts
- ClinVar variant interpretations
- HGVS nomenclature validation

### `constraints.py`
Encodes biological "sanity checks":
- GC content should be 0-1, not percentages
- PHRED scores are typically 0-60
- Coverage values can't be negative
- VCF quality scores can't be negative

## Integration

Every agent output passes through verification:

```
Agent: "Found a deletion at chr1:1000000-1000010"
  ↓
CoordinateValidator: ✓ chr1 exists, coordinates valid
  ↓
ReferenceChecker: ✓ Position falls within gene XYZ
  ↓
Output: "Deletion confirmed in gene XYZ (chr1:1000000-1000010)"
```

If validation fails:
```
Agent: "Found variant at chr1:999999999999"
  ↓
CoordinateValidator: ❌ Position exceeds chr1 length (248,956,422)
  ↓
Agent: [Self-corrects] "Re-checking coordinates..."
```

## Priority Checks

1. **P0 - Critical**: Wrong coordinates = wrong patient implications
2. **P1 - High**: Mismatched REF allele = technical artifact
3. **P2 - Medium**: Missing annotation = incomplete report
4. **P3 - Low**: Formatting inconsistencies = aesthetics
