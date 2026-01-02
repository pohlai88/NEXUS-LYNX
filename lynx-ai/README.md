# Lynx AI - Implementation

**Kernel-Governed Artificial Intelligence for AI-BOS NexusCanon**

This directory contains the implementation of Lynx AI following PRD-LYNX-003 (HYBRID BASIC strategy).

---

## Project Structure

```
lynx-ai/
├── core/                    # Core runtime components
│   ├── runtime/            # mcp-agent integration
│   ├── session/            # Session management
│   ├── registry/           # MCP tool registry
│   ├── permissions/        # Permission checking
│   └── audit/              # Audit logging
├── mcp/                    # MCP tool implementations
│   ├── domain/            # Domain MCPs (read-only)
│   ├── cluster/           # Cluster MCPs (drafts)
│   └── cell/              # Cell MCPs (execution)
├── integration/            # External integrations
│   ├── kernel/            # Kernel SSOT integration
│   └── ui/                # UI integration
├── config/                 # Configuration files
└── tests/                  # Test suite
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- uv (recommended) or pip
- OpenAI API key (or Anthropic)
- Kernel API access
- Supabase access (for audit logs)

### Installation

```bash
# Install uv (if not installed)
# pipx install uv

# Navigate to lynx-ai directory
cd lynx-ai

# Initialize uv environment
uv init

# Install dependencies
uv add "mcp-agent[openai]"
uv add pydantic
uv add httpx
uv add supabase
```

### Configuration

1. Copy `config/config.yaml.example` to `config/config.yaml`
2. Copy `config/secrets.yaml.example` to `config/secrets.yaml`
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `KERNEL_API_URL`
   - `KERNEL_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

### Run

```bash
uv run python -m lynx.main
```

### Status Check

Check system health and connectivity:

```bash
python -m lynx.cli.status
```

### Test

```bash
# Run all tests
uv run pytest

# Run integration tests only
uv run pytest tests/integration/

# Run with verbose output
uv run pytest -v

# Run RLS verification tests (requires Supabase credentials)
export SUPABASE_URL=https://<project-ref>.supabase.co
export SUPABASE_KEY=your-service-role-key
uv run pytest tests/integration/test_rls_verification.py -v
```

**Windows (PowerShell):**
```powershell
.\run_tests.ps1
```

**Linux/Mac:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Staging Deployment

See `docs/DEPLOYMENT/STAGING-CHECKLIST.md` for complete staging deployment instructions.

**Quick start:**
1. Apply Supabase schema: `docs/DEPLOYMENT/supabase-migration.sql`
2. Set environment variables: `SUPABASE_URL`, `SUPABASE_KEY`
3. Run smoke test: `python scripts/staging-smoke-test.py`
4. Deploy to Railway (or your preferred platform)

### Status Command

```bash
# Check system status
uv run python -m lynx.cli.status
```

This shows:
- Service status and connectivity
- Storage backend type (supabase/memory)
- Draft/execution counts (last 24h)
- Pending settlement count
- Recent runs summary

---

## Development Status

**Current Phase:** Phase 1 - Foundation + Governance (Week 1-2)

**Progress:**
- [x] Project structure created
- [x] mcp-agent foundation
- [x] Session management
- [x] MCP tool registry
- [x] Kernel SSOT integration
- [x] Audit logging
- [x] Tenant isolation
- [x] Testing infrastructure
- [x] Integration tests (PRD Law gates)

---

## References

- **PRD-LYNX-001** - Master PRD (SSOT)
- **PRD-LYNX-003** - HYBRID BASIC Implementation Strategy
- **TSD-LYNX-001** - Technical Specification Document
- **IMPLEMENTATION-LYNX-001** - Implementation Plan
- **ANALYSIS-LYNX-002** - awesome-llm-apps Analysis

---

**Status:** In Development

