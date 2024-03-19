#pragma once

#include <string>
#include <ostream>
#include <map>
#include <vector>
#include <variant>
#include <memory>

#ifndef YY_DECLflexingLex
#define YY_DECL TokenDomain Scanner::lex(Attribute &yylval, Fragment &yylloc)
#endif

#ifndef yyFlexLexer
#include <FlexLexer.h>
#endif

class Position
{
public:
    int line = 1;
    int pos = 1;
    int index = 0;

    Position() {};

    Position(int line, int pos, int index) : line(line), pos(pos), index(index) {}
};

template <>
struct std::less<Position> {
  bool operator()(const Position& lhs, const Position& rhs) const {
    return lhs.index < rhs.index;
  }
};

std::ostream &operator<<(std::ostream &os, const Position &position);

class Fragment
{
public:
    Position starting;
    Position following;

    Fragment() {};

    Fragment(const Position &starting, const Position &following) : starting(starting), following(following) {}
};

std::ostream &operator<<(std::ostream &os, const Fragment &fragment);

enum class TokenDomain
{
    STRING,
    INT,
    IDENT,
    END_OF_PROGRAM,
};

std::ostream &operator<<(std::ostream &os, const TokenDomain &domain);

class Token
{
public:
    Token(const TokenDomain domain, const Fragment &coords) : domain(domain), coords(coords) {}

    virtual ~Token() {}

    TokenDomain domain;
    Fragment coords;
};

class StringToken : public Token
{
public:
    StringToken(const Fragment &coords, std::string attr) : Token(TokenDomain::STRING, coords), attr(attr) {}

    std::string attr;
};

class IntToken : public Token
{
public:
    IntToken(const Fragment &coords, int64_t attr) : Token(TokenDomain::INT, coords), attr(attr) {}

    int64_t attr;
};

class IdentToken : public Token
{
public:
    IdentToken(const Fragment &coords, int64_t attr) : Token(TokenDomain::IDENT, coords), attr(attr) {}

    int64_t attr;
};

std::ostream &operator<<(std::ostream &os, const Token &token);

class Message
{
public:
    bool isErr;
    std::string text;

    Message() {}

    Message(bool isErr, std::string text) : isErr(isErr), text(text) {}

    Message(const Message &message) : isErr(message.isErr), text(message.text) {}
};

std::ostream &operator<<(std::ostream &os, const Message &message);

class Compiler
{
public:
    std::map<Position, Message> messages;
    std::vector<std::string> names;
    std::map<std::string, int> nameCodes;

    void AddMessage(const Position &position, Message message);

    int AddName(const std::string &name);

    int GetCode(const std::string &name);
};

using Attribute = std::variant<int64_t, std::string>;

class Scanner : public yyFlexLexer
{
public:
    Position cur = Position(1, 1, 0);
    int continued = 0;

    Scanner(std::shared_ptr<Compiler> compiler, std::istream& sin);

    TokenDomain lex(Attribute &yylval, Fragment &yylloc);

    TokenDomain ProcessString(Attribute &yylval);

    TokenDomain ProcessInt(Attribute &yylval);

    TokenDomain ProcessIdent(Attribute &yylval);

    void ParseCoords(Fragment &yyloc);

    std::shared_ptr<Compiler> compiler;
};
