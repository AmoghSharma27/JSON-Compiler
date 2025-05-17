# **Lexer for JSON**
**By:** Amogh Sharma

**_Assumptions Made_**  
This code assumes that the input contains tokens that follow the JSON alphabet and
are lexically correct. It also assumes that each token in the input is enclosed by 
angular braces.

**_Error Handling in Code_**  
For errors like having the wrong closing braces, the code indicates the error to the
user and continues parsing like normal, and replaces the incorrect braces with the 
correct ones in the output. 

For errors like a missing comma or colon in arrays and pairs respectively, the program
raises an Exception and stops the parsing.

Errors are printed at the top of the printed parse tree

**_How to Run Code_**   
To run the code, simply write the name of the txt file that is required to be parsed
for the input_file variable in the main method of the parser.py file, replacing the filename is already in the function. 
A test file's name has already been typed in. 

If you need the output to also be written to a file, please specify the output file's name
in the output_file variable. Otherwise, you can leave the output_file variable blank.

I have indicated where
to give the file name in the program as well. Please use that as reference.

**_Output_**  
The program outputs the parse tree resulting from parsing the input from a file
to the console. It also writes the output to an output file only if 
the output file is provided as given above and in the program.