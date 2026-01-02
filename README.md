# NexusCanon-Lynx

**AI Assistant as a Governed Product Feature inside AI-BOS NexusCanon**

This repository contains the **Product Requirements Document (PRD)**, documentation, and **implementation** for **Lynx AI** — a tenant-aware, permission-governed AI assistant embedded inside AI-BOS NexusCanon.

---

## 🚀 Quick Start

**Lynx AI implementation is in the `lynx-ai/` directory.**

```bash
# Navigate to implementation directory
cd lynx-ai

# Follow setup instructions
# See lynx-ai/SETUP.md for detailed setup guide
```

**Status:** Phase 1 - Foundation + Governance (In Progress)

---

## What Is This Repository?

This repository uses `@aibos/docs-registry` — an NPM-pure governance SDK for managing documents as **compiled artifacts**, not free-text files.

### Key Principles

- **Humans own meaning** — intent, rationale, philosophy
- **Machines own enforcement** — validation, consistency, memory
- **Drift is expected — but never silent**

Documents are not "written" — they are **compiled** and machine-validated.

---

## Documentation System Setup

### What Was Configured

1. **@aibos/docs-registry** — Document governance SDK installed
2. **Document structure** — `docs/` directory with governance system
3. **Generation scripts** — Automated managed block and INDEX generation
4. **Audit system** — Full validation pipeline for document integrity

### Project Structure

```
NexusCanon-Lynx/
├── docs/                    # Governed documentation directory
│   ├── README.md           # Documentation guide
│   ├── INDEX.md            # Auto-generated document index
│   └── <TYPE>/             # Document type folders (PRD, ADR, RFC, etc.)
│       └── <DOC-ID>/
│           ├── doc.json    # Machine-validated metadata (SSOT)
│           └── doc.md      # Human content + managed block
├── scripts/
│   ├── generate-docs.ts    # Generate managed blocks and INDEX
│   └── audit-docs.ts       # Run full document audit
├── draft                   # Original draft PRD (to be migrated)
├── package.json            # NPM configuration with docs scripts
├── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```

---

## Quick Start

### Prerequisites

- Node.js 18+ installed
- NPM installed

### Installation

```bash
npm install
```

This installs:
- `@aibos/docs-registry` — Document governance SDK
- `handlebars` — Template engine (peer dependency)
- `glob` — File pattern matching (runtime dependency)
- `tsx`, `typescript` — Development tools for scripts

### Creating Your First Document

1. **Create document directory:**
   ```bash
   mkdir -p docs/PRD/PRD-001
   ```

2. **Create `doc.json`** (metadata — SSOT):
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

3. **Create `doc.md`** (content):
   ```markdown
   # PRD-001 — My First Document
   
   Your content here. The managed block will be automatically generated.
   ```

4. **Generate managed blocks and INDEX:**
   ```bash
   npm run docs:generate
   ```

5. **Run audit:**
   ```bash
   npm run docs:audit
   ```

---

## Available Commands

### `npm run docs:generate`

Generates:
- Managed header blocks in all `doc.md` files
- SHA-256 checksums for content integrity
- `docs/INDEX.md` with all documents

**When to run:**
- After creating new documents
- After modifying document content
- Before committing changes

### `npm run docs:audit`

Validates:
- All `doc.json` files pass Zod schema validation
- Content checksums match stored checksums
- `INDEX.md` is synchronized with filesystem
- No orphan documents exist

**When to run:**
- Before committing changes
- In CI/CD pipelines
- When verifying document integrity

---

## Document Types & Hierarchy

Documents follow a **constitutional hierarchy**:

| Type | Level | Purpose                     | Authority Chain                              |
| ---- | ----- | --------------------------- | -------------------------------------------- |
| LAW  | 1     | Constitutional law documents | Original (constitutional foundation)         |
| RFC  | —     | Proposals (pre-decision)     | Derived from LAW (proposes new LAW or changes) |
| PRD  | 2     | Product intent & boundaries  | Derived from LAW/RFC                         |
| SRS  | 3     | System requirements         | Derived from PRD                             |
| ADR  | 4     | Architecture decisions      | Derived from SRS                             |
| TSD  | 5     | Technical specification     | Derived from ADR                              |
| SOP  | 6     | Operating procedures        | Derived from TSD                              |

### Constitutional Model

This system supports a **3-Tier Constitutional Model**:

1. **Tier 1: Constitutional Laws (LAW Documents)**
   - Foundational philosophy that rarely changes
   - Example: `LAW-001` — A foundational constitutional law

2. **Tier 2: Enforcement Doctrines**
   - Required mechanisms to enforce Tier 1
   - Example: Registry is the sole semantic authority

3. **Tier 3: Enforcement Surface**
   - Execution reality and enforcement gates
   - Example: Semantic registry validation

**RFC's Role:** RFCs propose changes to the Constitution or new LAW documents. All RFCs must reference existing LAW documents.

---

## Governance Rules

### ✅ DO

- Treat `doc.json` as **Single Source of Truth (SSOT)**
- Generate managed blocks — never hand-edit them
- Run audits before committing changes
- Use RFCs for structural changes
- Derive from LAW — All documents must trace back to LAW documents
- Maintain lineage — Always specify `derived_from` in `doc.json`

### ❌ DON'T

- Edit generated sections (they will be overwritten)
- Skip audits
- Create documents without constitutional lineage
- Change LAW documents directly — Use RFC to propose changes
- Modify files in `node_modules/` (they are managed by NPM)

---

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

---

## How It Works

### Document Lifecycle

1. **Create** — Human creates `doc.json` (metadata) and `doc.md` (content)
2. **Generate** — Machine generates managed header block and calculates checksum
3. **Validate** — Machine validates schema, checksum, and filesystem sync
4. **Audit** — Machine ensures no drift or violations

### Managed Blocks

The SDK automatically injects a **managed header block** into `doc.md`:

```markdown
<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | PRD-001 |
| **Status** | DRAFT |
| **Version** | 0.1.0 |
<!-- END: AIBOS_MANAGED -->
```

**Rules:**
- Content **inside** the block is machine-owned (auto-generated)
- Content **outside** the block is human-owned
- Manual edits inside the block are **overwritten** on next generation

---

## Configuration Files

### `package.json`

Contains:
- Dependencies: `@aibos/docs-registry`, `handlebars`, `glob`
- Dev dependencies: `tsx`, `typescript`, `@types/node`
- Scripts: `docs:generate`, `docs:audit`

### `tsconfig.json`

TypeScript configuration for ESM modules (required for `@aibos/docs-registry`).

### `scripts/generate-docs.ts`

Script that:
1. Discovers all documents in `docs/`
2. Generates managed header blocks
3. Calculates and updates checksums
4. Generates `INDEX.md`

### `scripts/audit-docs.ts`

Script that:
1. Validates all `doc.json` schemas
2. Verifies checksums match content
3. Ensures INDEX is synchronized
4. Detects orphan documents

---

## Troubleshooting

### "Template not found"

The template is included in the package. If you see this error:
1. Ensure `handlebars` is installed: `npm install handlebars`
2. Verify the package is properly installed: `npm install`

### "Module not found" errors

Ensure you're using ESM imports:
```ts
// ✅ Correct
import { generateDocs } from "@aibos/docs-registry";

// ❌ Wrong
const { generateDocs } = require("@aibos/docs-registry");
```

### "Checksum mismatch"

Regenerate documents:
```bash
npm run docs:generate
```

### "INDEX out of sync"

Regenerate INDEX:
```bash
npm run docs:generate
```

---

## Migration from Draft

The `draft` file contains the original PRD. To migrate it to the governed system:

1. Create document structure:
   ```bash
   mkdir -p docs/PRD/PRD-LYNX-001
   ```

2. Create `doc.json` with appropriate metadata

3. Copy content from `draft` to `doc.md`

4. Run generation:
   ```bash
   npm run docs:generate
   ```

5. Verify with audit:
   ```bash
   npm run docs:audit
   ```

---

## More Information

- **Documentation Guide:** See `docs/README.md` for detailed usage
- **Package Documentation:** See `node_modules/@aibos/docs-registry/README.md` for complete API reference
- **Lynx PRD:** See `draft` file for the original Product Requirements Document

---

## License

ISC

---

**Last Updated:** 2026-01-01  
**Documentation System:** @aibos/docs-registry v0.1.1

