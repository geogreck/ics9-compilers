package lexer

class Fragment(
    starting: Position,
    following: Position,
) {
    private val starting = starting
        get() = field
    private val following = following
        get() = field

    override fun toString(): String {
        return "$starting-$following"
    }
}