from lexer import *

if __name__=="__main__":
	source_code = "IF+-123 foo*THEN/"
	lexer = Lexer(source_code)

	token = lexer.getToken()
	while token.kind != TokenType.EOF:
		print(token.kind, token.text)
		token = lexer.getToken()
	