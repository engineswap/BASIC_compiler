from enum import Enum

# Contains original text and type of token
class Token:
	def __init__(self, tokenText:str, tokenKind:Enum):
		self.text = tokenText
		self.kind = tokenKind

	@staticmethod
	def isKeyword(text:str) -> bool:
		try:
			enum = TokenType[text]
			return True
		except Exception as e:
			return False
	
# Enum for token type
class TokenType(Enum):
	EOF = -1
	NEWLINE = 0
	NUMBER = 1
	INDENT = 2
	STRING = 3
	# Keywords
	LABEL = 101
	GOTO = 102
	PRINT = 103
	INPUT = 104
	LET = 105
	IF = 106
	THEN = 107
	ENDIF = 108
	WHILE = 109
	REPEAT = 110
	ENDWHILE = 111
	# Operators
	EQ = 201
	PLUS = 202
	MINUS = 203
	ASTERISK = 204
	SLASH = 205
	EQEQ = 206
	NOTEQ = 207
	LT = 208
	LTEQ = 209
	GT = 210
	GTEQ = 211



