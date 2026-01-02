"""
Docs Domain MCP: Read Registry

Tool ID: docs.domain.registry.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class DocsRegistryInput(BaseModel):
    """Input schema for docs registry read."""
    doc_type: Optional[str] = Field(
        default=None,
        description="Filter by document type (PRD, SRS, ADR, etc.)",
    )
    include_versions: bool = Field(
        default=True,
        description="Include version information",
    )
    include_checksums: bool = Field(
        default=True,
        description="Include checksums for integrity verification",
    )


class DocumentPack(BaseModel):
    """Document pack schema."""
    document_id: str
    document_type: str
    title: str
    version: str
    status: str
    checksum: Optional[str] = None


class DocsRegistryOutput(BaseModel):
    """Output schema for docs registry read."""
    documents: List[DocumentPack] = Field(description="List of available document packs")
    total_count: int = Field(description="Total number of documents")
    tenant_id: str = Field(description="Tenant ID for these documents")


async def docs_registry_read_handler(
    input: DocsRegistryInput,
    context: ExecutionContext,
) -> DocsRegistryOutput:
    """
    Read document registry - available doc packs (PRD/SRS/ADR/Decision Records).
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: DocsRegistryInput
        context: Execution context
    
    Returns:
        DocsRegistryOutput with document registry
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        pass
    
    try:
        # Read document registry from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        
        documents = [
            DocumentPack(
                document_id="PRD-LYNX-001",
                document_type="PRD",
                title="Master PRD - Lynx AI",
                version="1.0.0",
                status="APPROVED",
                checksum="abc123..." if input.include_checksums else None,
            ),
            DocumentPack(
                document_id="PRD-LYNX-003",
                document_type="PRD",
                title="HYBRID BASIC Implementation Strategy",
                version="1.1.0",
                status="APPROVED",
                checksum="def456..." if input.include_checksums else None,
            ),
            DocumentPack(
                document_id="ADR-LYNX-001",
                document_type="ADR",
                title="Architecture Decision Record",
                version="1.0.0",
                status="ACTIVE",
                checksum="ghi789..." if input.include_checksums else None,
            ),
        ]
        
        # Apply filters
        if input.doc_type:
            documents = [d for d in documents if d.document_type == input.doc_type]
        
        # Remove checksums if not requested
        if not input.include_checksums:
            for doc in documents:
                doc.checksum = None
        
        return DocsRegistryOutput(
            documents=documents,
            total_count=len(documents),
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_docs_registry_read_tool(registry) -> None:
    """Register the docs.domain.registry.read tool."""
    tool = MCPTool(
        id="docs.domain.registry.read",
        name="Read Document Registry",
        description="Returns available document packs (PRD/SRS/ADR/Decision Records), versions, and checksums for governance visibility.",
        layer="domain",
        risk="low",
        domain="docs",
        input_schema=DocsRegistryInput,
        output_schema=DocsRegistryOutput,
        required_role=[],
        required_scope=[],
        handler=docs_registry_read_handler,
    )
    registry.register(tool)

