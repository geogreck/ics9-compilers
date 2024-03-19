%{

#include "lexer.hpp"

#define yyterminate() return TokenDomain::END_OF_PROGRAM

#define YY_USER_ACTION ParseCoords(yylloc);

%}

%option c++
%option debug
%option noyywrap

WHITESPACE   [ \t\r\n]
LETTER       [a-zA-Z]
DIGIT        [0-9]
IDENT        {LETTER}({LETTER}|{DIGIT}|$)*
HEX_DIGIT    [0-9A-F]
NUMBER       {DIGIT}+|${HEX_DIGIT}+

%x STRING_1

%%

{WHITESPACE}+           /* pass */

{IDENT}                 { return ProcessIdent(yylval); }

{NUMBER}                { return ProcessInt(yylval); }

\"                      { BEGIN(STRING_1); continued = 1; }

<STRING_1>\"\"          { continued = 1; std::string buf = ""; try { buf = std::get<std::string>(yylval);  } catch (const std::bad_variant_access& ex) {} yylval = buf + yytext[0];}

<STRING_1>\n            { compiler->AddMessage(yylloc.starting, Message(true, "newline in string constant")); BEGIN(0); }

<STRING_1><<EOF>>       { compiler->AddMessage(yylloc.starting, Message(true, "EOF in string constant")); BEGIN(0); }

<STRING_1>\\\n          { continued = 1; }

<STRING_1>\"            { BEGIN(0); return ProcessString(yylval); }

<STRING_1>.             { continued = 1; std::string buf = ""; try { buf = std::get<std::string>(yylval);  } catch (const std::bad_variant_access& ex) {} yylval = buf + yytext[0];}

.                       { compiler->AddMessage(yylloc.starting, Message(true, "invalid syntax")); }

%%

// "

TokenDomain Scanner::ProcessString(Attribute &yylval)
{
    return TokenDomain::STRING;
}

TokenDomain Scanner::ProcessInt(Attribute &yylval)
{
  if (yytext[0] != '$')
  {
    yylval = std::atoi(yytext);
  } else {
    yytext = yytext + 1;
    yylval = std::stoi(yytext, 0, 16);
  }
  return TokenDomain::INT;
}

TokenDomain Scanner::ProcessIdent(Attribute &yylval)
{
    yylval = compiler->AddName(yytext);

    return TokenDomain::IDENT;
}

#ifdef yylex
#undef yylex
#endif

int yyFlexLexer::yylex() {
  return 0;
}


