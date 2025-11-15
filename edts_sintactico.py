from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from edts_lexer import Token

# AST
@dataclass
class AST:
    pass

@dataclass
class Num(AST):
    value: float
    line: int
    col: int
    tipo: str = "num"
    val: float = field(init=False)

    def __post_init__(self):
        self.val = self.value

@dataclass
class Var(AST):
    name: str
    line: int
    col: int
    tipo: str = "num"
    val: Optional[float] = None

@dataclass
class BinOp(AST):
    op: str
    left: AST
    right: AST
    line: int
    col: int
    tipo: str = "num"
    val: Optional[float] = None

# Tabla de símbolos
@dataclass
class Sym:
    name: str
    tipo: str = "num"
    valor: Optional[float] = None
    ocurrencias: List[Tuple[int, int]] = field(default_factory=list)

class SymbolTable:
    def __init__(self):
        self.tab: Dict[str, Sym] = {}

    def touch(self, name: str, line: int, col: int):
        if name not in self.tab:
            self.tab[name] = Sym(name)
        self.tab[name].ocurrencias.append((line, col))

    def set_value(self, name: str, value: float):
        if name not in self.tab:
            self.tab[name] = Sym(name)
        self.tab[name].valor = value

    def __iter__(self):
        return iter(self.tab.values())

# Parser LL(1) recursivo descendente
# E  → T E'
# E' → + T E' | - T E' | ε
# T  → F T'
# T' → * F T' | / F T' | ε
# F  → NUMBER | ID | '(' E ')'
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.symtab = SymbolTable()

    def peek(self) -> Token:
        return self.tokens[self.i]

    def eat(self, ttype: str) -> Token:
        tok = self.peek()
        if tok.type != ttype:
            raise SyntaxError(
                f"Se esperaba {ttype} y llegó {tok.type} en línea {tok.line}, col {tok.col}"
            )
        self.i += 1
        return tok

    def parse_E(self) -> AST:
        node = self.parse_T()
        return self.parse_Ep(node)

    def parse_Ep(self, inherited: AST) -> AST:
        tok = self.peek()
        if tok.type in ("PLUS", "MINUS"):
            op = tok.value
            self.eat(tok.type)
            t = self.parse_T()
            merged = BinOp(op=op, left=inherited, right=t, line=tok.line, col=tok.col)
            return self.parse_Ep(merged)
        return inherited

    def parse_T(self) -> AST:
        node = self.parse_F()
        return self.parse_Tp(node)

    def parse_Tp(self, inherited: AST) -> AST:
        tok = self.peek()
        if tok.type in ("TIMES", "DIV"):
            op = tok.value
            self.eat(tok.type)
            f = self.parse_F()
            merged = BinOp(op=op, left=inherited, right=f, line=tok.line, col=tok.col)
            return self.parse_Tp(merged)
        return inherited

    def parse_F(self) -> AST:
        tok = self.peek()
        if tok.type == "NUMBER":
            t = self.eat("NUMBER")
            return Num(float(t.value), t.line, t.col)
        if tok.type == "ID":
            t = self.eat("ID")
            self.symtab.touch(t.value, t.line, t.col)
            return Var(t.value, t.line, t.col)
        if tok.type == "LPAREN":
            self.eat("LPAREN")
            e = self.parse_E()
            self.eat("RPAREN")
            return e
        raise SyntaxError(
            f"Token inesperado {tok.type} en línea {tok.line}, col {tok.col}"
        )

    def parse(self) -> AST:
        tree = self.parse_E()
        if self.peek().type != "EOF":
            tok = self.peek()
            raise SyntaxError(
                f"Sobra entrada desde {tok.type} en línea {tok.line}, col {tok.col}"
            )
        return tree

# AST a texto
def _format_ast_rec(n: AST, indent: int, out: List[str]):
    pref = "  " * indent
    if isinstance(n, Num):
        out.append(f"{pref}Num({n.value})")
    elif isinstance(n, Var):
        out.append(f"{pref}Id({n.name})")
    elif isinstance(n, BinOp):
        out.append(f"{pref}BinOp({n.op})")
        _format_ast_rec(n.left, indent + 1, out)
        _format_ast_rec(n.right, indent + 1, out)
    else:
        out.append(f"{pref}<?>")

def format_ast(root: AST) -> str:
    lines: List[str] = []
    _format_ast_rec(root, 0, lines)
    return "\n".join(lines)

# Tabla de símbolos a texto
def symtab_to_str(symtab: SymbolTable) -> str:
    lines: List[str] = []
    hay = False
    for sym in symtab:
        hay = True
        lines.append(f"{sym.name:10s} tipo={sym.tipo} valor={sym.valor}")
    if not hay:
        lines.append("(sin identificadores)")
    return "\n".join(lines)

# Generación de TAC
class TACGenerator:
    def __init__(self):
        self.instructions: List[str] = []
        self.temp_counter = 1

    def new_temp(self) -> str:
        t = f"t{self.temp_counter}"
        self.temp_counter += 1
        return t

    def gen(self, node: AST) -> str:
        if isinstance(node, Num):
            t = self.new_temp()
            self.instructions.append(f"{t} = {node.value}")
            return t
        if isinstance(node, Var):
            return node.name
        if isinstance(node, BinOp):
            left = self.gen(node.left)
            right = self.gen(node.right)
            t = self.new_temp()
            self.instructions.append(f"{t} = {left} {node.op} {right}")
            return t
        raise RuntimeError("Nodo AST desconocido en TAC")

def generate_tac(root: AST) -> str:
    gen = TACGenerator()
    result_temp = gen.gen(root)
    gen.instructions.append(f"resultado en: {result_temp}")
    return "\n".join(gen.instructions)
