# **Scanner for JSON**
**By:** Amogh Sharma

**_Assumptions Made_**              
The main assumption made by me in the code is that the syntax of the input JSON script
is valid as my code does not check for syntax errors. Otherwise, the code correctly tokenizes
all JSON datatypes.

**_Explanation of Key Parts of Code_**    
The main classes in the code are the TokenType, Token, LexerError and LexerDFA. Their
main functions in brief are as follows:       

*TokenType:* This class lists the different JSON datatypes that can be input to the scanner    

*Token:* This method returns the string representation of each token within angular
brackets which is then output to the console after the LexerDFA finishes running.

*LexerError:* This class is used to output an error message every time the LexerDFA
detects a Lexical Error in the given token stream. It outputs the position as well as
the character that caused the error.

*LexerDFA:* This class contains the main functionality of the scanner. It is implemented
like a DFA and has different behaviours according to the characters read. It recognizes
and returns the tokenized versions of the input characters according to the JSON language.

**_How to Run Code_**                                                            
To run the code, simply type the name of the file containing the JSON script in the
open() function at line 240 of the code. A file's name has already been input into
the function as a test file (input_test1.txt).   
The code will output the tokenized versions of the JSON scripts by printing them to the terminal.
If there are any lexical errors, it would print those errors and stop tokenization.