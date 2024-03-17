package lexer

import lexer.tokens.*

class Scanner(
    private val compiler: Compiler,
    val program: String,
    val cur: Position,
) {
    var comments: List<Fragment> = listOf()


    fun nextToken(): Token {
        while (cur.cp() != EOF) {
            while (cur.isWhitespace()) {
                cur.next()
            }

            val start = cur.clone();

            when (cur.cp()) {
                '/' -> {
                    if (cur.next() != '*') {
                        compiler.addMessage("bad comment", true, start.clone())
                        return nextToken()
                    }
                    while (cur.cp() == '*' && cur.cp() != EOF) {
                        cur.next()
                    }
                    while (cur.cp() != '*' && cur.cp() != EOF) {
                        cur.next()
                    }
                    while (cur.cp() == '*' && cur.cp() != EOF) {
                        cur.next()
                    }
                    if (cur.cp() == EOF) {
                        compiler.addMessage("bad comment end of file", true, cur.clone())
                        return EOPToken(Fragment(cur, cur))
                    }
                    if (cur.cp() != '/') {
                        compiler.addMessage("bad comment unclosed", true, cur.clone())

                        return nextToken()
                    }
                    comments += Fragment(start.clone(), cur.clone())
                    cur.next()
                    return nextToken()
                }

                else -> {
                    if (!cur.isLetterOrDigit()) {
                        compiler.addMessage("bad syntax", true, cur.clone())
                        cur.next()
                        return nextToken()
                    }
                    var word = ""
                    while (cur.isLetterOrDigit()) {
                        word += cur.cp()
                        cur.next()
                    }
                    if (!cur.isWhitespace() && cur.cp() != EOF) {
                        compiler.addMessage("very bad syntax", true, cur.clone())
                        while (!cur.isWhitespace()) cur.next()
                        return nextToken()

                    }
                    when (word) {
                        "for" -> {
                            val token =  ForToken(Fragment(start.clone(), Position(cur.program, cur.line, cur.pos-1, cur.index)))
                            cur.next()
                            return token
                        }
                        "if" -> {
                            val token =  IfToken(Fragment(start.clone(), Position(cur.program, cur.line, cur.pos-1, cur.index)))
                            cur.next()
                            return token
                        }
                        "m1" -> {
                            val token =  M1Token(Fragment(start.clone(), Position(cur.program, cur.line, cur.pos-1, cur.index)))
                            cur.next()
                            return token
                        }
                        else -> {
                            if (!IdentToken.validate(word)) {
                                compiler.addMessage("bad ident syntax", true, start.clone())
                                cur.next()
                                return nextToken()
                            }
                            val id = compiler.addName(word)
                            val token = IdentToken(Fragment(start.clone(), cur.clone()), id)
                            cur.next()
                            return token
                        }
                    }
                }
            }
        }
        return EOPToken(Fragment(cur, cur))
    }


}
