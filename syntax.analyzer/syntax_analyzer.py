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
            self.report_error(
                f"Unexpected end of tokens. Expected {expected_type or expected_value}"
            )
            return None

        ttype, tval = self.current_token
        type_ok = (expected_type is None or ttype == expected_type)
        value_ok = (expected_value is None or tval == expected_value)

        if type_ok and value_ok:
            matched = self.current_token
            self.advance()
            return matched
        else:
            self.report_error(
                f"Expected {expected_type or ''} {expected_value or ''}, got ({ttype}, {tval})"
            )
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

        if tval in {
            "flex", "nocap", "bet", "num",  # declarations
            "sus",                          # if
            "forreal",                      # for
            "talk",                         # while
            "spill",                        # print
            "post",                         # input
            "mood",                         # switch
            "trend",                        # function def
            "else",                         # else / else if
            "reply",                        # return statement
            "line",
        }:
            return True

        if ttype == "Identifier":
            return True

        if ttype == "Function":
            return True

        if tval == "{":
            return True

        return False

    def parse_statement(self):
        if not self.current_token:
            return None

        ttype, tval = self.current_token

        # Declarations
        if tval in {"flex", "nocap", "bet", "num"}:
            return self.parse_declaration()

        # If
        if tval == "sus":
            return self.parse_if_stmt()

        # For
        if tval == "forreal":
            return self.parse_for_stmt()

        # While
        if tval == "talk":
            return self.parse_while_stmt()

        # Print
        if tval == "spill":
            return self.parse_print_stmt()

        # Input
        if tval == "post":
            return self.parse_input_stmt()

        # Switch
        if tval == "mood":
            return self.parse_switch_stmt()

        # Function definition
        if tval == "trend":
            return self.parse_function_definition()

        # Else
        if tval == "else":
            return self.parse_else_block()

        # Return statement
        if tval == "reply":
            return self.parse_return_stmt()

        # "line" statement
        if tval == "line":
            return self.parse_line_statement()

        # Function Call
        if ttype == "Function":
            call_node = self.parse_function_call()
            stmt_node = ParseTreeNode("FUNCTION_STMT")
            stmt_node.add_child(call_node)
            return stmt_node

        # Block
        if tval == "{":
            return self.parse_block()

        # Assignment or expression
        if ttype == "Identifier":
            return self.parse_assignment_or_expr()

        self.report_error(f"Unrecognized statement start: ({ttype}, {tval})")
        return None

    # ----------------------------------------------------------------
    # Line Statement
    # ----------------------------------------------------------------
    def parse_line_statement(self):
        node = ParseTreeNode("LINE_STMT")

        line_kw = self.match(expected_value="line")
        if not line_kw:
            return None

        if not self.current_token:
            return None
        eq_type, eq_val = self.current_token
        if eq_val == "=":
            self.advance()
        else:
            self.report_error(f"Expected '=' after 'line'. Got {eq_type}, {eq_val}")
            return None

        bracket = self.match(expected_type="Open Bracket", expected_value="[")
        if not bracket:
            return None

        elements_node = ParseTreeNode("LINE_ELEMENTS")
        while self.current_token and self.current_token[1] != "]":

            ttype, tval = self.current_token

            if ttype == "Integer":
                int_node = ParseTreeNode("INTEGER", tval)
                elements_node.add_child(int_node)
                self.advance()

                if self.current_token and self.current_token[1] == ",":
                    self.advance()  
            else:

                if tval == ",":
                    self.advance() 
                    continue
                else:
                    self.report_error(
                        f"Expected integer or ']' in line statement, got {ttype}, {tval}"
                    )
                    return node

        node.add_child(elements_node)

        close_bracket = self.match(expected_type="Close Bracket", expected_value="]")
        if not close_bracket:
            return None

        return node

    # ----------------------------------------------------------------
    # Declarations
    # ----------------------------------------------------------------
    def parse_declaration(self):
        node = ParseTreeNode("DECLARATION")
        decl_kw = self.match(expected_type="Keyword")
        if not decl_kw:
            return None
        node.value = decl_kw[1] 

        ident = self.match(expected_type="Identifier")
        if not ident:
            return None
        node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))

        if self.current_token and self.current_token[1] in {"=", "+=", "-=", "*=", "/=", "%=", "^="}:
            op_token = self.match()
            if not op_token:
                return None
            expr = self.parse_expression()
            if not expr:
                return None
            assign_node = ParseTreeNode("ASSIGN_OP", op_token[1])
            assign_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
            assign_node.add_child(expr)
            node.add_child(assign_node)

        return node

    # ----------------------------------------------------------------
    # IF statement (supports else-if chain and else block)
    # ----------------------------------------------------------------
    def parse_if_stmt(self):
        chain_node = ParseTreeNode("IF_CHAIN")

        first_if = self.parse_single_if_block()
        if not first_if:
            return None
        chain_node.add_child(first_if)

        while self.current_token and self.current_token[1] == "else":

            else_kw = self.match(expected_value="else")
            if not else_kw:
                return chain_node  

            if self.current_token and self.current_token[1] == "sus":
                elif_block = self.parse_single_if_block(is_elif=True)
                if elif_block:
                    chain_node.add_child(elif_block)
                else:
                    return chain_node
            else:
                else_block = self.parse_else_block()
                if else_block:
                    chain_node.add_child(else_block)
                return chain_node

        return chain_node

    def parse_single_if_block(self, is_elif=False):
        node_type = "IF_BLOCK" if not is_elif else "ELSE_IF_BLOCK"
        node = ParseTreeNode(node_type)

        sus_kw = self.match(expected_value="sus")
        if not sus_kw:
            return None

        lp = self.match(expected_value="(")
        if not lp:
            return None

        condition_expr = self.parse_expression()
        if not condition_expr:
            return None
        node.add_child(condition_expr)

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

        return node

    def parse_else_block(self):
        node = ParseTreeNode("ELSE_BLOCK")

        if self.current_token and self.current_token[1] == "sus":
            return None

        lb = self.match(expected_value="{")
        if not lb:
            return None

        stmt_list = self.parse_statement_list()
        node.add_child(stmt_list)

        rb = self.match(expected_value="}")
        if not rb:
            return None

        return node

    # ----------------------------------------------------------------
    # FOR statement
    # ----------------------------------------------------------------
    def parse_for_stmt(self):
        node = ParseTreeNode("FOR_STMT")
        fr_kw = self.match(expected_value="forreal")
        if not fr_kw:
            return None

        lp = self.match(expected_value="(")
        if not lp:
            return None

        expr1 = self.parse_expression()
        if not expr1:
            return None
        node.add_child(expr1)

        sc1 = self.match(expected_value=";")
        if not sc1:
            return None

        expr2 = self.parse_expression()
        if not expr2:
            return None
        node.add_child(expr2)

        sc2 = self.match(expected_value=";")
        if not sc2:
            return None

        expr3 = self.parse_expression()
        if not expr3:
            return None
        node.add_child(expr3)

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

        return node

    # ----------------------------------------------------------------
    # WHILE statement
    # ----------------------------------------------------------------
    def parse_while_stmt(self):
        node = ParseTreeNode("WHILE_STMT")

        talk_kw = self.match(expected_value="talk")
        if not talk_kw:
            return None

        lp = self.match(expected_value="(")
        if not lp:
            return None

        condition_expr = self.parse_expression()
        if not condition_expr:
            return None
        node.add_child(condition_expr)

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

        return node

    # ----------------------------------------------------------------
    # PRINT statement
    # ----------------------------------------------------------------
    def parse_print_stmt(self):
        node = ParseTreeNode("PRINT_STMT")

        sp_kw = self.match(expected_value="spill")
        if not sp_kw:
            return None

        lp = self.match(expected_value="(")
        if not lp:
            return None

        expr = self.parse_expression()
        if not expr:
            return None
        node.add_child(expr)

        rp = self.match(expected_value=")")
        if not rp:
            return None

        return node

    # ----------------------------------------------------------------
    # INPUT statement
    # ----------------------------------------------------------------
    def parse_input_stmt(self):
        node = ParseTreeNode("INPUT_STMT")

        pst_kw = self.match(expected_value="post")
        if not pst_kw:
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

        return node

    # ----------------------------------------------------------------
    # SWITCH statement
    # ----------------------------------------------------------------
    def parse_switch_stmt(self):
        node = ParseTreeNode("SWITCH_STMT")

        sw_kw = self.match(expected_value="mood")
        if not sw_kw:
            return None

        lp = self.match(expected_value="(")
        if not lp:
            return None

        expr = self.parse_expression()
        if not expr:
            return None
        node.add_child(expr)

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

        return node

    # ----------------------------------------------------------------
    # FUNCTION DEFINITION
    # ----------------------------------------------------------------
    def parse_function_definition(self):
        node = ParseTreeNode("FUNCTION_DEF")

        trend_kw = self.match(expected_value="trend")
        if not trend_kw:
            return None

        func_name = self.match(expected_type="Function")
        if not func_name:
            return None
        node.value = func_name[1]

        lp = self.match(expected_value="(")
        if not lp:
            return None

        params = self.parse_param_list()
        node.add_child(params)

        rp = self.match(expected_value=")")
        if not rp:
            return None

        block = self.parse_block()
        if block:
            node.add_child(block)
        else:
            return None

        return node

    def parse_param_list(self):
        params_node = ParseTreeNode("PARAM_LIST")

        while self.current_token and self.current_token[1] != ")":

            if self.current_token[0] == "Keyword":
                type_tok = self.match(expected_type="Keyword")
            else:
                self.report_error("Parameter type must be a keyword (e.g. flex, nocap, bet).")
                return params_node

            ident_tok = self.match(expected_type="Identifier")
            if not ident_tok:
                return params_node

            param_node = ParseTreeNode("PARAM")
            param_node.add_child(ParseTreeNode("TYPE", type_tok[1]))
            param_node.add_child(ParseTreeNode("IDENTIFIER", ident_tok[1]))
            params_node.add_child(param_node)

            if self.current_token and self.current_token[1] == ",":
                self.advance()
                continue
            else:
                break

        return params_node

    def parse_function_call(self):
        call_node = ParseTreeNode("FUNCTION_CALL")

        func_tok = self.match(expected_type="Function")
        if not func_tok:
            return None
        call_node.value = func_tok[1]

        lp = self.match(expected_type="Open Parenthesis", expected_value="(")
        if not lp:
            return None

        while self.current_token and self.current_token[1] != ")":
            arg_expr = self.parse_expression()
            if not arg_expr:
                return None
            call_node.add_child(arg_expr)

            if self.current_token and self.current_token[1] == ",":
                self.advance()
                continue
            else:
                break

        rp = self.match(expected_type="Close Parenthesis", expected_value=")")
        if not rp:
            return None

        return call_node

    def parse_array_initializer(self):
        array_node = ParseTreeNode("ARRAY_LITERAL")

        ob = self.match(expected_type="Open Bracket", expected_value="[")
        if not ob:
            return None

        while self.current_token and self.current_token[1] != "]":
            element = None

            ttype, tval = self.current_token

            if ttype == "Function":
                element = self.parse_function_call()
                if not element:
                    return None

            else:
                element = self.parse_expression()
                if not element:
                    return None

            array_node.add_child(element)

            if self.current_token and self.current_token[1] == ",":
                self.advance()
                continue
            else:
                break

        cb = self.match(expected_type="Close Bracket", expected_value="]")
        if not cb:
            return None

        return array_node

    # ----------------------------------------------------------------
    # RETURN statement (reply)
    # ----------------------------------------------------------------
    def parse_return_stmt(self):
        node = ParseTreeNode("RETURN_STMT")

        r_kw = self.match(expected_value="reply")
        if not r_kw:
            return None

        expr = self.parse_expression()
        if not expr:
            return None
        node.add_child(expr)

        return node

    # ----------------------------------------------------------------
    # BLOCK
    # ----------------------------------------------------------------
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

    # ----------------------------------------------------------------
    # ASSIGNMENT or EXPRESSION STATEMENT
    # ----------------------------------------------------------------
    def parse_assignment_or_expr(self):
        node = ParseTreeNode("EXPR_STMT")

        ident = self.match(expected_type="Identifier")
        if not ident:
            return None

        if self.current_token:
            ttype, tval = self.current_token

            if ttype in {
                "Equal Sign",
                "Addition Assignment",
                "Subtraction Assignment",
                "Multiplication Assignment",
                "Division Assignment",
                "Remainder Assignment",
                "Exponentiation Assignment"} and tval in {"=", "+=", "-=", "*=", "/=", "%=", "^="}:
                op_tok = self.match() 
                if not op_tok:
                    return None

                if self.current_token and self.current_token[1] == "[":
                    array_node = self.parse_array_initializer()
                    if not array_node:
                        return None
                    assign_node = ParseTreeNode("ASSIGNMENT_OP", op_tok[1])
                    assign_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
                    assign_node.add_child(array_node)
                    node.add_child(assign_node)
                    return node
                else:
                    expr = self.parse_expression()
                    if not expr:
                        return None
                    assign_node = ParseTreeNode("ASSIGNMENT_OP", op_tok[1])
                    assign_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
                    assign_node.add_child(expr)
                    node.add_child(assign_node)
                    return node

            elif ttype in {"Increment Operator", "Decrement Operator"} and tval in {"++", "--"}:
                incdec_tok = self.match()
                incdec_node = ParseTreeNode("INCDEC_OP", incdec_tok[1])
                incdec_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
                node.add_child(incdec_node)
                return node

        expr_node = ParseTreeNode("EXPR")
        expr_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
        node.add_child(expr_node)
        return node

    # ----------------------------------------------------------------
    # EXPRESSIONS
    # ----------------------------------------------------------------
    def parse_expression(self):
        left_node = self.parse_primary()
        if not left_node:
            return None

        while self.current_token and self.current_token[0] in {
                "Operator",
                "Equal Sign",
                "Addition Assignment",
                "Subtraction Assignment",
                "Multiplication Assignment",
                "Division Assignment",
                "Remainder Assignment",
                "Exponentiation Assignment",
                "Addition Operator",
                "Subtraction Operator",
                "Multiplication Operator",
                "Division Operator",
                "Remainder Operator",
                "Exponentiation Operator",
                "Logical NOT Operator",
                "Logical AND Operator",
                "Logical OR Operator",
                "Equal To Operator",
                "Not Equal To Operator",
                "Greater Than Operator",
                "Less Than Operator",
                "Greater Than or Equal To Operator",
                "Less Than or Equal To Operator"
            }:
            op_token = self.current_token  # e.g. ("Operator", ">=")
            self.advance()

            right_node = self.parse_primary()
            if not right_node:
                return None

            bin_op_node = ParseTreeNode("BINARY_OP", op_token[1])
            bin_op_node.add_child(left_node)
            bin_op_node.add_child(right_node)
            left_node = bin_op_node

        return left_node

    def parse_primary(self):
        if not self.current_token:
            self.report_error("Unexpected end of tokens in parse_primary().")
            return None

        ttype, tval = self.current_token

        if ttype == "Open Parenthesis" and tval == "(":
            self.match("Open Parenthesis", "(")
            subexpr = self.parse_expression()
            self.match("Close Parenthesis", ")")
            return subexpr

        if ttype == "Open Bracket" and tval == "[":
            return self.parse_array_initializer()

        if ttype in {"Integer", "Float Number", "String", "Identifier"}:
            node_type = ttype.upper().replace(" ", "_") 
            primary_node = ParseTreeNode(node_type, tval)
            self.advance() 

            if self.current_token and \
            self.current_token[0] in {"Increment Operator", "Decrement Operator"}:
                incdec_tok = self.current_token
                postfix_node = ParseTreeNode("POSTFIX_OP", incdec_tok[1])
                postfix_node.add_child(primary_node)
                self.advance()

                return postfix_node

            return primary_node

        self.report_error(f"Invalid expression token: ({ttype}, {tval})")
        return None