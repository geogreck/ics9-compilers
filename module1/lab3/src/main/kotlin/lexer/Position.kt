package lexer

import java.util.NoSuchElementException

class Position(
    var program: String
) : Iterable<Char>, Cloneable {
    var line: Int = 1
    var pos: Int = 1
    var index: Int = 0

    public override fun clone(): Position {
        return Position(program, line, pos, index)
    }
    constructor(program: String, line: Int, pos: Int, index: Int) : this(program) {
        this.line = line
        this.pos = pos
        this.index = index
    }

    fun cp(): Char {
        if (index == program.length) {
            return EOF
        }
        return program[index]
    }

    fun isLetter(): Boolean {
        return cp().isLetter()
    }

    fun isDigit(): Boolean {
        return cp().isDigit()
    }

    fun isLetterOrDigit(): Boolean {
        return cp().isLetterOrDigit()
    }

    fun isWhitespace(): Boolean {
        return cp().isWhitespace()
    }

    fun isNewLine(): Boolean {
        return cp() == '\n'
    }

    fun next(): Char {
        if (index == program.length) {
            return EOF
        }

        if (isNewLine()) {
            line++
            pos = 1
        } else {
            pos++
        }
        index++

        return cp()
    }

    override fun iterator(): Iterator<Char> {
        return object : Iterator<Char> {
            override fun hasNext(): Boolean {
                return index < program.length - 1
            }

            override fun next(): Char {
                if (!hasNext()) throw NoSuchElementException()

                return next()
            }
        }
    }

    override fun toString(): String {
        return "($line, $pos)"
    }
}