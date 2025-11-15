import os
from edts_lexer import lex
from edts_sintactico import Parser, format_ast, symtab_to_str, generate_tac

# Programa principal: lee expr.txt y genera AST, tabla de símbolos y TAC
def main():
    expr_path = "expr.txt"
    if not os.path.exists(expr_path):
        raise FileNotFoundError(
            f"No se encontró {expr_path}. Crea el archivo y escribe una expresión en la primera línea."
        )

    with open(expr_path, "r", encoding="utf-8") as f:
        expr = f.readline().strip()

    if not expr:
        raise ValueError("expr.txt está vacío o la primera línea está vacía.")

    tokens = list(lex(expr))
    parser = Parser(tokens)
    tree = parser.parse()

    ast_text = format_ast(tree)
    sym_text = symtab_to_str(parser.symtab)
    tac_text = generate_tac(tree)

    with open("AST.txt", "w", encoding="utf-8") as f_ast:
        f_ast.write(ast_text + "\n")

    with open("TABLA_SIMBOLOS.txt", "w", encoding="utf-8") as f_sym:
        f_sym.write(sym_text + "\n")

    with open("TAC.txt", "w", encoding="utf-8") as f_tac:
        f_tac.write(tac_text + "\n")

    print("Expresión:", expr)
    print("Archivos generados:")
    print(" - AST.txt")
    print(" - TABLA_SIMBOLOS.txt")
    print(" - TAC.txt")

if __name__ == "__main__":
    main()
