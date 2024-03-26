% Лабораторная работа № 2.2 «Абстрактные синтаксические деревья»
% <лабораторная ещё не сдана>
% Георгий Гречко, ИУ9-61Б

# Цель работы

# Индивидуальный вариант

# Реализация

## Абстрактный синтаксис

Программа представляет собой набор определений функций. Порядок определения не важен.

```
Program -> Funcs
Funcs -> Funcs Func | ε
```

Определение функции состоит из заголовка и тела.

```
Func -> FuncHeader FuncBody
```

Заголовок функции начинается со слова define за которым опционально идет
тип возвращаемого значения, имя функции и список формальных параметров.

!! Имя функции должно начинаться с заглавной буквы
```
FuncHeader -> DEFINE Type FUNCNAME FuncParams | DEFINE FUNCNAME FuncParams
```

Список формальных параметров заключен в круглые скобки и состоит 
из последовательности операторов объявлений.
```
FuncParams -> ( FuncConstructors )
FuncConstructors -> FuncConstructors , FuncConstructor | FuncConstructor | ε
FuncConstructor -> Type VARNAME
```

Тело функции представляет собой последовательность операторов, разделённых точками с запятой
и завершается ключевым словом end.

```
FuncBody -> Operators END
Operators -> Operators Operator ; | ε
```

В языке есть три примитивных типа int, char и bool и типы-массивы.

```
Type -> INT | CHAR | BOOL | ArrayType
ArrayType -> Type ARRAY
```

Выражения формируются из символов операций, констант, имен переменных, параметров и функций,
изображений типов и круглых скобок.
```
PrimExpr -> Expr | NewExpr

NewExpr -> NEW Type '[' Expr ']'
Expr -> ( Expr ) | Expr BinOp Expr | FuncCallOperator | UnarOp Expr | ArrVal | ConstVal

BinOp -> LogicOp | CompareOp | MathOp
LogicOp -> AND | OR | XOR
CompareOp -> EQ | NEQ | LT | GT | LTE | GTE
MathOp -> EXP | MUL | DIV | MOD | ADD | SUB

UnarOp -> - | NOT

ArrVal -> ARRNAME '[' Expr ']'

ConstVal -> IntConst | CharConst | StringConst | BoolConst | NULL

IntConst -> "[0-9]+|{[0-9]+}[0-9A-Z]+"
CharConst -> "'.'|#{[0-9A-F]+}|#[A-F]+"
StringConst -> блять это полная параша
```

Операторы - действия, выполняемые программой. Предусмотрено 9 типов операторов.

```
Operator -> DeclOperator
Operator -> AssignOperator
Operator -> FuncCallOperator
Operator -> CondOperator
Operator -> PreConditionLoop
Operator -> PostConditionLoop
Operator -> ReturnOperator
Operator -> AssertOperator
```

Оператор-объявление служит для объявления и инициализации переменных. Имеет следующую структуру:

```
DeclOperator -> Type VARNAME
DecltOperator -> Type ValName ASSIGN Expr
ValName -> VARNAME | CONSTNAME
```

Оператор присваивания служит для присваивания значения ячейкам.

```
AssignOperator -> Expr ASSIGN Expr
```

Оператор вызова функции

```
FuncCallOperator -> FUNCNAME '(' Params ')'
Params -> Params ',' Expr | Expr | ε
```

Оператор выбора

```
CondOperator -> IF Cond THEN Operators CompBranches END
CondOperator -> IF Cond THEN Operators CompBranches ELSE Operators END

CompBranches -> ε
CompBranches -> CompBranches ELSEIF Operators 
```

Оператор цикла с предусловием

```
PreConditionLoop -> WHILE Expr DO Operators END
PreConditionLoop -> VARNAME ASSIGN Expr TO Expr LoopStep DO Operators END
PreConditionLoop -> Type VARNAME ASSIGN Expr TO Expr LoopStep DO Operators END
LoopStep -> STEP Expr | ε
```

Оператор цикла с постусловием

```
PostConditionLoop -> DO Operators WHILE Expr
```

Оператор завершения функции

```
ReturnOperator -> RETURN Expr
```

Оператор-предупреждение

```
AssertOperator -> ASSERT EXPR
```

## Лексическая структура и конкретный синтаксис
…

## Программная реализация

```python
…
```

# Тестирование

## Входные данные

```
…
```

## Вывод на `stdout`

<!-- ENABLE LONG LINES -->

```
…
```

# Вывод
‹пишете, чему научились›
