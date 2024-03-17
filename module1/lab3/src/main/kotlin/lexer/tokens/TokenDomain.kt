package lexer.tokens

enum class TokenDomain(private val string: String) {
    IDENT("IDENT"),
    FOR("FOR"),
    IF("IF"),
    M1("M1"),
    ENDOFPROGRAM("ENDOFPROGRAM");

    override fun toString(): String {
        return this.string;
    }
}
