package lexer.tokens

import lexer.Fragment

open class Token(
    val domain: TokenDomain,
    val coords: Fragment,
) {
    var z: Int = 0

    override fun toString(): String {
        return "$domain $coords"
    }
}

