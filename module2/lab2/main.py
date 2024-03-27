import abc
import enum
import re
import sys
import typing
from dataclasses import dataclass

import parser_edsl as pe
from pprint import pprint


class Type(enum.Enum):
    Integer = 'INTEGER'
    Char = 'CHAR'
    Boolean = 'BOOLEAN'
    Void = 'VOID'


class Operator(abc.ABC):
    pass


@dataclass
class FuncConstructor:
    type: Type
    name: str


@dataclass
class FuncParam:
    func_contructors: list[FuncConstructor]


@dataclass
class FuncHeader:
    return_type: Type
    func_name: str
    func_params: list[FuncParam]


@dataclass
class FuncBody:
    operators: list[Operator]


@dataclass
class Function:
    header: FuncHeader
    body: FuncBody


@dataclass
class Program:
    funcs: list[Function]


@dataclass
class Expression(abc.ABC):
    pass


@dataclass
class DeclOperator(Operator):
    type: Type
    name: str
    expr: Expression


@dataclass
class AssignOperator(Operator):
    lexpr: Expression
    rexpr: Expression


@dataclass
class FuncCallOperator(Operator):
    func_name: str
    params: list[Expression]


@dataclass
class CompBranch:
    condition: Expression
    branch: list[Operator]


@dataclass
class ConditionOperator(Operator):
    condition: Expression
    then_branch: list[Operator]
    else_branch: list[Operator]
    comp_branches: list[CompBranch]


@dataclass
class PreConditionLoopOperator(Operator):
    pass


@dataclass
class WhileLoopOperator(PreConditionLoopOperator):
    condition: Expression
    operators: list[Operator]


@dataclass
class ForLoopOperator(PreConditionLoopOperator):
    type: Type
    name: str
    from_expr: Expression
    to_expr: Expression
    step: Expression
    operators: list[Operator]


@dataclass
class PostConditionLoopOperator(Operator):
    condition: Expression
    operators: list[Operator]


@dataclass
class ReturnOperator(Operator):
    expr: Expression


@dataclass
class AssertOperator(Operator):
    expr: Expression


@dataclass
class EmptyOperator(Operator):
    pass


@dataclass
class VariableExpression(Expression):
    varname: str


@dataclass
class ConstExpression(Expression):
    value: typing.Any
    type: Type


@dataclass
class BinOpExpression(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class UnOpExpression(Expression):
    op: str
    expr: Expression


def parse_int(x) -> int:
    if x.isdigit():
        return x
    if x[0] == '{':
        x = str(x)
        pos = x.find('}')
        base = x[1:pos]
        x = x[pos + 1:]
        print(x)
        return int(x, int(base))
    return 0


symbs_by_code = ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL", "BS", "TAB", "LF", "VT",
                 "FF", "CR", "SO", "SI", "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
                 "CAN", "EM", "SUB", "ESC", "FS", "GS", "RS", "US"]


def parse_char(x) -> str:
    x = str(x)
    for i in range(len(symbs_by_code)):
        print("#{}".format(symbs_by_code[i]))
        tmpl = "#{}".format(symbs_by_code[i])
        if x[1:1 + len(tmpl)] == tmpl:
            return chr(i)
        tmpl = "#{{{}}}".format(format(i, 'x').upper())
        if x[1:1 + len(tmpl)] == tmpl:
            return chr(i)
    x = x[1:2]
    return x


def parse_boolean(x) -> bool:
    return x == 'T'


def parse_string(x) -> str:
    x = str(x)
    x = x.replace("\"", "")
    x = x.replace("$QUOT", "\"")
    for i in range(len(symbs_by_code)):
        print("${}".format(symbs_by_code[i]))
        tmpl = "${}".format(symbs_by_code[i])
        x = x.replace(tmpl, chr(i))
        tmpl = "${{{}}}".format(format(i, 'x').upper())
        x = x.replace(tmpl, chr(i))
    return x


INTEGER = pe.Terminal('INTEGER', '[0-9]+|{[0-9]+}[0-9A-Z]+', parse_int, priority=7)
CHAR = pe.Terminal('CHAR', "('#[A-Z]+')|('#{[0-9A-F]+}')|('.')", parse_char, priority=11)
BOOLEAN = pe.Terminal('BOOLEAN', "T|F", parse_boolean, priority=10)
STRING = pe.Terminal('STRING', '(\".*\"|\$QUOT|\$[A-Z]+|\${[0-9A-F]+})*', parse_string)

VARNAME = pe.Terminal('VARNAME', "[a-z][a-zA-Z0-9_]*", str)
ANYNAME = pe.Terminal('ANYNAME', "[a-zA-Z][a-zA-Z0-9_]*", str, priority=7)
VALNAME = pe.Terminal('VALNAME', "[A-Z][a-zA-Z0-9_]*", str, priority=8)


def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None,
                       re_flags=re.IGNORECASE, priority=10)


KV_AND, KV_ARRAY, KV_ASSERT, KV_BOOL, KV_CHAR, KV_DEFINE, KV_DO = \
    map(make_keyword, 'and array assert bool char define do'.split())
KV_ELSE, KV_ELSEIF, KV_END, KV_F, KV_IF, KV_INT, KV_MOD = \
    map(make_keyword, 'else elseif end F if int mod'.split())
KV_NEW, KV_NOT, KN_NULL, KV_OR, KV_RETURN, KV_STEP, KV_T = \
    map(make_keyword, 'new not NULL or return step T'.split())
KV_THEN, KV_TO, KV_WHILE, KV_XOR = \
    map(make_keyword, 'then to while xor'.split())

NType, NArrayType, NProgram, NFuncs, NFunc, NFuncHeader, NFuncParams, NFuncConstructors, NFuncConstructor = \
    map(pe.NonTerminal, 'Type ArrayType Program Funcs Func FuncHeader FuncParams FuncConstructors FuncConstructor'
        .split())
NFuncBody, NOperators, NOperator, NDeclOperator, NValName, NAssignOperator, NFuncCallOperator, NParams = \
    map(pe.NonTerminal, 'FuncBody Operators Operator DeclOperator ValName AssignOperator FuncCallOperator Params'
        .split())
NCondOperator, NCompBranches, NPreConditionLoop, NLoopStep, NPostConditionLoop, NReturnOperator = \
    map(pe.NonTerminal, 'CondOperator CompBranches PreConditionLoop LoopStep PostConditionLoop ReturnOperator'.split())
NAssertOperator, NExpr, NLogCompOp, NLogCompExpr, NLogOp, NLogExpr, NCmpOp, NCmpExpr, NArithmOp = \
    map(pe.NonTerminal, 'AssertOperator Expr LogCompOn LogCompExpr LogOp LogExpr CmpOp CmpExpr ArithmOp'.split())
NArithmExpr, NMulOp, NMulExpr, NDegOp, NDegExpr, NUnaryOp, NUnaryExpr, NNewExpr, NArrVal = \
    map(pe.NonTerminal, 'ArithmExpr MulOp MulExpr DegOp DegExpr UnaryOp UnaryExpr NewExpr ArrVal'.split())

NProgram |= NFuncs
NFuncs |= NFuncs, NFunc, lambda funcs, func: funcs + [func]
NFuncs |= lambda: []

NFunc |= NFuncHeader, NFuncBody, lambda head, body: Function(head, body)

NFuncHeader |= KV_DEFINE, NType, VALNAME, NFuncParams, lambda type, name, params: FuncHeader(type, name, params)
NFuncHeader |= KV_DEFINE, VALNAME, NFuncParams, lambda type, name, params: FuncHeader(Type.Void, name, params)
NFuncParams |= '(', NFuncConstructors, ')', lambda func_contructors: FuncParam(func_contructors)
NFuncConstructors |= NFuncConstructors, ',', NFuncConstructor, lambda funcs, func: funcs + [func]
NFuncConstructors |= NFuncConstructor, lambda func_constructor: [func_constructor]
NFuncConstructors |= lambda: []
NFuncConstructor |= NType, VARNAME, lambda type, varname: FuncConstructor(type, varname)
NFuncConstructor |= NType, VALNAME, lambda type, varname: FuncConstructor(type, varname)

NFuncBody |= NOperators, KV_END, lambda operators: FuncBody(operators)
NOperators |= NOperators, NOperator, ';', lambda funcs, func: funcs + [func]
NOperators |= lambda: []

NOperator |= NDeclOperator
NOperator |= NAssignOperator
NOperator |= NFuncCallOperator
NOperator |= NCondOperator
NOperator |= NPreConditionLoop
NOperator |= NPostConditionLoop
NOperator |= NReturnOperator
NOperator |= NAssertOperator

NDeclOperator |= NType, ANYNAME, ':=', NExpr, lambda type, name, expr: DeclOperator(type, name, expr)

NAssignOperator |= NExpr, ':=', NExpr, lambda expr1, expr2: AssignOperator(expr1, expr2)

NFuncCallOperator |= VALNAME, '(', NParams, ')', lambda name, params: FuncCallOperator(name, params)
NParams |= NParams, ',', NExpr, lambda funcs, func: funcs + [func]
NParams |= NExpr
NParams |= lambda: []

NCondOperator |= KV_IF, NExpr, KV_THEN, NOperators, NCompBranches, KV_END, \
    lambda expr, operators, br: ConditionOperator(expr, operators, [], br)
NCondOperator |= KV_IF, NExpr, KV_THEN, NOperators, NCompBranches, KV_ELSE, NOperators, KV_END, \
    lambda expr, operators, operators2, br: ConditionOperator(expr, operators, operators2, br)
NCompBranches |= NCompBranches, KV_ELSEIF, NOperators
NCompBranches |= lambda: []

NPreConditionLoop |= KV_WHILE, NExpr, KV_DO, NOperators, KV_END, lambda expr, operators: \
    WhileLoopOperator(expr, operators)
NPreConditionLoop |= VARNAME, ':=', NExpr, KV_TO, NExpr, NLoopStep, KV_DO, NOperators, KV_END, \
    lambda name, expr1, expr2, step, operators: ForLoopOperator(Type.Void, name, expr1, expr2, step, operators)
# NPreConditionLoop |= NType, VARNAME, ':=', NExpr, KV_TO, NExpr, NLoopStep, KV_DO, NOperators, KV_END, \
#     lambda type, name, expr1, expr2, step, operators: ForLoopOperator(type, name, expr1, expr2, step, operators)
NLoopStep |= KV_STEP, NExpr
NLoopStep |= lambda: []

NPostConditionLoop |= KV_DO, NOperators, KV_WHILE, NExpr, lambda opers, expr: PostConditionLoopOperator(expr, opers)

NReturnOperator |= KV_RETURN, NExpr

NAssertOperator |= KV_ASSERT, NExpr

NExpr |= NLogCompExpr
NExpr |= NLogCompExpr, NLogCompOp, NLogCompExpr, BinOpExpression
NLogCompOp |= KV_OR, lambda: 'or'
NLogCompOp |= KV_XOR, lambda: 'xor'

NLogCompExpr |= NLogExpr
NLogCompExpr |= NLogCompExpr, NLogOp, NLogExpr, BinOpExpression
NLogOp |= KV_AND, lambda: 'and'

NLogExpr |= NCmpExpr
NLogExpr |= NLogExpr, NCmpOp, NCmpExpr, BinOpExpression
NCmpOp |= '=', lambda: '='
NCmpOp |= '<>', lambda: '<>'
NCmpOp |= '<', lambda: '<'
NCmpOp |= '>', lambda: '>'
NCmpOp |= '<=', lambda: '<='
NCmpOp |= '>=', lambda: '>='

NCmpExpr |= NArithmExpr
NCmpExpr |= NCmpExpr, NArithmOp, NArithmExpr, BinOpExpression
NArithmOp |= '+', lambda: '+'
NArithmOp |= '-', lambda: '-'

NArithmExpr |= NMulExpr
NArithmExpr |= NArithmExpr, NMulOp, NMulExpr, BinOpExpression
NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= KV_MOD, lambda: 'mod'

NMulExpr |= NDegExpr
NMulExpr |= NDegExpr, NDegOp, NMulExpr, BinOpExpression
NDegOp |= '**', lambda: '**'

NDegExpr |= NUnaryExpr
# NDegExpr |= '-', NUnaryExpr, lambda t: UnOpExpression('-', t)

NUnaryExpr |= ANYNAME
NUnaryExpr |= NArrVal
NUnaryExpr |= NFuncCallOperator
NUnaryExpr |= NNewExpr
NUnaryExpr |= INTEGER
NUnaryExpr |= CHAR
NUnaryExpr |= BOOLEAN
NUnaryExpr |= STRING

NNewExpr |= KV_NEW, NType, '[', NExpr, ']'
NArrVal |= ANYNAME, '[', NExpr, ']'

NType |= KV_INT, lambda: Type.Integer
NType |= KV_BOOL, lambda: Type.Boolean
NType |= KV_CHAR, lambda: Type.Char
NType |= NType, KV_ARRAY, lambda t: "array of {}".format(t)

p = pe.Parser(NProgram)
assert p.is_lalr_one()

p.add_skipped_domain('\\s')

from pprint import pprint
import sys

for filename in sys.argv[1:]:
    try:
        with open(filename) as f:
            tree = p.parse(f.read())
            pprint(tree)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')
    except Exception as e:
        print(e)
