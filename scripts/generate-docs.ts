import { generateDocs, generateIndex } from "@aibos/docs-registry";

async function main() {
  const docsDir = "docs";
  
  console.log("📄 Generating documents...");
  await generateDocs({ docsDir });
  
  console.log("📑 Generating INDEX...");
  await generateIndex({ docsDir });
  
  console.log("✅ Done!");
}

main().catch(console.error);

