package lexer.tokens

import lexer.Fragment

class EOPToken(coords: Fragment) : Token(TokenDomain.ENDOFPROGRAM, coords) {}
