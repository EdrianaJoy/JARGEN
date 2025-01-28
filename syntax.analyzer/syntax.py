from test123 import *

class Token:
    """
    A simple Token representation.
    Fields:
      - type  : e.g., 'Keyword', 'Identifier', 'Operator', ...
      - value : the actual string, e.g., 'flex', 'sus', '=', '(', ')'
    """
    def __init__(self, token_type, token_value):
        self.type = token_type
        self.value = token_value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Parser:
    def __init__(self, tokens):
        """
        tokens: a list of tokens (flattened) that come from the lexer.
                Note that your lexer returns a list of lists (lines).
                So you'd want to flatten that into a single list of Tokens
                for convenience.
        """
        self.tokens = tokens
        self.position = 0  # current index in tokens
        self.current_token = self.tokens[self.position] if self.tokens else None

    def advance(self):
        """
        Move to the next token.
        """
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None  # indicates end-of-stream

    def peek(self):
        """
        Look at the next token without consuming it.
        """
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None

    def match(self, *expected_values):
        """
        Consumes the current token if its value is among expected_values,
        otherwise raises an error. This is used for easily matching
        specific keywords or symbols.
        """
        if self.current_token and self.current_token.value in expected_values:
            self.advance()
        else:
            raise SyntaxError(
                f"Expected one of {expected_values}, got {self.current_token}"
            )

    def match_type(self, *expected_types):
        """
        Consumes the current token if its type is among expected_types,
        otherwise raises an error.
        """
        if self.current_token and self.current_token.type in expected_types:
            token_val = self.current_token.value
            self.advance()
            return token_val
        else:
            raise SyntaxError(
                f"Expected token type {expected_types}, got {self.current_token}"
            )

    def parse_program(self):
        """
        Entry point for parsing: Program -> StatementList
        """
        statements = []
        while self.current_token is not None:
            stmt = self.parse_statement()
            statements.append(stmt)
        return statements

    def parse_statement(self):
        """
        Statement -> DeclarationStatement
                   | AssignmentStatement
                   | ConditionalStatement
                   | LoopStatement
                   | PrintStatement
                   | FunctionDefinition
                   | BlockStatement
                   | ";"
        """
        # Look at the current token to decide what to parse
        if self.current_token is None:
            return None
        
        # handle block
        if self.current_token.value == "{":
            return self.parse_block_statement()
        
        # handle empty statement
        if self.current_token.value == ";":
            self.advance()
            return ("EmptyStatement", )

        # handle DeclarationStatement
        if self.current_token.value in ("flex", "nocap", "bet"):
            return self.parse_declaration_statement()

        # handle function definition
        if self.current_token.value == "trend":
            return self.parse_function_definition()

        # handle conditionals
        if self.current_token.value == "sus":
            return self.parse_conditional_statement()

        # handle else (which might appear in some error scenario if code is structured differently)
        if self.current_token.value == "else":
            # Typically this is caught as part of 'sus' expansions, but might be handled here if stand-alone
            raise SyntaxError("Unexpected 'else' without preceding 'sus' block.")
        
        # handle loops
        if self.current_token.value == "forreal":
            return self.parse_for_statement()
        if self.current_token.value == "talk":
            return self.parse_while_statement()

        # handle print
        if self.current_token.value == "spill":
            return self.parse_print_statement()

        # If not recognized yet, it might be an assignment or expression
        return self.parse_possible_assignment()

    # ------------------------------------------------------
    # Parsing specific constructs
    # ------------------------------------------------------

    def parse_block_statement(self):
        """
        BlockStatement -> "{" StatementList "}"
        """
        self.match("{")
        statements = []
        while self.current_token and self.current_token.value != "}":
            statements.append(self.parse_statement())
        self.match("}")
        return ("BlockStatement", statements)

    def parse_declaration_statement(self):
        """
        DeclarationStatement -> ( "flex" | "nocap" | "bet" ) Identifier "=" Expression ";"
        """
        decl_type = self.current_token.value  # flex | nocap | bet
        self.advance()

        identifier = self.match_type("Identifier")
        self.match("=")
        expr = self.parse_expression()
        self.match(";")

        return ("DeclarationStatement", decl_type, identifier, expr)

    def parse_function_definition(self):
        """
        FunctionDefinition -> "trend" FunctionName "(" [ ParameterList ] ")" BlockStatement
        """
        self.match("trend")
        func_name = self.match_type("Identifier")  # your lexer tags function name as "Function" or "Identifier"?
        self.match("(")

        params = []
        if self.current_token.value != ")":
            params = self.parse_parameter_list()
        self.match(")")

        block = self.parse_block_statement()

        return ("FunctionDefinition", func_name, params, block)

    def parse_parameter_list(self):
        """
        ParameterList -> Parameter { "," Parameter }
        Each Parameter can be: ( "num" | "char" | "caption" | "Identifier" ) Identifier
        or simplified to just "Identifier".
        """
        params = []
        params.append(self.parse_parameter())
        while self.current_token and self.current_token.value == ",":
            self.match(",")
            params.append(self.parse_parameter())
        return params

    def parse_parameter(self):
        """
        Parameter -> 
          - Possibly a type token (num, char, caption, etc.) followed by an Identifier
          - Or a single identifier
        """
        # If the current token is a type, consume it, then expect an identifier
        if self.current_token.value in ("num", "char", "caption"):
            param_type = self.current_token.value
            self.advance()
            param_name = self.match_type("Identifier")
            return (param_type, param_name)
        else:
            # Otherwise, treat it as an identifier
            param_name = self.match_type("Identifier")
            return ("Identifier", param_name)

    def parse_conditional_statement(self):
        """
        ConditionalStatement -> "sus" "(" Expression ")" BlockStatement 
                                { "else" "sus" "(" Expression ")" BlockStatement }
                                [ "else" BlockStatement ]
        """
        # first 'sus'
        self.match("sus")
        self.match("(")
        expr = self.parse_expression()
        self.match(")")
        true_block = self.parse_block_statement()

        branches = [("IfBranch", expr, true_block)]
        
        # check for repeated else sus
        while self.current_token and self.current_token.value == "else":
            self.match("else")
            # check if next is "sus" or just a block
            if self.current_token and self.current_token.value == "sus":
                self.match("sus")
                self.match("(")
                elif_expr = self.parse_expression()
                self.match(")")
                elif_block = self.parse_block_statement()
                branches.append(("ElseIfBranch", elif_expr, elif_block))
            else:
                # plain else
                else_block = self.parse_block_statement()
                branches.append(("ElseBranch", else_block))
                break  # no more chaining after plain else

        return ("ConditionalStatement", branches)

    def parse_for_statement(self):
        """
        ForStatement -> "forreal" "(" ForInitializer ";" Expression ";" ForUpdate ")" BlockStatement
        """
        self.match("forreal")
        self.match("(")
        
        # ForInitializer 
        # Could be 'Identifier = Expression' or a Declaration
        initializer = None
        if self.current_token.type == "Identifier":
            # e.g. i = 0
            id_name = self.match_type("Identifier")
            self.match("=")
            init_expr = self.parse_expression()
            initializer = ("ForInitAssign", id_name, init_expr)
        elif self.current_token.value in ("flex", "nocap", "bet"):
            # e.g. flex i = 0;
            # But we do not match the semicolon here
            decl_type = self.current_token.value
            self.advance()
            id_name = self.match_type("Identifier")
            self.match("=")
            init_expr = self.parse_expression()
            initializer = ("ForInitDecl", decl_type, id_name, init_expr)
        else:
            raise SyntaxError("Invalid for initializer")
        self.match(";")

        # Condition expression
        condition = self.parse_expression()
        self.match(";")

        # Update expression
        update = self.parse_expression()
        self.match(")")

        block = self.parse_block_statement()

        return ("ForStatement", initializer, condition, update, block)

    def parse_while_statement(self):
        """
        WhileStatement -> "talk" "(" Expression ")" BlockStatement
        """
        self.match("talk")
        self.match("(")
        condition = self.parse_expression()
        self.match(")")
        block = self.parse_block_statement()
        return ("WhileStatement", condition, block)

    def parse_print_statement(self):
        """
        PrintStatement -> "spill" "(" [ ExpressionList ] ")" ";"
        """
        self.match("spill")
        self.match("(")
        exprs = []
        if self.current_token and self.current_token.value != ")":
            exprs = self.parse_expression_list()
        self.match(")")
        self.match(";")
        return ("PrintStatement", exprs)

    def parse_expression_list(self):
        """
        ExpressionList -> Expression { "," Expression }
        """
        exprs = []
        exprs.append(self.parse_expression())
        while self.current_token and self.current_token.value == ",":
            self.match(",")
            exprs.append(self.parse_expression())
        return exprs

    def parse_possible_assignment(self):
        """
        Attempt to parse either:
            - AssignmentStatement: Identifier = Expression ;
            - Or just parse an ExpressionStatement: Expression ;
        """
        if self.current_token.type == "Identifier":
            # peek next token
            next_t = self.peek()
            if next_t and next_t.value == "=":
                # It's an assignment
                id_name = self.current_token.value
                self.advance()  # consume identifier
                self.match("=")
                expr = self.parse_expression()
                self.match(";")
                return ("AssignmentStatement", id_name, expr)
        
        # Otherwise parse an expression statement
        expr = self.parse_expression()
        self.match(";")
        return ("ExpressionStatement", expr)

    def parse_expression(self):
        """
        Highly simplified expression parsing:
        Expression -> SimpleExpression
        In real usage, you'd expand into sub-rules to handle operator precedence, 
        parentheses, unary ops, etc.
        """
        return self.parse_simple_expression()

    def parse_simple_expression(self):
        """
        SimpleExpression -> ( Integer | Float | String | Identifier ) 
                           { Operator ( Integer | Float | String | Identifier ) }
        """
        lhs = self.parse_operand()
        # Check for repeated operator-operand pairs
        while self.current_token and self.current_token.value in (
            "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", 
            "&&", "||", "^", "+=", "-=", "*=", "/=", "%=", "^=", "++", "--", "!"
        ):
            op = self.current_token.value
            self.advance()
            rhs = self.parse_operand()
            lhs = ("BinaryOp", op, lhs, rhs)
        return lhs

    def parse_operand(self):
        """
        Operand -> Integer | Float | String | Identifier
        """
        if not self.current_token:
            raise SyntaxError("Unexpected end of tokens in parse_operand")

        token_type = self.current_token.type
        token_val = self.current_token.value

        if token_type in ("Integer", "Float Number", "String", "Identifier", "Reserved Word"):
            self.advance()
            return (token_type, token_val)
        else:
            raise SyntaxError(f"Unexpected token {self.current_token} in expression.")