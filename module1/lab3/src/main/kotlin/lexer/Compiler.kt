package lexer

class Compiler() {
    val nameCodes: NameDictionary = NameDictionary()
    val messages: HashMap<Position, Message> = HashMap()

    fun addName(s: String): Int {
        return nameCodes.addName(s)
    }

    fun getName(code: Int) {
        nameCodes.getName(code)
    }

    fun addMessage(s: String, isErr: Boolean, position: Position) {
        messages[position] = Message(isErr, s)
    }
}