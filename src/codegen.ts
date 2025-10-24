import { Program, Statement, Expr } from "./ast.js";

export function gen(program: Program): string {
  const parts: string[] = [];
  // header with print
  parts.push(`function print(x){ console.log(x); return 0; }`);

  for (const s of program) {
    if (s.kind === "FunDecl") {
      const params = s.params.join(", ");
      parts.push(`function ${s.name}(${params}){ return ${genExpr(s.body)}; }`);
    } else if (s.kind === "Let") {
      parts.push(`const ${s.name} = ${genExpr(s.expr)};`);
    } else if (s.kind === "ExprStmt") {
      parts.push(`${genExpr(s.expr)};`);
    }
  }
  return parts.join("\n");
}

function genExpr(e: Expr): string {
  switch (e.kind) {
    case "Int": return e.value.toString();
    case "Ident": return e.name;
    case "Binary": return `(${genExpr(e.left)} ${e.op} ${genExpr(e.right)})`;
    case "Call":
      const args = e.args.map(a => genExpr(a)).join(", ");
      return `${e.callee}(${args})`;
  }
}