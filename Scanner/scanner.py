# Author: Amogh Sharma

# Token types
class TokenType:
    LCURVEDBRACKET = 'LCURVEDBRACKET' # '{'
    RCURVEDBRACKET = 'RCURVEDBRACKET' # '}'
    LBOXBRACKET = 'LBOXBRACKET' # '['
    RBOXBRACKET = 'RBOXBRACKET' # ']'
    COMMA = 'COMMA' # ','
    COLON = 'COLON' # ':'
    DICT = 'DICT' # JSON Dictionaries
    ARRAY = 'ARRAY' # JSON Arrays
    PAIR = 'PAIR' # Key-value Pairs
    VALUE = 'VALUE' # Values
    STRING = 'STRING' # String values
    INTEGER = 'INTEGER' # Integers
    BOOLEAN = 'BOOLEAN' # True and False values
    NULL = 'NULL' # 'null'
    EOF = 'EOF' # End of input

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.type == TokenType.STRING:
            return f"<STR, {self.value}>"
        elif self.type == TokenType.INTEGER:
            return f"<INT, {self.value}>"
        elif self.type == TokenType.BOOLEAN:
            return f"<BOOL, {self.value}>"
        elif self.type == TokenType.LCURVEDBRACKET:
            return "<{>"
        elif self.type == TokenType.RCURVEDBRACKET:
            return "<}>"
        elif self.type == TokenType.LBOXBRACKET:
            return "<[>"
        elif self.type == TokenType.RBOXBRACKET:
            return "<]>"
        elif self.type == TokenType.COMMA:
            return "<,>"
        elif self.type == TokenType.COLON:
            return "<:>"
        elif self.type == TokenType.NULL:
            return "<null>"
        else:
            return f"<{self.type}>"


# Lexer error
class LexerError(Exception):
    def __init__(self, position, character):
        self.position = position
        self.character = character
        super().__init__(f"Invalid character '{character}' at position {position}")

# Implements the scanner as a DFA and detects lexical errors
class LexerDFA:
    def __init__(self, input_text):
        # Input string
        self.input_text = input_text

        # Current position
        self.position = 0
        self.current_char = self.input_text[self.position] if self.input_text else None

    # Input Buffering
    def advance(self):
        self.position += 1
        if self.position >= len(self.input_text):
            # End of input
            self.current_char = None
        else:
            self.current_char = self.input_text[self.position]

    # If whitespace, don't do anything and just advance to the next input char
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Similarly, skip newline
    def skip_newline(self):
        self.advance()

    # Recognize string values
    def recognize_string(self):
        result = ''

        # Read each character of the string and store it in result
        while self.current_char is not None:
            result += self.current_char
            self.advance()

            # Stop reading string when the ending quotation is reached
            if self.current_char == '"':
                result += self.current_char
                self.advance()
                break

        return Token(TokenType.STRING, result)


    # Recognize integers
    def recognize_integer(self):
        result = ''

        # Read each digit of the integer
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char in ['.', 'e', 'E', '-', '+']):
            result += self.current_char
            self.advance()

        # If it is in scientific notation, return the number as is in scientific notation
        if result.lower().__contains__("e"):
            # Raise error if there is more than one e in the scientific notation
            if result.lower().count("e") > 1:
                raise LexerError(self.position, result.lower())

            return Token(TokenType.INTEGER, result)

        # Don't output a number with a decimal point if it is a whole number
        result = float(result)
        if result.is_integer():
            result = int(result)

        return Token(TokenType.INTEGER, result)

    # Recognize true or false values
    def recognize_boolean(self):
        result = ''

        # Read the boolean value character by character
        while self.current_char is not None:
            result += self.current_char

            # Once 'e' is reached, stop reading the value
            if self.current_char == 'e':
                self.advance()
                break

            self.advance()

        # If the value is not true or false, raise an error
        if result != 'true' and result != 'false':
            raise LexerError(self.position, result)

        return Token(TokenType.BOOLEAN, result)

    # Recognize null values
    def recognize_null(self):
        result = ''
        while self.current_char is not None:
            result += self.current_char
            self.advance()

            # If null has been fully scanned, stop loop. Recovers from lexical errors like 'nulll'
            if result.__contains__('null'):
                break

        # Raise error if the value is not exactly null and return a proper null
        if result != 'null':
            raise LexerError(self.position, result)

        return Token(TokenType.NULL, result)

    # Get next token from input
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Skip newline
            elif self.current_char == '\n':
                self.skip_newline()
                continue

            # Recognize brackets and punctuation
            elif self.current_char == '{':
                self.advance()
                return Token(TokenType.LCURVEDBRACKET)
            elif self.current_char == '}':
                self.advance()
                return Token(TokenType.RCURVEDBRACKET)
            elif self.current_char == '[':
                self.advance()
                return Token(TokenType.LBOXBRACKET)
            elif self.current_char == ']':
                self.advance()
                return Token(TokenType.RBOXBRACKET)
            elif self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA)
            elif self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON)

            # For String
            elif self.current_char == '"':
                return self.recognize_string()

            # For Boolean
            elif self.current_char in ['t', 'f']:
                return self.recognize_boolean()

            # For Null value
            elif self.current_char == 'n':
                return self.recognize_null()

            # For Integer values
            elif self.current_char.isdigit() or self.current_char in ['-', '+']:
                return self.recognize_integer()

            # Raise exception for unrecognized characters
            else:
                raise LexerError(self.position, self.current_char)

        # Eof
        return Token(TokenType.EOF)

    # Tokenize the input
    def tokenize(self):
        tokens = []
        while True:
            try:
                token = self.get_next_token()
            except LexerError as e:
                print(f"Lexical Error: {e}")
                break
            if token is not None and token.type == TokenType.EOF:
                break
            tokens.append(token)
        return tokens

# The main code that runs the lexer with a file
# To run, please input the file name in the open() function as given below
if __name__ == "__main__":
    # Open the test input file to read
    input_file = open("Scanner/input_test1.txt", "r")
    input_string = ""

    # Turn the input file in to a string
    for line in input_file.readlines():
        input_string += line

    # Run the file through the Lexer DFA and tokenize it
    lexer = LexerDFA(input_string)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)