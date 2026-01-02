import { auditAll } from "@aibos/docs-registry";

async function main() {
  const docsDir = "docs";
  
  console.log("🔍 Running audit...");
  const result = await auditAll({ docsDir });
  
  if (!result.passed) {
    console.error("❌ Audit failed:");
    result.violations.forEach(v => {
      console.error(`  - ${v.docId}: ${v.message}`);
    });
    process.exit(1);
  }
  
  console.log("✅ All checks passed");
}

main().catch(console.error);

