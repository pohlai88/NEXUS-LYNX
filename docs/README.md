# Documentation Governance

This directory is managed by `@aibos/docs-registry` — an NPM-pure governance SDK for managing documents as compiled artifacts.

## Human–Machine Governance Contract

- **Humans own meaning** — intent, rationale, philosophy
- **Machines own enforcement** — validation, consistency, memory
- **Drift is expected — but never silent**

## Document Structure

Each document lives in its own folder:

```
docs/<TYPE>/<DOC-ID>/
  doc.json   ← Machine-validated metadata (SSOT)
  doc.md     ← Human content + managed block
```

## Document Types

| Type | Level | Purpose                     | Authority Chain                              |
| ---- | ----- | --------------------------- | -------------------------------------------- |
| LAW  | 1     | Constitutional law documents | Original (constitutional foundation)         |
| RFC  | —     | Proposals (pre-decision)     | Derived from LAW (proposes new LAW or changes) |
| PRD  | 2     | Product intent & boundaries  | Derived from LAW/RFC                         |
| SRS  | 3     | System requirements         | Derived from PRD                             |
| ADR  | 4     | Architecture decisions      | Derived from SRS                             |
| TSD  | 5     | Technical specification     | Derived from ADR                              |
| SOP  | 6     | Operating procedures        | Derived from TSD                              |

## Quick Start

### 1. Create a Document

```bash
mkdir -p docs/PRD/PRD-001
```

### 2. Create `doc.json`

```json
{
  "document_id": "PRD-001",
  "document_type": "PRD",
  "classification": "STANDARD",
  "title": "My First Document",
  "status": "DRAFT",
  "authority": "DERIVED",
  "scope": "KERNEL",
  "derived_from": [],
  "version": "0.1.0",
  "owners": ["Your Name"],
  "checksum_sha256": null,
  "created_at": "2026-01-01",
  "updated_at": "2026-01-01"
}
```

### 3. Create `doc.md`

```markdown
# PRD-001 — My First Document

Your content here. The managed block will be automatically generated.
```

### 4. Generate Managed Blocks and INDEX

```bash
npm run docs:generate
```

This will:
- Generate managed header blocks in all `doc.md` files
- Calculate and update checksums in `doc.json` files
- Generate `INDEX.md` with all documents

### 5. Run Audit

```bash
npm run docs:audit
```

This validates:
- All `doc.json` files pass schema validation
- Content checksums match stored checksums
- INDEX.md is in sync with filesystem
- No orphan documents exist

## Available Commands

- `npm run docs:generate` — Generate managed blocks, checksums, and INDEX.md
- `npm run docs:audit` — Run full audit (schema, checksum, index, orphans)

## Governance Rules

### ✅ DO

- Treat `doc.json` as SSOT
- Generate, never hand-edit managed blocks
- Run audits before commit
- Use RFCs for structural change
- Derive from LAW — All documents must trace back to LAW documents
- Maintain lineage — Always specify `derived_from` in `doc.json`

### ❌ DON'T

- Edit generated sections
- Skip audits
- Create documents without constitutional lineage
- Change LAW documents directly — Use RFC to propose changes

## Constitutional Model

This SDK supports a **3-Tier Constitutional Model**:

1. **Tier 1: Constitutional Laws (LAW Documents)**
   - Foundational philosophy — Human truths that rarely change
   - Example: `LAW-001` — A foundational constitutional law

2. **Tier 2: Enforcement Doctrines**
   - Required mechanisms — Non-optional mechanics to enforce Tier 1
   - Example: Registry is the sole semantic authority

3. **Tier 3: Enforcement Surface**
   - Execution reality — Required capabilities and enforcement gates
   - Example: Semantic registry validation, override creation

**RFC's Role:** RFCs propose changes to the Constitution or new LAW documents. All RFCs must reference existing LAW documents.

## Audit Guarantees

| Check      | Guarantee                            |
| ---------- | ------------------------------------ |
| Schema     | All `doc.json` pass Zod validation   |
| Checksum   | Content hash matches stored checksum |
| INDEX → FS | Every INDEX entry exists             |
| FS → INDEX | No undocumented files                |
| Orphans    | No stray documents                   |
| Drift      | All violations are explicit          |

**Nothing passes silently.**

## More Information

See the [@aibos/docs-registry README](../../node_modules/@aibos/docs-registry/README.md) for complete documentation.

