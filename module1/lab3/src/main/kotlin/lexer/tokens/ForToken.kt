package lexer.tokens

import lexer.Fragment

class ForToken(coords: Fragment) : Token(TokenDomain.FOR, coords) {}
