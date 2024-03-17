package lexer

class Message(
    val isErr: Boolean,
    val text: String,
) {
    override fun toString(): String {
        if (isErr) {
            return "ERROR: $text"
        }
        return "INFO: $text"
    }
}