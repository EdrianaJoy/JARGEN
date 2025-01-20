def flatten_token_lines(token_lines):
    flat = []
    for line in token_lines:
        flat.extend(line)
    return flat

class ParseTreeNode:
    def __init__(self, node_type, value=None):
        self.node_type = node_type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"<{self.node_type} value={self.value} children={len(self.children)}>"

class SyntaxAnalyzer:
    def __init__(self, token_lines):
        self.tokens = flatten_token_lines(token_lines)
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.error_count = 0

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match(self, expected_type=None, expected_value=None):
        if not self.current_token:
            self.report_error(f"Unexpected end of tokens. Expected {expected_type or expected_value}")
            return None

        ttype, tval = self.current_token
        type_ok = (expected_type is None or ttype == expected_type)
        value_ok = (expected_value is None or tval == expected_value)

        if type_ok and value_ok:
            matched = self.current_token
            self.advance()
            return matched
        else:
            self.report_error(f"Expected {expected_type or ''} {expected_value or ''}, got ({ttype}, {tval})")
            return None

    def report_error(self, message):
        print(f"[Syntax Error @ token index {self.pos}]: {message}")
        self.error_count += 1

    def parse_program(self):
        root = ParseTreeNode("PROGRAM")
        stmt_list = self.parse_statement_list()
        if stmt_list:
            root.add_child(stmt_list)
        else:
            self.report_error("Empty program or invalid statements.")
        return root

    def parse_statement_list(self):
        node = ParseTreeNode("STATEMENT_LIST")
        while self.can_start_statement():
            stmt = self.parse_statement()
            if stmt:
                node.add_child(stmt)
            else:
                break
        return node

    def can_start_statement(self):
        if not self.current_token:
            return False
        ttype, tval = self.current_token

        # Adjust these to match the keywords or token values that can start a statement
        if tval in {"flex", "nocap", "bet", "sus", "forreal", "mood",
                    "talk", "spill", "post", "else"}:
            return True
        if ttype == "Identifier":
            return True
        if tval == "{":
            return True

        return False

    def parse_statement(self):
        if not self.current_token:
            return None

        ttype, tval = self.current_token

        if tval in {"flex", "nocap", "bet"}:
            return self.parse_declaration()
        if tval == "sus":
            return self.parse_if_stmt()
        if tval == "forreal":
            return self.parse_for_stmt()
        if tval == "talk":
            return self.parse_while_stmt()
        if tval == "spill":
            return self.parse_print_stmt()
        if tval == "post":
            return self.parse_input_stmt()
        if tval == "mood":
            return self.parse_switch_stmt()

        if tval == "{":
            return self.parse_block()

        if ttype == "Identifier":
            return self.parse_assignment()

        self.report_error(f"Unrecognized statement start: ({ttype}, {tval})")
        return None

    # --- Add more parse_XXX methods below as needed --- #
    # Example:
    def parse_declaration(self):
        node = ParseTreeNode("DECLARATION")
        decl_kw = self.match(expected_type="Keyword")  # or none, if your tokens are slightly different
        if not decl_kw:
            return None
        node.value = decl_kw[1]  # e.g. "flex", "nocap", or "bet"

        # Expect Identifier
        ident = self.match(expected_type="Identifier")
        if not ident:
            return None
        node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))

        # Optional '='
        if self.current_token and self.current_token[1] == "=":
            eq = self.match(expected_value="=")
            if not eq:
                return None
            expr = self.parse_expr()
            if expr:
                node.add_child(expr)
            else:
                return None

        # Expect semicolon
        semi = self.match(expected_type="Semi-colon", expected_value=";")
        if not semi:
            return None

        return node

    def parse_if_stmt(self):
        node = ParseTreeNode("IF_STMT")
        sus_kw = self.match(expected_value="sus")
        if not sus_kw:
            return None
        lp = self.match(expected_value="(")
        if not lp:
            return None
        expr_node = self.parse_expr()
        if not expr_node:
            return None
        node.add_child(expr_node)
        rp = self.match(expected_value=")")
        if not rp:
            return None

        lb = self.match(expected_value="{")
        if not lb:
            return None
        stmt_list = self.parse_statement_list()
        node.add_child(stmt_list)
        rb = self.match(expected_value="}")
        if not rb:
            return None

        # Optional else
        if self.current_token and self.current_token[1] == "else":
            else_tok = self.match(expected_value="else")
            if else_tok:
                lb2 = self.match(expected_value="{")
                if not lb2:
                    return None
                else_list = self.parse_statement_list()
                else_node = ParseTreeNode("ELSE_BLOCK")
                else_node.add_child(else_list)
                node.add_child(else_node)

                rb2 = self.match(expected_value="}")
                if not rb2:
                    return None

        return node

    def parse_for_stmt(self):
        node = ParseTreeNode("FOR_STMT")
        for_kw = self.match(expected_value="forreal")
        if not for_kw:
            return None
        lp = self.match(expected_value="(")
        if not lp:
            return None

        # Example for 3 expressions and 2 semicolons
        expr1 = self.parse_expr()
        if not expr1:
            return None
        node.add_child(expr1)

        s1 = self.match(expected_value=";")
        if not s1:
            return None

        expr2 = self.parse_expr()
        if not expr2:
            return None
        node.add_child(expr2)

        s2 = self.match(expected_value=";")
        if not s2:
            return None

        expr3 = self.parse_expr()
        if not expr3:
            return None
        node.add_child(expr3)

        rp = self.match(expected_value=")")
        if not rp:
            return None

        lb = self.match(expected_value="{")
        if not lb:
            return None
        stmts = self.parse_statement_list()
        node.add_child(stmts)
        rb = self.match(expected_value="}")
        if not rb:
            return None

        return node

    def parse_while_stmt(self):
        node = ParseTreeNode("WHILE_STMT")
        w_kw = self.match(expected_value="talk")
        if not w_kw:
            return None
        lp = self.match(expected_value="(")
        if not lp:
            return None
        expr_node = self.parse_expr()
        node.add_child(expr_node)
        rp = self.match(expected_value=")")
        if not rp:
            return None
        lb = self.match(expected_value="{")
        if not lb:
            return None
        slist = self.parse_statement_list()
        node.add_child(slist)
        rb = self.match(expected_value="}")
        if not rb:
            return None
        return node

    def parse_print_stmt(self):
        node = ParseTreeNode("PRINT_STMT")
        sp = self.match(expected_value="spill")
        if not sp:
            return None
        lp = self.match(expected_value="(")
        if not lp:
            return None
        expr = self.parse_expr()
        if not expr:
            return None
        node.add_child(expr)
        rp = self.match(expected_value=")")
        if not rp:
            return None
        semi = self.match(expected_value=";")
        if not semi:
            return None
        return node

    def parse_input_stmt(self):
        node = ParseTreeNode("INPUT_STMT")
        pst = self.match(expected_value="post")
        if not pst:
            return None
        lp = self.match(expected_value="(")
        if not lp:
            return None
        ident = self.match(expected_type="Identifier")
        if not ident:
            return None
        node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
        rp = self.match(expected_value=")")
        if not rp:
            return None
        semi = self.match(expected_value=";")
        if not semi:
            return None
        return node

    def parse_switch_stmt(self):
        node = ParseTreeNode("SWITCH_STMT")
        sw = self.match(expected_value="mood")
        if not sw:
            return None
        lp = self.match(expected_value="(")
        if not lp:
            return None
        expr = self.parse_expr()
        if not expr:
            return None
        node.add_child(expr)
        rp = self.match(expected_value=")")
        if not rp:
            return None
        lb = self.match(expected_value="{")
        if not lb:
            return None
        slist = self.parse_statement_list()
        node.add_child(slist)
        rb = self.match(expected_value="}")
        if not rb:
            return None
        return node

    def parse_block(self):
        node = ParseTreeNode("BLOCK")
        lb = self.match(expected_value="{")
        if not lb:
            return None
        stmt_list = self.parse_statement_list()
        node.add_child(stmt_list)
        rb = self.match(expected_value="}")
        if not rb:
            return None
        return node

    def parse_assignment(self):
        node = ParseTreeNode("ASSIGNMENT")
        ident = self.match(expected_type="Identifier")
        if not ident:
            return None
        node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
        eq = self.match(expected_value="=")
        if not eq:
            return None
        expr = self.parse_expr()
        if not expr:
            return None
        node.add_child(expr)
        semi = self.match(expected_value=";")
        if not semi:
            return None
        return node

    def parse_expr(self):
        """
        For now, just parse a single numeric literal, string, or identifier.
        You can expand to handle operators (+, -, etc.) or parentheses.
        """
        expr_node = ParseTreeNode("EXPR")
        if not self.current_token:
            self.report_error("Unexpected end of tokens in expression.")
            return None

        ttype, tval = self.current_token
        if ttype in {"Integer", "Float Number", "String", "Identifier"}:
            self.advance()
            child = ParseTreeNode(ttype.upper().replace(" ", "_"), tval)
            expr_node.add_child(child)
            return expr_node
        else:
            self.report_error(f"Invalid expression token: ({ttype}, {tval})")
            return None
