package lexer.tokens

import lexer.Fragment

class IdentToken(coords: Fragment, val attr: Int) : Token(TokenDomain.IDENT, coords) {
    override fun toString(): String {
        return super.toString() + ": $attr"
    }

    companion object {
        fun validate(s: String): Boolean {
            var wasDigit = s[0].isDigit()
            for (letter in s.drop(1)) {
                if (letter.isDigit()) {
                    if (wasDigit) {
                        return false
                    }
                    wasDigit = true
                } else {
                    if (!wasDigit) {
                        return false
                    }
                    wasDigit = false
                }
            }
            return true
        }
    }
}
