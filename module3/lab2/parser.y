%{
#include <stdio.h>
#include "lexer.h"
%}

%define api.pure
%locations
%lex-param {yyscan_t scanner}  /* параметр для yylex() */
/* параметры для yyparse() */
%parse-param {yyscan_t scanner}
%parse-param {long env[26]}
%parse-param {int tab_count}

%union {
    long number;
    char* string;
    char* ident;
    char char_cnst;
    bool bool_cnst;
}

%left OP_EQ OP_NEQ OP_LT OP_GTE OP_PLUS OP_MINUS
%left OP_MULT OP_DIV OP_MOD OP_GT OP_LTE

%right OP_OR OP_XOR OP_AND

%right OP_FACTOR OP_NOT OP_ASSIGN


%token KW_DEFINE L_PARENTHESIS R_PARENTHESIS COMMA KW_END
%token SEMICOLON L_SQUARE R_SQUARE KW_IF KW_THEN KW_ELSE
%token KW_ELSEIF KW_WHILE KW_DO KW_TO KW_STEP KW_UNTIL
%token KW_RETURN KW_ASSERT KW_NEW KW_ARRAY KW_INT KW_CHAR KW_BOOL

%token <number> INT_CONST
%token <ident> IDENT
%token <string> STRING_CONST
%token <char_cnst> CHAR_CONST
%token <bool_cnst> BOOL_CONST

%{
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], int tab_count, const char *message);
%}

%{
void tabulate(int tab_count) {
    for(int i = 0; i < tab_count; i++) {
        printf("  ");
    }
}


%}

%%
Program:
    Funcs { printf("\033[2A"); }
    ;

Funcs:
     Func { printf("\n\n"); } Funcs
     |
    ;

Func:
    {tabulate(tab_count);} FuncHeader FuncBody
    ;

FuncHeader:
    {tabulate(tab_count);} KW_DEFINE { printf("define "); } FuncHeader1
    ;

FuncHeader1:
    Type IDENT { printf(" %s", $2); } FuncParams
    | IDENT { printf(" %s", $1); } FuncParams
    ;

FuncParams:
    L_PARENTHESIS { printf("("); } FuncConstructors R_PARENTHESIS { printf(")\n"); }
    ;

FuncConstructors:
    FuncConstructor FuncConstructors1
    | /* empty */
    ;

FuncConstructors1:
    COMMA { printf(", "); } FuncConstructor FuncConstructors1
    | /* empty */
    ;

FuncConstructor:
    Type IDENT { printf(" %s", $2); }
    ;

FuncBody:
    {tab_count +=1;}  Operators {tab_count -=1;} KW_END SEMICOLON { tabulate(tab_count); printf("end;\n"); }
    ;

Operators:
    {tabulate(tab_count);} Operator SEMICOLON { printf(";\n"); } Operators
    | /* empty */
    ;

Operator:
    DeclOperator
    | AssignFuncCallOperator
    | PreConditionLoop
    | PostConditionLoop
    | ReturnOperator
    | AssertOperator
    | CondOperator
    ;

DeclOperator:
    Type DeclOperator1
    ;

DeclOperator1:
    IDENT  { printf(" %s", $1); } OP_ASSIGN  { printf(" := "); } Expr
    ;

AssignFuncCallOperator:
    IDENT { printf("%s", $1); } AssignFuncCallOperator1
    ;

AssignFuncCallOperator1:
    AssignOperator1
    | FuncCallOperator1
    ;

AssignOperator:
    AssignExpr AssignOperator1
    ;

AssignOperator1:
    OP_ASSIGN { printf(" := "); } Expr
    ;

AssignExpr:
    IDENT  { printf(" %s", $1); }
    | ArrvalShort
    ;

ArrvalShort:
    L_SQUARE { printf("["); } Expr R_SQUARE { printf("]"); }
    | /* empty */

FuncCallOperator:
    IDENT  { printf(" %s", $1); }
    ;

FuncCallOperator1:
    L_PARENTHESIS { printf("("); } Params R_PARENTHESIS { printf(")"); };

Params:
    Expr Params1
    ;

Params1:
    COMMA Expr Params1
    | /* empty */

CondOperator:
    KW_IF { printf("if "); } Expr KW_THEN { printf(" then\n"); } {tab_count +=1;}  Operators {tab_count -=1;} CompBranches CondOperator1
    ;

CondOperator1:
    KW_END { tabulate(tab_count); printf("end"); }
    | KW_ELSE { printf("else"); } {tab_count +=1;}  Operators {tab_count -=1;} KW_END { tabulate(tab_count); printf("end"); }
    ;

CompBranches:
    KW_ELSEIF { printf("elseif"); } Operators CompBranches
    | /* empty */
    ;

PreConditionLoop:
    KW_WHILE { printf("while "); } Expr KW_DO { printf(" do\n"); } {tab_count +=1;}  Operators {tab_count -=1;} KW_END { tabulate(tab_count); printf("end"); }
    ;

PreConditionLoop1:
    IDENT { printf("%s", $1); } KW_TO { printf(" to "); } Expr LoopStep KW_DO { printf(" do\n"); } {tab_count +=1;}  Operators {tab_count -=1;} KW_END { tabulate(tab_count); printf("end"); }
    | /* empty */
    ;

LoopStep:
    KW_STEP { printf(" step "); } Expr
    | /* empty */

PostConditionLoop:
    KW_DO { printf("do\n"); } {tab_count +=1;}  Operators {tab_count -=1;} KW_UNTIL { tabulate(tab_count); printf("until "); } Expr
    ;

ReturnOperator:
    KW_RETURN Expr
    ;

AssertOperator:
    KW_ASSERT { printf("assert "); } Expr
    ;

Expr:
    LogCompExpr Expr1
    ;

Expr1:
    LogCompOp LogCompExpr
    | /* empty */
    ;

LogCompOp:
    OP_OR
    | OP_XOR
    ;

LogCompExpr:
    LogExpr LogCompExpr1
    ;

LogCompExpr1:
    LogOp LogExpr LogCompExpr1
    | /* empty */
    ;

LogOp:
    OP_AND
    ;

LogExpr:
    CmpExpr LogExpr1
    ;

LogExpr1:
    CmpOp CmpExpr LogExpr1
    | /* empty */
    ;

CmpOp:
    OP_EQ
    | OP_NEQ
    | OP_LT
    | OP_GT
    | OP_LTE
    | OP_GTE
    ;

CmpExpr:
    ArithmExpr CmpExpr1
    ;

CmpExpr1:
    ArithmOp ArithmExpr CmpExpr1
    | /* empty */
    ;

ArithmOp:
    OP_PLUS  { printf(" + "); }
    | OP_MINUS { printf(" - "); }
    ;

ArithmExpr:
    MulExpr ArithmExpr1
    ;

ArithmExpr1:
    MulOp MulExpr ArithmExpr1
    | /* empty */
    ;

MulOp:
    OP_MULT
    | OP_DIV
    | OP_MOD
    ;

MulExpr:
    DegExpr MulExpr1
    ;

MulExpr1:
    DegOp MulExpr
    | /* empty */
    ;

DegOp:
    OP_FACTOR
    ;

DegExpr:
    UnaryExpr
    | UnaryOp UnaryExpr
    ;

UnaryOp:
    '-'
    | OP_NOT
    ;

UnaryExpr:
    IDENT  { printf("%s", $1); } ArrVal
    | NewExpr
    | Const
    ;

NewExpr:
    KW_NEW Type L_SQUARE { printf("["); } Expr R_SQUARE { printf("]"); }
    ;

ArrVal:
    L_SQUARE { printf("["); } Expr R_SQUARE { printf("]"); }
    | /* empty */
    ;

Const:
    INT_CONST  { printf("%ld", $1); }
    | STRING_CONST { printf("%s", $1); }
    | BOOL_CONST { printf("%d", $1); }
    | CHAR_CONST { printf("%d", $1); }
    ;

Type:
    Type KW_ARRAY { printf(" array"); }
    | Type1
    ;

Type1:
    KW_INT { printf("int"); }
    | KW_CHAR { printf("char"); }
    | KW_BOOL { printf("bool"); }
    ;


%%



int main(int argc, char *argv[]) {
    FILE *input = 0;
    long env[26] = { 0 };
    int tab_count = 0;
    bool user_tab = false;
    yyscan_t scanner;
    struct Extra extra;

    if (argc > 1) {
        printf("Read file %s\n", argv[1]);
        input = fopen(argv[1], "r");
    } else {
        printf("No file in command line, use stdin\n");
        input = stdin;
    }

    init_scanner(input, &scanner, &extra);
    yyparse(scanner, env, tab_count);
    destroy_scanner(scanner);

    if (input != stdin) {
        fclose(input);
    }

    return 0;
}

