import abc
import enum
import re
import sys
import typing
from dataclasses import dataclass

import parser_edsl as pe
from pprint import pprint


class SemanticError(pe.Error):
    def __init__(self, pos, message):
        self.pos = pos
        self.__message = message

    @property
    def message(self):
        return self.__message


class RepeatedFuncError(SemanticError):
    def __init__(self, pos, funcname):
        self.pos = pos
        self.funcname = funcname

    @property
    def message(self):
        return f"Функция с именем '{self.funcname}' уже объявлена"


class UndeclaredFuncError(SemanticError):
    def __init__(self, pos, funcname):
        self.pos = pos
        self.funcname = funcname

    @property
    def message(self):
        return f"Функция с именем '{self.funcname}' не была объявлена"


class UndeclaredVarError(SemanticError):
    def __init__(self, pos, varname):
        self.pos = pos
        self.varname = varname

    @property
    def message(self):
        return f"Переменная с именем '{self.varname}' не была объявлена"


class MismatchedTypeError(SemanticError):
    def __init__(self, pos, type1, type2):
        self.pos = pos
        self.type1 = type1
        self.type2 = type2

    @property
    def message(self):
        return f"Операнды оператора присваивания имеют различные типы: '{self.type1}' и '{self.type2}'"


class WrongArgsCount(SemanticError):
    def __init__(self, pos, count1, count2):
        self.pos = pos
        self.count1 = count1
        self.count2 = count2

    @property
    def message(self):
        return f"Неправильное количество аргументов вызова функции: '{self.count1}'. ожидалось: '{self.count2}'"


class WrongBinOperandTypes(SemanticError):
    def __init__(self, pos, oper, type1, type2):
        self.pos = pos
        self.oper = oper
        self.type1 = type1
        self.type2 = type2

    @property
    def message(self):
        return f"Неправильные типы для операнда '{self.oper}': '{self.type1}' и '{self.type2}'"


class WrongUnaryOperandTypes(SemanticError):
    def __init__(self, pos, oper, type1):
        self.pos = pos
        self.oper = oper
        self.type1 = type1

    @property
    def message(self):
        return f"Неправильный тип для операнда '{self.oper}': '{self.type1}'"


class Type(abc.ABC):
    pass


class BaseType(enum.Enum):
    Integer = 'INTEGER'
    Char = 'CHAR'
    Boolean = 'BOOLEAN'
    Void = 'VOID'


@dataclass
class ElementaryType(Type):
    type: BaseType


@dataclass
class ArrayType(Type):
    wrapped: BaseType


class Operator(abc.ABC):
    def check(self, funcs, curvars):
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
    func_params: FuncParam


@dataclass
class FuncBody:
    operators: list[Operator]


@dataclass
class Function:
    header: FuncHeader
    body: FuncBody
    func_coords: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        head, body = attrs
        head_coord, body_coord = coords
        return Function(head, body, head_coord)

    def check(self, funcs):
        curvars = {}
        for operator in self.body.operators:
            operator.check(funcs, curvars)
            # print(curvars)


@dataclass
class Program:
    funcs: list[Function]

    def check(self):
        funcs = {}
        for func in self.funcs:
            if func.header.func_name in funcs:
                raise RepeatedFuncError(func.func_coords, func.header.func_name)
            funcs[func.header.func_name] = func
        for func in self.funcs:
            func.check(funcs)


@dataclass
class Expression(abc.ABC):
    def get_type(self, curvars):
        pass


@dataclass
class DeclOperator(Operator):
    type: Type
    name: str
    expr: Expression

    typec: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        type, name, expr = attrs
        typec, namec, assignc, exprc = coords
        return DeclOperator(type, name, expr, typec)

    def check(self, func_names, curvars):
        if self.type != self.expr.get_type(curvars):
            raise MismatchedTypeError(self.typec, self.type, self.expr.get_type(curvars))
        curvars[self.name] = {'type': self.type, 'name': self.name}


@dataclass
class AssignOperator(Operator):
    lexpr: Expression
    rexpr: Expression

    lexprc: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        lexpr, rexpr = attrs
        lc, ac, rc = coords
        return AssignOperator(lexpr, rexpr, lc)

    def check(self, func_names, curvars):
        if type(self.lexpr) is VarName and self.lexpr.name not in curvars:
            raise UndeclaredVarError(self.lexprc, self.lexpr.name)
        type1 = None
        if self.lexpr.name in curvars:
            type1 = curvars[self.lexpr.name]['type']
        type2 = self.rexpr.get_type(curvars)

        if type1 != type2:
            raise MismatchedTypeError(self.lexprc, type1, type2)


@dataclass
class FuncCallOperator(Operator):
    func_name: str
    params: list[Expression]

    oper_coords: pe.Position

    params_coords: list[pe.Position]

    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, params = attrs
        params_coord = coords
        return FuncCallOperator(name, params, params_coord[0], params_coord[1:])

    def check(self, funcs, curvars):
        if self.func_name not in funcs.keys():
            raise UndeclaredFuncError(self.oper_coords, self.func_name)
        expected_params = funcs[self.func_name].header.func_params.func_contructors
        len1 = 1 if type(self.params) is not list else len(self.params)
        len2 = len(expected_params)
        if len1 != len2:
            raise WrongArgsCount(self.oper_coords, len1, len2)
        for i in range(len(expected_params)):
            param = self.params[i]
            exp_param = expected_params[i]
            if param.get_type(curvars) != exp_param.type:
                raise MismatchedTypeError(self.params_coords[i], param.get_type(curvars), exp_param.type)




@dataclass
class CompBranch:
    condition: Expression
    branch: list[Operator]

    def check(self, funcs, curvars):
        curvars_internal = curvars.copy()
        for operator in self.branch:
            operator.check(funcs, curvars_internal)


@dataclass
class ConditionOperator(Operator):
    condition: Expression
    then_branch: list[Operator]
    else_branch: list[Operator]
    comp_branches: list[CompBranch]

    def check(self, funcs, curvars):
        curvars_internal = curvars.copy()
        for operator in self.then_branch:
            operator.check(funcs, curvars_internal)

        curvars_internal = curvars.copy()
        for operator in self.else_branch:
            operator.check(funcs, curvars_internal)

        for branch in self.comp_branches:
            branch.check(funcs, curvars)


@dataclass
class PreConditionLoopOperator(Operator):
    pass


@dataclass
class WhileLoopOperator(PreConditionLoopOperator):
    condition: Expression
    operators: list[Operator]

    def check(self, funcs, curvars):
        curvars_internal = curvars.copy()
        for operator in self.operators:
            operator.check(funcs, curvars_internal)


@dataclass
class ForLoopOperator(PreConditionLoopOperator):
    type: Type
    name: str
    from_expr: Expression
    to_expr: Expression
    step: Expression
    operators: list[Operator]

    def check(self, funcs, curvars):
        curvars_internal = curvars.copy()
        for operator in self.operators:
            operator.check(funcs, curvars_internal)


@dataclass
class PostConditionLoopOperator(Operator):
    condition: Expression
    operators: list[Operator]

    def check(self, funcs, curvars):
        curvars_internal = curvars.copy()
        for operator in self.operators:
            operator.check(funcs, curvars_internal)


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

    binc: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        left, op, right = attrs
        lc, opc, rc = coords
        return BinOpExpression(left, op, right, lc)

    def get_type(self, curvars):
        int_type = ElementaryType(BaseType.Integer)
        char_type = ElementaryType(BaseType.Char)
        bool_type = ElementaryType(BaseType.Boolean)
        ltype = self.left.get_type(curvars)
        rtype = self.right.get_type(curvars)
        print(ltype)

        if self.op == '+':
            if ltype == int_type and rtype == int_type:
                return int_type
            if ltype == int_type and rtype == char_type:
                return char_type
            if ltype == char_type and rtype == int_type:
                return char_type
            raise WrongBinOperandTypes(self.binc, self.op, ltype, rtype)

        if self.op == '-':
            if ltype == int_type and rtype == int_type:
                return int_type
            if ltype == char_type and rtype == int_type:
                return int_type
            if ltype == char_type and rtype == int_type:
                return char_type
            raise WrongBinOperandTypes(self.binc, self.op, ltype, rtype)

        if self.op in ["**", "*", "/", "mod"]:
            if ltype == int_type and rtype == int_type:
                return int_type
            raise WrongBinOperandTypes(self.binc, self.op, ltype, rtype)

        if self.op in ["=", "<>"]:
            if ltype == int_type and rtype == int_type:
                return bool_type
            if ltype == int_type and rtype == char_type:
                return bool_type
            if ltype == char_type and rtype == int_type:
                return bool_type
            if ltype == char_type and rtype == char_type:
                return bool_type
            if ltype == bool_type and rtype == bool_type:
                return bool_type
            if ltype == ArrayType and rtype == ArrayType:
                return bool_type
            raise WrongBinOperandTypes(self.binc, self.op, ltype, rtype)

        if self.op in ["<", ">", "<=", ">="]:
            if ltype == int_type and rtype == int_type:
                return bool_type
            if ltype == int_type and rtype == char_type:
                return bool_type
            if ltype == char_type and rtype == int_type:
                return bool_type
            if ltype == char_type and rtype == char_type:
                return bool_type
            raise WrongBinOperandTypes(self.binc, self.op, ltype, rtype)

        if self.op in ["and", "or", "xor"]:
            if ltype == bool_type and rtype == bool_type:
                return bool_type
            raise WrongBinOperandTypes(self.binc, self.op, ltype, rtype)

        if ltype != rtype:
            raise MismatchedTypeError(self.binc, ltype, rtype)
        return ltype


@dataclass
class ConstExpr(Expression):
    value: typing.Any
    type: ArrayType or ElementaryType

    @pe.ExAction
    def create(attrs, coords, res_coord):
        value, typee = attrs
        vc, tc = coords
        return ConstExpr(value, typee)

    def get_type(self, curvars):
        return self.type


@dataclass
class VarName(Expression):
    name: str
    namec: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        name = attrs[0]
        namec = coords[0]
        return VarName(name, namec)

    def get_type(self, curvars):
        if self.name in curvars:
            return curvars[self.name]['type']
        else:
            raise UndeclaredVarError(self.namec, self.name)


@dataclass
class UnOpExpression(Expression):
    op: str
    expr: Expression

    def get_type(self, curvars):
        int_type = ElementaryType(BaseType.Integer)
        char_type = ElementaryType(BaseType.Char)
        bool_type = ElementaryType(BaseType.Boolean)
        ltype = self.expr.get_type(curvars)

        if self.op == "[]":
            if ltype == int_type:
                return ArrayType.wrapped
            if ltype == char_type:
                return ArrayType.wrapped
            raise WrongUnaryOperandTypes(self.binc, self.op, ltype)

        if self.op == "-":
            if ltype == int_type:
                return int_type
            if ltype == char_type:
                return char_type
            raise WrongUnaryOperandTypes(self.binc, self.op, ltype)

        if self.op == "not":
            if ltype == bool_type:
                return bool_type
            raise WrongUnaryOperandTypes(self.binc, self.op, ltype)


def parse_int(x) -> int:
    if x.isdigit():
        return x
    if x[0] == '{':
        x = str(x)
        pos = x.find('}')
        base = x[1:pos]
        x = x[pos + 1:]
        return int(x, int(base))
    return 0


symbs_by_code = ["NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL", "BS", "TAB", "LF", "VT",
                 "FF", "CR", "SO", "SI", "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
                 "CAN", "EM", "SUB", "ESC", "FS", "GS", "RS", "US"]


def parse_char(x) -> str:
    x = str(x)
    for i in range(len(symbs_by_code)):
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
        tmpl = "${}".format(symbs_by_code[i])
        x = x.replace(tmpl, chr(i))
        tmpl = "${{{}}}".format(format(i, 'x').upper())
        x = x.replace(tmpl, chr(i))
    return x


INTEGER = pe.Terminal('INTEGER', '[0-9]+|{[0-9]+}[0-9A-Z]+', parse_int, priority=7)
CHAR = pe.Terminal('CHAR', "('#[A-Z]+')|('#{[0-9A-F]+}')|('.')", parse_char, priority=11)
BOOLEAN = pe.Terminal('BOOLEAN', "T|F", parse_boolean, priority=10)
STRING = pe.Terminal('STRING', r'(\".*\"|\$QUOT|\$[A-Z]+|\${[0-9A-F]+})*', parse_string)

VARNAME = pe.Terminal('VARNAME', "[a-z][a-zA-Z0-9_]*", str)
ANYNAME = pe.Terminal('ANYNAME', "[a-zA-Z][a-zA-Z0-9_]*", str, priority=7)
VALNAME = pe.Terminal('VALNAME', "[A-Z][a-zA-Z0-9_]*", str, priority=8)


def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None,
                       priority=10)


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
NArithmExpr, NMulOp, NMulExpr, NDegOp, NDegExpr, NUnaryOp, NUnaryExpr, NNewExpr, NArrVal, NConst = \
    map(pe.NonTerminal, 'ArithmExpr MulOp MulExpr DegOp DegExpr UnaryOp UnaryExpr NewExpr ArrVal Const'.split())

NProgram |= NFuncs, lambda funcs: Program(funcs)
NFuncs |= NFuncs, NFunc, lambda funcs, func: funcs + [func]
NFuncs |= lambda: []

NFunc |= NFuncHeader, NFuncBody, Function.create

NFuncHeader |= KV_DEFINE, NType, VALNAME, NFuncParams, lambda type, name, params: FuncHeader(type, name, params)
NFuncHeader |= KV_DEFINE, VALNAME, NFuncParams, lambda type, name, params: FuncHeader(ElementaryType(BaseType.Void),
                                                                                      name, params)
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

NDeclOperator |= NType, ANYNAME, ':=', NExpr, DeclOperator.create

NAssignOperator |= NExpr, ':=', NExpr, AssignOperator.create

NFuncCallOperator |= VALNAME, '(', NParams, ')', FuncCallOperator.create
NParams |= NParams, ',', NExpr, lambda funcs, func: funcs + [func]
NParams |= NExpr, lambda expr: [expr]
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
    lambda name, expr1, expr2, step, operators: ForLoopOperator(ElementaryType(BaseType.Void), name, expr1, expr2, step,
                                                                operators)
# NPreConditionLoop |= NType, VARNAME, ':=', NExpr, KV_TO, NExpr, NLoopStep, KV_DO, NOperators, KV_END, \
#     lambda type, name, expr1, expr2, step, operators: ForLoopOperator(type, name, expr1, expr2, step, operators)
NLoopStep |= KV_STEP, NExpr
NLoopStep |= lambda: []

NPostConditionLoop |= KV_DO, NOperators, KV_WHILE, NExpr, lambda opers, expr: PostConditionLoopOperator(expr, opers)

NReturnOperator |= KV_RETURN, NExpr

NAssertOperator |= KV_ASSERT, NExpr

NExpr |= NLogCompExpr
NExpr |= NLogCompExpr, NLogCompOp, NLogCompExpr, BinOpExpression.create
NLogCompOp |= KV_OR, lambda: 'or'
NLogCompOp |= KV_XOR, lambda: 'xor'

NLogCompExpr |= NLogExpr
NLogCompExpr |= NLogCompExpr, NLogOp, NLogExpr, BinOpExpression.create
NLogOp |= KV_AND, lambda: 'and'

NLogExpr |= NCmpExpr
NLogExpr |= NLogExpr, NCmpOp, NCmpExpr, BinOpExpression.create
NCmpOp |= '=', lambda: '='
NCmpOp |= '<>', lambda: '<>'
NCmpOp |= '<', lambda: '<'
NCmpOp |= '>', lambda: '>'
NCmpOp |= '<=', lambda: '<='
NCmpOp |= '>=', lambda: '>='

NCmpExpr |= NArithmExpr
NCmpExpr |= NCmpExpr, NArithmOp, NArithmExpr, BinOpExpression.create
NArithmOp |= '+', lambda: '+'
NArithmOp |= '-', lambda: '-'

NArithmExpr |= NMulExpr
NArithmExpr |= NArithmExpr, NMulOp, NMulExpr, BinOpExpression.create
NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= KV_MOD, lambda: 'mod'

NMulExpr |= NDegExpr
NMulExpr |= NDegExpr, NDegOp, NMulExpr, BinOpExpression.create
NDegOp |= '**', lambda: '**'

NDegExpr |= NUnaryExpr
# NDegExpr |= '-', NUnaryExpr, lambda t: UnOpExpression('-', t)

NUnaryExpr |= ANYNAME, VarName.create
NUnaryExpr |= NArrVal
NUnaryExpr |= NFuncCallOperator
NUnaryExpr |= NNewExpr
NUnaryExpr |= NConst


NUnaryExpr |= INTEGER, lambda x: ConstExpr(x, ElementaryType(BaseType.Integer))
NUnaryExpr |= CHAR, lambda x: ConstExpr(x, ElementaryType(BaseType.Char))
NUnaryExpr |= BOOLEAN, lambda x: ConstExpr(x, ElementaryType(BaseType.Boolean))
NUnaryExpr |= STRING, lambda x: ConstExpr(x, ArrayType(ElementaryType(BaseType.Char)))

NNewExpr |= KV_NEW, NType, '[', NExpr, ']'
NArrVal |= ANYNAME, '[', NExpr, ']'

NType |= KV_INT, lambda: ElementaryType(BaseType.Integer)
NType |= KV_BOOL, lambda: ElementaryType(BaseType.Boolean)
NType |= KV_CHAR, lambda: ElementaryType(BaseType.Char)
NType |= NType, KV_ARRAY, lambda t: ArrayType(t)

p = pe.Parser(NProgram)
assert p.is_lalr_one()

p.add_skipped_domain('\\s')

p.add_skipped_domain(r'\*.*')

for filename in sys.argv[1:]:
    try:
        with open(filename) as f:
            tree = p.parse(f.read())
            # pprint(tree)
            tree.check()
            print("Программа корректна")
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')
    # except Exception as e:
    #     print(e)
