import { Token, lex } from "./lexer.js";
import { Program, Statement, Expr } from "./ast.js";

export class Parser {
  tokens: Token[];
  pos = 0;
  constructor(source: string) { this.tokens = lex(source); }

  peek() { return this.tokens[this.pos]; }
  next() { return this.tokens[this.pos++]; }
  expectSym(s: string) {
    const t = this.next();
    if (t.type !== "sym" || t.value !== s) throw new Error(`Expected '${s}', got ${JSON.stringify(t)}`);
  }

  parseProgram(): Program {
    const out: Program = [];
    while (this.peek().type !== "eof") {
      out.push(this.parseStmt());
    }
    return out;
  }

  parseStmt(): Statement {
    const p = this.peek();
    if (p.type === "kw" && p.value === "fn") return this.parseFun();
    if (p.type === "kw" && p.value === "let") return this.parseLet();
    return { kind: "ExprStmt", expr: this.parseExpr() };
  }

  parseFun(): Statement {
    this.next(); // fn
    const nameTok = this.next();
    if (nameTok.type !== "ident") throw new Error("Expected function name");
    const name = nameTok.value;
    this.expectSym("(");
    const params: string[] = [];
    while (this.peek().type !== "sym" || this.peek().value !== ")") {
      const t = this.next();
      if (t.type !== "ident") throw new Error("Expected param name");
      params.push(t.value);
      if (this.peek().type === "sym" && this.peek().value === ",") this.next();
    }
    this.expectSym(")");
    this.expectSym("->");
    const body = this.parseExpr();
    return { kind: "FunDecl", name, params, body };
  }

  parseLet(): Statement {
    this.next(); // let
    const nameTok = this.next();
    if (nameTok.type !== "ident") throw new Error("Expected name after let");
    this.expectSym("=");
    const expr = this.parseExpr();
    return { kind: "Let", name: nameTok.value, expr };
  }

  parseExpr(): Expr {
    return this.parseAdd();
  }

  parseAdd(): Expr {
    let left = this.parseMul();
    while (this.peek().type === "sym" && (this.peek().value === "+" || this.peek().value === "-")) {
      const op = this.next().value;
      const right = this.parseMul();
      left = { kind: "Binary", op, left, right };
    }
    return left;
  }

  parseMul(): Expr {
    let left = this.parsePrimary();
    while (this.peek().type === "sym" && (this.peek().value === "*" || this.peek().value === "/")) {
      const op = this.next().value;
      const right = this.parsePrimary();
      left = { kind: "Binary", op, left, right };
    }
    return left;
  }

  parsePrimary(): Expr {
    const t = this.next();
    if (t.type === "num") return { kind: "Int", value: parseInt(t.value, 10) };
    if (t.type === "ident") {
      // could be call if next is '('
      if (this.peek().type === "sym" && this.peek().value === "(") {
        this.next(); // '('
        const args: Expr[] = [];
        if (!(this.peek().type === "sym" && this.peek().value === ")")) {
          while (true) {
            args.push(this.parseExpr());
            if (this.peek().type === "sym" && this.peek().value === ",") { this.next(); continue; }
            break;
          }
        }
        this.expectSym(")");
        return { kind: "Call", callee: t.value, args };
      }
      return { kind: "Ident", name: t.value };
    }
    if (t.type === "kw" && t.value === "print") {
      this.expectSym("(");
      const arg = this.parseExpr();
      this.expectSym(")");
      return { kind: "Call", callee: "print", args: [arg] };
    }
    if (t.type === "sym" && t.value === "(") {
      const e = this.parseExpr();
      this.expectSym(")");
      return e;
    }
    throw new Error("Unexpected token in primary: " + JSON.stringify(t));
  }
}