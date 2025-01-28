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
        """
        token_lines is expected to be a list of lists of tokens.
        Each token is typically a tuple: (TokenType, TokenValue)
        Example: ("Keyword", "sus"), ("Identifier", "grade"),
                 ("Operator", ">="), ("Integer", "90"), ("Bracket", "("), etc.
        """
        self.tokens = flatten_token_lines(token_lines)
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.error_count = 0

        for i, token in enumerate(self.tokens):
            print(i, token)

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match(self, expected_type=None, expected_value=None):
        """
        Attempt to match the current token to either an expected type or an expected value.
        If both are provided, both must match.
        If it matches, consume the token and return it.
        Otherwise, report an error and return None.
        """
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
        """
        Entry point: parse a list of statements until tokens are exhausted.
        """
        root = ParseTreeNode("PROGRAM")
        stmt_list = self.parse_statement_list()
        if stmt_list:
            root.add_child(stmt_list)
        else:
            self.report_error("Empty program or invalid statements.")
        return root

    def parse_statement_list(self):
        """
        Parse zero or more statements until we run out of tokens or cannot form a statement.
        """
        node = ParseTreeNode("STATEMENT_LIST")
        while self.can_start_statement():
            stmt = self.parse_statement()
            if stmt:
                node.add_child(stmt)
            else:
                # If we fail to parse a statement, break to avoid infinite loops
                break
        return node

    def can_start_statement(self):
        """
        Checks if the current token can begin a statement.
        """
        if not self.current_token:
            return False

        ttype, tval = self.current_token

        # Keywords that can start statements in this language
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
        }:
            return True

        # Identifiers can start an assignment or expression statement
        if ttype == "Identifier":
            return True

        # A block can start with '{'
        if tval == "{":
            return True

        return False

    def parse_statement(self):
        """
        Decide which kind of statement we are dealing with based on the current token.
        """
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

        # Else — might be part of an else-if chain or a standalone else block
        if tval == "else":
            return self.parse_else_block()

        # Return statement
        if tval == "reply":
            return self.parse_return_stmt()

        # Block
        if tval == "{":
            return self.parse_block()

        # Assignment or expression
        if ttype == "Identifier":
            return self.parse_assignment_or_expr()

        self.report_error(f"Unrecognized statement start: ({ttype}, {tval})")
        return None

    # ----------------------------------------------------------------
    # Declarations
    # ----------------------------------------------------------------
    def parse_declaration(self):
        """
        Example:
          flex age = 21
          num count = 1
          bet height = 5.9
        No semicolon in the new language (except inside forreal loops).
        """
        node = ParseTreeNode("DECLARATION")
        decl_kw = self.match(expected_type="Keyword")
        if not decl_kw:
            return None
        node.value = decl_kw[1]  # e.g. "flex", "nocap", "bet", "num"

        # Expect Identifier
        ident = self.match(expected_type="Identifier")
        if not ident:
            return None
        node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))

        # Optional '=' <expr>
        # (We can also handle +=, -=, etc. if desired, just expand here.)
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
            # In this scenario, the node is effectively both a DECLARATION and an assignment
            node.add_child(assign_node)

        return node

    # ----------------------------------------------------------------
    # IF statement (supports else-if chain and else block)
    # ----------------------------------------------------------------
    def parse_if_stmt(self):
        """
        Handles if/else-if/else chains of the form:

          sus (condition) {
              ... 
          }
          else sus (otherCondition) {
              ...
          }
          else {
              ...
          }
        """
        chain_node = ParseTreeNode("IF_CHAIN")

        # The first `sus(...) {}` is mandatory
        first_if = self.parse_single_if_block()
        if not first_if:
            return None
        chain_node.add_child(first_if)

        # Now handle possible `else sus(...) {}` or `else {}` blocks
        while self.current_token and self.current_token[1] == "else":
            # consume 'else'
            else_kw = self.match(expected_value="else")
            if not else_kw:
                return chain_node  # or break

            # check if next token is 'sus' => else if
            if self.current_token and self.current_token[1] == "sus":
                # parse another `sus(...) {}` block
                elif_block = self.parse_single_if_block(is_elif=True)
                if elif_block:
                    chain_node.add_child(elif_block)
                else:
                    return chain_node
            else:
                # plain else block
                else_block = self.parse_else_block()
                if else_block:
                    chain_node.add_child(else_block)
                # once we have a plain else, there's no more chain
                return chain_node

        return chain_node

    def parse_single_if_block(self, is_elif=False):
        """
        Parse `sus (expr) { statements }`.
        Used by both an initial `if` and an `else if`.
        """
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
        """
        Parse `else { statements }`.
        If the next token is 'sus', that's handled in parse_if_stmt (as else-if).
        """
        node = ParseTreeNode("ELSE_BLOCK")

        # If the current token is 'sus', that means else-if, which is handled above
        if self.current_token and self.current_token[1] == "sus":
            return None  # let parse_if_stmt handle it

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
        """
        forreal (i = 1; i <= 5; i++) {
            spill(i)
        }
        Note: semicolons appear only inside `forreal(...)`.
        """
        node = ParseTreeNode("FOR_STMT")
        fr_kw = self.match(expected_value="forreal")
        if not fr_kw:
            return None

        lp = self.match(expected_value="(")
        if not lp:
            return None

        # first expression
        expr1 = self.parse_expression()
        if not expr1:
            return None
        node.add_child(expr1)

        # semicolon
        sc1 = self.match(expected_value=";")
        if not sc1:
            return None

        # second expression (condition)
        expr2 = self.parse_expression()
        if not expr2:
            return None
        node.add_child(expr2)

        # semicolon
        sc2 = self.match(expected_value=";")
        if not sc2:
            return None

        # third expression (increment)
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
        """
        talk (count <= 3) {
            spill(count)
            count++
        }
        """
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
        """
        spill("Hello")
        """
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
        """
        post(name)
        """
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
        """
        mood (expr) {
            ...
        }
        """
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
        """
        trend add(num a, num b) {
            reply a + b
        }
        """
        node = ParseTreeNode("FUNCTION_DEF")

        trend_kw = self.match(expected_value="trend")
        if not trend_kw:
            return None

        func_name = self.match(expected_type="Function")
        if not func_name:
            return None
        node.value = func_name[1]  # e.g. "add"

        lp = self.match(expected_value="(")
        if not lp:
            return None

        params = self.parse_param_list()
        node.add_child(params)

        rp = self.match(expected_value=")")
        if not rp:
            return None

        # parse the function body as a block
        block = self.parse_block()
        if block:
            node.add_child(block)
        else:
            return None

        return node

    def parse_param_list(self):
        """
        Parse parameters inside parentheses: e.g. (num a, num b)
        """
        params_node = ParseTreeNode("PARAM_LIST")

        # If next token is ")", empty parameter list
        while self.current_token and self.current_token[1] != ")":
            # type must be a keyword (e.g. 'num', 'flex', etc.)
            if self.current_token[0] == "Keyword":
                type_tok = self.match(expected_type="Keyword")
            else:
                self.report_error("Parameter type must be a keyword (e.g. num).")
                return params_node

            # identifier
            ident_tok = self.match(expected_type="Identifier")
            if not ident_tok:
                return params_node

            param_node = ParseTreeNode("PARAM")
            param_node.add_child(ParseTreeNode("TYPE", type_tok[1]))
            param_node.add_child(ParseTreeNode("IDENTIFIER", ident_tok[1]))
            params_node.add_child(param_node)

            # if there's a comma, consume it and continue
            if self.current_token and self.current_token[1] == ",":
                self.advance()
                continue
            else:
                break

        return params_node

    # ----------------------------------------------------------------
    # RETURN statement (reply)
    # ----------------------------------------------------------------
    def parse_return_stmt(self):
        """
        reply <expr>
        """
        node = ParseTreeNode("RETURN_STMT")

        r_kw = self.match(expected_value="reply")
        if not r_kw:
            return None

        # The rest is an expression
        expr = self.parse_expression()
        if not expr:
            return None
        node.add_child(expr)

        return node

    # ----------------------------------------------------------------
    # BLOCK
    # ----------------------------------------------------------------
    def parse_block(self):
        """
        { statement_list }
        """
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
        """
        We check if it's "identifier = expr" or "identifier++" or "identifier--" etc.
        Otherwise treat it as an expression statement.
        """
        node = ParseTreeNode("EXPR_STMT")

        ident = self.match(expected_type="Identifier")
        if not ident:
            return None

        if self.current_token:
            ttype, tval = self.current_token

            # Check assignment operators (=, +=, -=, etc.)
            if ttype == "Operator" and tval in {"=", "+=", "-=", "*=", "/=", "%=", "^="}:
                op_tok = self.match()  # consume the operator
                if not op_tok:
                    return None
                expr = self.parse_expression()
                if not expr:
                    return None
                assign_node = ParseTreeNode("ASSIGNMENT_OP", op_tok[1])
                assign_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
                assign_node.add_child(expr)
                node.add_child(assign_node)
                return node

            # Increment/decrement operators (like ++ or --)
            elif ttype in {"Increment Operator", "Decrement Operator"} and tval in {"++", "--"}:
                incdec_tok = self.match()
                incdec_node = ParseTreeNode("INCDEC_OP", incdec_tok[1])
                incdec_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
                node.add_child(incdec_node)
                return node

        # If not an assignment or inc/dec, treat as expression statement with single identifier
        expr_node = ParseTreeNode("EXPR")
        expr_node.add_child(ParseTreeNode("IDENTIFIER", ident[1]))
        node.add_child(expr_node)
        return node

    # ----------------------------------------------------------------
    # EXPRESSIONS: a simple approach
    # ----------------------------------------------------------------
    def parse_expression(self):
        """
        A minimal expression parser that handles:
          - primary (number, string, identifier)
          - operators (>=, <=, +, -, etc.) in a left-associative chain.
        For example:  grade >= 90
                      x + 2 * y
        If you need more robust handling (operator precedence, parentheses),
        expand this method or implement separate parse_* functions.
        """
        left_node = self.parse_primary()
        if not left_node:
            return None

        # While next token is an operator, parse a binary op: left op right
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
                "Increment Operator",
                "Decrement Operator",
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
        """
        Primary = Identifier | Integer | Float Number | String | ( parenthesized expression ) ?
        For now, we just handle the four basic types plus an error if not found.
        """
        if not self.current_token:
            self.report_error("Unexpected end of tokens in parse_primary().")
            return None

        ttype, tval = self.current_token

        # Basic literal or identifier
        if ttype in {"Integer", "Float Number", "String", "Identifier"}:
            self.advance()
            node_type = ttype.upper().replace(" ", "_")
            return ParseTreeNode(node_type, tval)

        # If you want to handle '(' expr ')' for grouping, you can do:
        # if (ttype == "Bracket" and tval == "("):
        #     self.match("Bracket", "(")
        #     subexpr = self.parse_expression()
        #     self.match("Bracket", ")")
        #     return subexpr

        self.report_error(f"Invalid expression token: ({ttype}, {tval})")
        return None