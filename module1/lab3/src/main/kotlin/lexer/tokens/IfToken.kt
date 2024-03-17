package lexer.tokens

import lexer.Fragment

class IfToken(coords: Fragment) : Token(TokenDomain.IF, coords) {}
