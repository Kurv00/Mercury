export type Program = Statement[];

export type Statement =
  | { kind: "FunDecl"; name: string; params: string[]; body: Expr }
  | { kind: "Let"; name: string; expr: Expr }
  | { kind: "ExprStmt"; expr: Expr };

export type Expr =
  | { kind: "Int"; value: number }
  | { kind: "Ident"; name: string }
  | { kind: "Binary"; op: string; left: Expr; right: Expr }
  | { kind: "Call"; callee: string; args: Expr[] };