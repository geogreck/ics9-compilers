package main

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/printer"
	"go/token"
	"os"
)

func process(stmt ast.Stmt, x *[]ast.Stmt, i int) {
	if declStmt, ok := stmt.(*ast.DeclStmt); ok {
		if genDecl, ok := declStmt.Decl.(*ast.GenDecl); ok && genDecl.Tok == token.VAR {
			for _, spec := range genDecl.Specs {
				if valueSpec, ok := spec.(*ast.ValueSpec); ok {
					for j, name := range valueSpec.Names {
						value := valueSpec.Values[j]
						assignStmt := &ast.AssignStmt{
							Lhs: []ast.Expr{name},
							Tok: token.DEFINE,
							Rhs: []ast.Expr{value},
						}
						(*x)[i] = assignStmt
					}
				}
			}
		}
	}
}

func main() {
	src, err := os.ReadFile("example/example.go")
	if err != nil {
		panic(err)
	}

	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, "", src, parser.ParseComments)
	if err != nil {
		panic(err)
	}

	ast.Inspect(file, func(n ast.Node) bool {
		switch x := n.(type) {
		case *ast.FuncDecl:
			fmt.Println(x)
			for i, stmt := range x.Body.List {
				process(stmt, &x.Body.List, i)
			}

		case *ast.IfStmt:
			for i, stmt := range x.Body.List {
				process(stmt, &x.Body.List, i)
			}

		case *ast.ForStmt:
			for i, stmt := range x.Body.List {
				process(stmt, &x.Body.List, i)
			}

		case *ast.FuncLit:
			for i, stmt := range x.Body.List {
				process(stmt, &x.Body.List, i)
			}

		}

		return true
	})

	err = printer.Fprint(os.Stdout, fset, file)
	if err != nil {
		panic(err)
	}
}
