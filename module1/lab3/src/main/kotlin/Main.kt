import lexer.Compiler
import lexer.Position
import lexer.Scanner
import lexer.tokens.Token
import lexer.tokens.TokenDomain
import java.io.File

fun main(args: Array<String>) {
    if (args.size != 1) {
        error("filename must be passed")
    }
    val filename = args[0]
    val lines: String = File(filename).readText(Charsets.UTF_8)
    println(lines)
    val compiler = Compiler()
    val scanner = Scanner(compiler, lines, Position(lines))
    var token: Token
    while (scanner.nextToken().also { token = it }.domain != TokenDomain.ENDOFPROGRAM) {
        println(token)
    }
    println("comments: ${scanner.comments}")
    println("messages: ${compiler.messages}")
}