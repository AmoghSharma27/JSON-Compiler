# Author: Amogh Sharma

class JSONNode:
    def __init__(self, label, value=None, parent=None):
        self.label = label  # 'list', 'value', 'STRING'
        self.value = value  # "abc" for a STRING node
        self.children = []  # List of further JSONNode objects
        self.parent = parent  # The parent node of this JSONNode

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, depth=0):
        indent = "  " * depth

        # Print the node label and value (if available)
        if self.value is not None:
            print(f"{indent}{self.label}: {self.value}")
        else:
            print(f"{indent}{self.label}")

        # Print out all indented child nodes
        for child in self.children:
            child.print_tree(depth + 1)


class Parser:
    def __init__(self, lexer_file):
        self.lexer_file = lexer_file
        self.current_node = None
        self.root = None
        self.semantic_errors = []

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

    # Parse the Value: Dict | List | String | Number | true | false | null rule
    def value(self):
        if self.root is None:
            self.root = JSONNode("VALUE")
            self.current_node = self.root

            # Read a token from the file
            processed_string = self.get_next_token()

        else:
            # Read a token from the file
            processed_string = self.get_next_token()

        # Call on the object or array parsers depending upon what the starting brackets is
        if processed_string == "{":
            self.dict()
        elif processed_string == "[":
            self.list()
        elif processed_string.startswith("STR, "):
            self.string(processed_string)
        elif processed_string.startswith("INT, "):
            self.number(processed_string)
        elif processed_string.startswith("BOOL, "):
            self.boolean(processed_string)
        elif processed_string == "NULL":
            self.null()

    # Parse the Dict:- { Pair (, Pair)* } rule
    def dict(self):
        new_node = JSONNode("DICT", None, self.current_node)
        self.current_node.add_child(new_node)
        self.current_node = new_node
        dict_pointer = new_node

        # Parse first pair
        self.pair()

        # Handle (, Pair)*
        next_token = self.get_next_token()
        while next_token != "}":
            if next_token == ",":
                self.pair()
            next_token = self.get_next_token()

        # Set current node to the parent node as the dict has been fully parsed
        self.current_node = new_node.parent

        # Level A error: Check if there are duplicate keys in the dictionary
        self.check_duplicate_keys(dict_pointer)

    # Parse the LIST:- [ Value (, Value)* ] rule
    def list(self):
        new_node = JSONNode("LIST", None, self.current_node)
        self.current_node.add_child(new_node)
        self.current_node = new_node
        array_pointer = new_node

        # Parse first value
        self.value()

        # Handle (, Value)*
        next_token = self.get_next_token()
        while next_token != "]":

            # Ensure that each Value is seperated by a comma
            if next_token != ",":
                raise Exception("Missing Token: Commas must be present between values")
            self.value()
            next_token = self.get_next_token()

        # Set current node to the parent as the array has been fully parsed
        self.current_node = new_node.parent

    # Parse the Pair:- String ":" Value
    def pair(self):
        new_node = JSONNode("PAIR", None, self.current_node)
        self.current_node.add_child(new_node)
        self.current_node = new_node
        parent_node = self.current_node.parent
        processed_string = self.get_next_token()

        # Level C Type 2 error: Check if the key of the pair is empty
        if processed_string == "STR, \"\"":
            self.semantic_errors.append("Error Type 2 at " + processed_string + ": The key in a key-value pair cannot be empty.")

        # Level B Type 4 error: Check if Reserved keywords (true, false, null) are used as keys
        if processed_string == "STR, \"false\"" or processed_string == "STR, \"true\"" or processed_string == "STR, \"null\"":
            self.semantic_errors.append("Error Type 4 at " + processed_string +  ": The key in a key-value pair cannot be a reserved keyword (true, false or null).)")

        # Parse the key
        self.string(processed_string)

        # Parse the value
        processed_string = self.get_next_token()

        # Validate if there is a colon after the key
        if processed_string == ":":
            new_inner_node = JSONNode(":")
            self.current_node.add_child(new_inner_node)
            self.value()

        self.current_node = parent_node

    # Parse the Value:- String rule
    def string(self, processed_string):
        value = processed_string.replace("STR, ", "").replace('"', '')

        # Level A Type 7 error: Check if the string being used is a reserved keyword (true, false, null) as they are not allowed
        if value == "true" or value == "false" or value == "null":
            self.semantic_errors.append("Error Type 7 at " + value + ": Reserved keywords (true, false, null) cannot be used as strings anywhere.")

        new_node = JSONNode("STRING", value, self.current_node)
        self.current_node.add_child(new_node)

    # Parse the Value:- Number rule
    def number(self, processed_string):
        value = processed_string.replace("INT, ", "")

        # Level C Type 1 error: Check if the value does not have digits in front of or behind decimal points
        if value.startswith(".") or value.endswith("."):
            self.semantic_errors.append("Error Type 1 at " + value + ": Invalid Decimal Placement")

        # Level B Type 3 error: Check if there are leading zeros or leading +'s in front of decimal numbers
        if value.startswith("0") and not value.startswith("0."):
            self.semantic_errors.append("Error Type 3 at " + value + ": Leading Zeros")
        if (value.startswith("+") or "+" in value) and not "e+" in value:
            self.semantic_errors.append("Error Type 3 at " + value + ": Invalid Number")

        new_node = JSONNode("NUMBER", value, self.current_node)
        self.current_node.add_child(new_node)

    # Parse the Value:- Boolean rule
    def boolean(self, processed_string):
        value = processed_string.replace("BOOL, ", "")
        new_node = JSONNode("BOOL", value, self.current_node)
        self.current_node.add_child(new_node)

    # Parse the Value:- Null rule
    def null(self):
        new_node = JSONNode("NULL", None, self.current_node)
        self.current_node.add_child(new_node)

    # Function to detect duplicate keys in a given dictionary
    def check_duplicate_keys(self, dict_pointer):
        # Counter for the number of key-value pairs in the dict
        counter = 0

        # Hashset for checking duplicates
        check_set = set()

        for pair in dict_pointer.children:
            if len(pair.children) >= 1:
                counter += 1
                check_set.add(pair.children[0].value)

        # If hashset does not have all distinct values, there is a duplicate key
        if len(check_set) < counter:
            self.semantic_errors.append("Error Type 5 at " + dict_pointer.label + ": Duplicate Keys in Dictionary")

if __name__ == "__main__":
    lexer = open("Parser/input_error_type7.txt", "r")
    parser = Parser(lexer)
    tree = parser.parse()

    # If there are semantic errors in the file, print out the semantic errors and store them in a txt file
    # Otherwise, print out the Abstract Syntax Tree for the input
    if len(parser.semantic_errors) == 0:
        tree.print_tree()
    else:
        error_file = open("Parser/semantic_error1.txt", "w")
        for error in parser.semantic_errors:
            error_file.write(error)
            print(error)
    lexer.close()