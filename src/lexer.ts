export type Token =
  | { type: "num"; value: string }
  | { type: "ident"; value: string }
  | { type: "kw"; value: string }
  | { type: "sym"; value: string }
  | { type: "eof" };

const isDigit = (c: string) => /[0-9]/.test(c);
const isIdent = (c: string) => /[a-zA-Z_]/.test(c);

export function lex(input: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < input.length) {
    const c = input[i];
    if (/\s/.test(c)) { i++; continue; }
    if (isDigit(c)) {
      let num = c; i++;
      while (i < input.length && isDigit(input[i])) { num += input[i++]; }
      tokens.push({ type: "num", value: num }); continue;
    }
    if (isIdent(c)) {
      let id = c; i++;
      while (i < input.length && /[a-zA-Z0-9_]/.test(input[i])) id += input[i++];
      if (id === "let" || id === "fn" || id === "print") tokens.push({ type: "kw", value: id });
      else tokens.push({ type: "ident", value: id });
      continue;
    }
    // symbols
    const two = input.slice(i, i+2);
    if (two === "->") { tokens.push({ type: "sym", value: "->" }); i+=2; continue; }
    if ("+-*/=(),{}".includes(c)) { tokens.push({ type: "sym", value: c }); i++; continue; }
    throw new Error("Unknown char: " + c);
  }
  tokens.push({ type: "eof" });
  return tokens;
}