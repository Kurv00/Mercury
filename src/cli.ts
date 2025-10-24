import fs from "fs";
import path from "path";
import { Parser } from "./parser.js";
import { gen } from "./codegen.js";
import { typecheckProgram } from "./types.js";

function usage() {
  console.log("Usage: npx ts-node src/cli.ts <file.mr>");
  process.exit(1);
}

const file = process.argv[2];
if (!file) usage();

const source = fs.readFileSync(file, "utf-8");
const p = new Parser(source);
const prog = p.parseProgram();

try {
  typecheckProgram(prog);
} catch (e) {
  console.error("Type error:", e.message || e);
  process.exit(2);
}

const js = gen(prog);
const outFile = path.join(process.cwd(), "out.js");
fs.writeFileSync(outFile, js, "utf-8");
console.log("Compiled -> out.js");
console.log("Running...");
const { spawnSync } = await import("child_process");
const res = spawnSync("node", [outFile], { stdio: "inherit" });
process.exit(res.status ?? 0);