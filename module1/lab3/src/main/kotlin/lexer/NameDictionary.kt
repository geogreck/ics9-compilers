package lexer

class NameDictionary {
    private var namesCodes: HashMap<String, Int> = HashMap();
    private var names: List<String> = listOf();

    fun addName(s: String): Int {
        if (!contains(s)) {
            namesCodes[s] = namesCodes.size+1
            names += s
            return namesCodes.size
        }
        return getCode(s)!!
    }

    fun contains(s: String): Boolean {
        return namesCodes.containsKey(s)
    }

    fun getCode(s: String): Int? {
        return namesCodes.get(s)
    }

    fun getName(code: Int): String {
        return names.get(code)
    }
}