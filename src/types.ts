import { Program, Statement, Expr } from "./ast.js";

type Env = Record<string, "int" | "fn">;

export function typecheckProgram(prog: Program) {
  const env: Env = {};
  // builtin
  env["print"] = "fn";

  for (const s of prog) {
    if (s.kind === "FunDecl") {
      env[s.name] = "fn";
    } else if (s.kind === "Let") {
      const t = typeOfExpr(s.expr, env);
      if (t !== "int") throw new Error(`Only int lets supported. ${s.name} is ${t}`);
      env[s.name] = "int";
    } else if (s.kind === "ExprStmt") {
      typeOfExpr(s.expr, env);
    }
  }
}

function typeOfExpr(e: Expr, env: Env): "int" | "fn" {
  if (e.kind === "Int") return "int";
  if (e.kind === "Ident") {
    if (!env[e.name]) throw new Error(`Unknown identifier ${e.name}`);
    return env[e.name];
  }
  if (e.kind === "Binary") {
    const l = typeOfExpr(e.left, env);
    const r = typeOfExpr(e.right, env);
    if (l !== "int" || r !== "int") throw new Error("Binary ops require ints");
    return "int";
  }
  if (e.kind === "Call") {
    if (!env[e.callee]) throw new Error(`Unknown callee ${e.callee}`);
    // only support int-returning functions for now (including builtin print returns int 0)
    for (const a of e.args) {
      const ta = typeOfExpr(a, env);
      if (ta !== "int") throw new Error("Function args must be int");
    }
    return "int";
  }
  throw new Error("Unhandled expr in typechecker");
}