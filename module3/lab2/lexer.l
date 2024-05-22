%{
#include "lexer.h"
#include "parser.tab.h"

#define YY_USER_ACTION \
  { \
    int i; \
    struct Extra *extra = yyextra; \
    if (! extra->continued ) { \
      yylloc->first_line = extra->cur_line; \
      yylloc->first_column = extra->cur_column; \
    } \
    extra->continued = false; \
    for (i = 0; i < yyleng; ++i) { \
      if (yytext[i] == '\n') { \
        extra->cur_line += 1; \
        extra->cur_column = 1; \
      } else { \
        extra->cur_column += 1; \
      } \
    } \
    yylloc->last_line = extra->cur_line; \
    yylloc->last_column = extra->cur_column; \
  }

void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], int tab_count, const char *message) {
    printf("Error (%d,%d): %s\n", loc->first_line, loc->first_column, message);
}

%}

%option reentrant noyywrap bison-bridge bison-locations
%option extra-type="struct Extra *"
WHITESPACE   [ \t\r\n]
UPPERCASE    [A-Z]
LOWERCASE    [a-z]
DIGIT        [0-9]
LETTER       [A-Za-z]
NONTERMINAL  {LETTER}({LETTER}|{DIGIT})*
STRING       (\".*\"|\$QUOT|\$[A-Z]+|\$\{[0-9A-F]+\})*
BOOLEAN      T|F
CHAR         ('#[A-Z]+')|('#\{[0-9A-F]+\}')|('.')
INTEGER      [0-9]+|\{[0-9]+\}[0-9A-Z]+
IDENT        [a-zA-Z][a-zA-Z0-9_]*

%%

{WHITESPACE}            /* pass */
define                  { return KW_DEFINE; }
\(                      { return L_PARENTHESIS; }
\)                      { return R_PARENTHESIS; }
,                       { return COMMA; }
end                     { return KW_END; }
;                       { return SEMICOLON; }
:=                      { return OP_ASSIGN; }
\[                      { return L_SQUARE; }
\]                      { return R_SQUARE; }
if                      { return KW_IF; }
then                    { return KW_THEN; }
else                    { return KW_ELSE; }
elseif                  { return KW_ELSEIF; }
while                   { return KW_WHILE; }
do                      { return KW_DO; }
to                      { return KW_TO; }
step                    { return KW_STEP; }
until                   { return KW_UNTIL; }
return                  { return KW_RETURN; }
assert                  { return KW_ASSERT; }
or                      { return OP_OR; }
xor                     { return OP_XOR; }
and                     { return OP_AND; }
=                       { return OP_EQ; }
\<\>                      { return OP_NEQ; }
\<                       { return OP_LT; }
\>                       { return OP_GT; }
\<\=                      { return OP_LTE; }
\>\=                      { return OP_GTE; }
\+                       { return OP_PLUS; }
-                       { return OP_MINUS; }
\*                       { return OP_MULT; }
\/                       { return OP_DIV; }
mod                       { return OP_MOD; }
\*\*                      {return OP_FACTOR; }
not                       { return OP_NOT; }
new                       { return KW_NEW; }
array                       { return KW_ARRAY; }
int                       { return KW_INT; }
char                       { return KW_CHAR; }
bool                       { return KW_BOOL; }

{STRING}               { yylval->string = yytext; return STRING_CONST; }
{INTEGER}                  { yylval->number = atoi(yytext); return INT_CONST; }
{CHAR}                 { yylval->string = yytext; return CHAR_CONST; }
{IDENT}                { yylval->ident = yytext; return IDENT; }
%%

void init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra) {
    extra->continued = false;
    extra->cur_line = 1;
    extra->cur_column = 1;

    yylex_init(scanner);
    yylex_init_extra(extra, scanner);
    yyset_in(input, *scanner);
}

void destroy_scanner(yyscan_t scanner) {
    yylex_destroy(scanner);
}
