# Author: Amogh Sharma

class JSONNode:
    def __init__(self, label, value=None, parent=None):
        self.label = label  # 'list', 'value', 'STRING'
        self.value = value  # "abc" for a STRING node
        self.children = []  # List of further JSONNode objects
        self.parent = parent  # The parent node of this JSONNode

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, file=None, depth=0):
        indent = "  " * depth
        line = ""

        # Print the node label and value (if available)
        if self.value is not None:
            line = f"{indent}{self.label}: {self.value}"
        else:
            line = f"{indent}{self.label}"

        # Print to the console and an output file, if given
        if file is not None:
            file.write(line + '\n')
        print(line)

        # Print out all indented child nodes
        for child in self.children:
            child.print_tree(file, depth + 1)


class Parser:
    def __init__(self, lexer_file):
        self.lexer_file = lexer_file
        self.current_node = None
        self.root = None

    # Starts the parsing process by looping over each line of input.
    def parse(self):
        # Parse value rule
        self.value()

        # Return parse tree
        return self.root

    # Returns the next token read from the input file
    def get_next_token(self):
        line = self.lexer_file.readline()
        return line.replace('<', '').replace('>', '').strip()

    # Parse the Value: Dict | List | String | Number | true | false | null grammar rule
    def value(self):
        if self.root is None:
            self.root = JSONNode("VALUE")
            self.current_node = self.root

            # Read a token from the file
            processed_string = self.get_next_token()

            # Raise exception if the JSON file does not start with brackets
            if processed_string != "{" and processed_string != "[":
                raise Exception("JSON file does not begin with { or [")
        else:
            new_node = JSONNode("VALUE", None, self.current_node)
            self.current_node.add_child(new_node)
            self.current_node = new_node

            # Read a token from the file
            processed_string = self.get_next_token()

        # Call on the object or list parsers depending upon what the starting brackets is
        if processed_string == "{":
            self.dict()
        elif processed_string == "[":
            self.list()

        # Call the String, integer, boolean or null parsers
        elif processed_string.startswith("STR, "):
            self.string(processed_string)
            self.current_node = self.current_node.parent
        elif processed_string.startswith("INT, "):
            self.number(processed_string)
            self.current_node = self.current_node.parent
        elif processed_string.startswith("BOOL, "):
            self.boolean(processed_string)
            self.current_node = self.current_node.parent
        elif processed_string == "NULL":
            self.null()
            self.current_node = self.current_node.parent

    # Parse the Dict:- { Pair (, Pair)* } grammar rule
    def dict(self):
        new_node = JSONNode("DICT", None, self.current_node)
        self.current_node.add_child(new_node)
        self.current_node = new_node

        # Show opening braces
        opening_braces = JSONNode("{", None, self.current_node)
        self.current_node.add_child(opening_braces)
        self.current_node = opening_braces

        # Parse first pair
        self.pair()

        # Handle (, Pair)*
        next_token = self.get_next_token()
        while next_token != "}":
            # Call the Pair parser
            if next_token == ",":
                self.pair()

            # If the closing bracket is incorrect, indicate it and continue parsing
            elif next_token in [')', ']']:
                print(f"Invalid Closing Brace: {next_token}. Continuing program...")
                break

            #If pairs are not seperated by commas, raise exception and stop parsing
            elif next_token != ",":
                raise Exception("Pairs must be seperated by comma")
            next_token = self.get_next_token()

        # Show closing braces
        closing_braces = JSONNode("}", None, self.current_node)

        #Ensure that the closing braces is indented the same as the opening braces
        self.current_node = opening_braces.parent
        self.current_node.add_child(closing_braces)

        # Set current node to the parent node as the dict has been fully parsed
        self.current_node = new_node.parent

    # Parse the List:- [ Value (, Value)* ] grammar rule
    def list(self):
        new_node = JSONNode("LIST", None, self.current_node)
        self.current_node.add_child(new_node)
        self.current_node = new_node

        # Show opening braces
        opening_braces = JSONNode("[", None, self.current_node)
        self.current_node.add_child(opening_braces)
        self.current_node = opening_braces

        # Parse first value
        self.value()

        # Handle (, Value)*
        next_token = self.get_next_token()
        while next_token != "]":

            # Call the value parser for each value in list
            if next_token == ",":
                new_node = JSONNode(",")
                self.current_node.add_child(new_node)
                self.value()

            # If the closing bracket is incorrect, indicate that and continue the program
            elif next_token in [')', '}']:
                print(f"Invalid Closing Brace: {next_token}. Continuing program...")
                break

            # Ensure that each Value is seperated by a comma
            elif next_token != ",":
                raise Exception("Missing Token: Array elements must be seperated by comma")
            next_token = self.get_next_token()

        # Show closing braces
        closing_braces = JSONNode("]", None, self.current_node)

        # Ensure that the closing braces is indented the same amount as the closing braces
        self.current_node = opening_braces.parent
        self.current_node.add_child(closing_braces)

        # Set current node to the parent as the array has been fully parsed
        self.current_node = new_node.parent

    # Parse the Pair:- String ":" Value grammar rule
    def pair(self):
        new_node = JSONNode("PAIR", None, self.current_node)
        self.current_node.add_child(new_node)
        self.current_node = new_node
        parent_node = self.current_node.parent
        processed_string = self.get_next_token()

        # Parse the key
        self.string(processed_string)

        # Parse the value
        processed_string = self.get_next_token()

        # Validate if there is a colon after the key
        if processed_string == ":":
            new_inner_node = JSONNode(":")
            self.current_node.add_child(new_inner_node)
            self.value()
        elif processed_string != ":":
            raise Exception("Missing Token: Pair does not have a colon separating the key and value")

        self.current_node = parent_node

    # Parse the Value:- String grammar rule
    def string(self, processed_string):
        value = processed_string.replace("STR, ", "").replace('"', '')
        new_node = JSONNode("STRING", value, self.current_node)
        self.current_node.add_child(new_node)

    # Parse the Value:- Number grammar rule
    def number(self, processed_string):
        value = processed_string.replace("INT, ", "")
        new_node = JSONNode("NUMBER", value, self.current_node)
        self.current_node.add_child(new_node)

    # Parse the Value:- Boolean grammar rule
    def boolean(self, processed_string):
        value = processed_string.replace("BOOL, ", "")
        new_node = JSONNode("BOOL", value, self.current_node)
        self.current_node.add_child(new_node)

    # Parse the Value:- null grammar rule
    def null(self):
        new_node = JSONNode("NULL", None, self.current_node)
        self.current_node.add_child(new_node)

# Start parsing
if __name__ == "__main__":
    # Specify input file here
    input_file = "Lexer/test1.txt"
    lexer = open(input_file, "r")

    parser = Parser(lexer)
    tree = parser.parse()

    # Specify output file here (in both the open() function and the print_tree() function) if needed, otherwise please leave as ""
    output_file = "Lexer/output.txt"
    file = None
    if output_file != "":
        file = open(output_file, "w")
        tree.print_tree(file)
    else:
        tree.print_tree()

    lexer.close()