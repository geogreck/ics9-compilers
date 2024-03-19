#include "lexer.hpp"

void Compiler::AddMessage(const Position &position, Message message)
{
    messages[position] = message;
}

int Compiler::AddName(const std::string &name)
{
    if (nameCodes.find(name) == nameCodes.end())
    {
        nameCodes[name] = names.size() + 1;
        names.push_back(name);
        return names.size();
    }
    return GetCode(name);
}

int Compiler::GetCode(const std::string &name)
{
    return nameCodes.at(name);
}

void Scanner::ParseCoords(Fragment &yylloc)
{

    if (!continued) {
        yylloc.starting = cur;
    }
    continued = 0;

    for (std::size_t i = 0; i < yyleng; ++i)
    {
        if (yytext[i] == '\n')
        {
            ++cur.line;
            cur.pos = 1;
        }
        else
        {
            ++cur.pos;
        }

        ++cur.index;
    }

    yylloc.following = cur;
}

std::ostream &operator<<(std::ostream &os, const Position &position)
{
    os << '(' << position.line << ", " << position.pos << ")";
    return os;
}

std::ostream &operator<<(std::ostream &os, const Fragment &fragment)
{
    os << fragment.starting << "-" << fragment.following;
    return os;
}

std::ostream &operator<<(std::ostream &os, const TokenDomain &domain)
{
    switch (domain)
    {
    case TokenDomain::STRING:
        os << "STRING";
        break;
    case TokenDomain::INT:
        os << "INT";
        break;
    case TokenDomain::IDENT:
        os << "IDENT";
        break;
    case TokenDomain::END_OF_PROGRAM:
        os << "EOP";
        break;
    }
    return os;
}

std::ostream &operator<<(std::ostream &os, const Token &token)
{
    os << token.domain << " " << token.coords;

    switch (token.domain)
    {
    case TokenDomain::STRING:
    {
        const auto &str_token = static_cast<const StringToken &>(token);
        os << ": " << str_token.attr;
        break;
    }
    case TokenDomain::INT:
    {
        const auto &int_token = static_cast<const IntToken &>(token);
        os << ": " << int_token.attr;
        break;
    }
    case TokenDomain::IDENT:
    {
        const auto &ident_token = static_cast<const IdentToken &>(token);
        os << ": " << ident_token.attr;
        break;
    }
    default:
        break;
    }

    return os;
}

std::ostream &operator<<(std::ostream &os, const Message &message)
{
    if (message.isErr)
    {
        os << "ERROR: " << message.text;
        return os;
    }
    os << "INFO: " << message.text;
    return os;
}

Scanner::Scanner(std::shared_ptr<Compiler> compiler, std::istream &sin) : compiler(compiler), yyFlexLexer(sin, std::cout) {}
