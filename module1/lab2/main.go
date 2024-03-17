package main

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
	"unicode"
)

var (
	FibNumberRegex = regexp.MustCompile("(^(0|10)*(1|0)? )|(^(0|10)*(1|0)?$)")
	IdentRegex     = regexp.MustCompile("((^([bcdfghjklmnpqrstvwxyz][aeiou])*[bcdfghjklmnpqrstvwxyz]? )|(^([aeiou][bcdfghjklmnpqrstvwxyz])*[aeiou]? ))|((^([bcdfghjklmnpqrstvwxyz][aeiou])*[bcdfghjklmnpqrstvwxyz]?$)|(^([aeiou][bcdfghjklmnpqrstvwxyz])*[aeiou]?$))")

	ErrFileEnd = fmt.Errorf("end of file reached")
)

type TokenDomain int

const (
	FibNumber TokenDomain = 1 << iota
	Ident
	Invalid
)

func (td TokenDomain) String() string {
	switch td {
	case FibNumber:
		return "FIB"
	case Ident:
		return "IDENT"
	case Invalid:
		return "???"
	default:
		panic("Unknown token domain")
	}
}

type Token interface {
	String() string
}

type TokenBase struct {
	Line   int
	Col    int
	Domain TokenDomain
}

type FibNumberToken struct {
	TokenBase
	Attr int
}

func NewFibNumberToken(line, col int, attr int) FibNumberToken {
	return FibNumberToken{
		TokenBase: TokenBase{
			Line:   line,
			Col:    col,
			Domain: FibNumber,
		},
		Attr: attr,
	}
}

func (t FibNumberToken) String() string {
	return fmt.Sprintf("%s (%d, %d): %d", t.Domain, t.Line, t.Col, t.Attr)
}

type IdentToken struct {
	TokenBase
	Attr string
}

func NewIdentToken(line, col int, attr string) IdentToken {
	return IdentToken{
		TokenBase: TokenBase{
			Line:   line,
			Col:    col,
			Domain: Ident,
		},
		Attr: attr,
	}
}

func (t IdentToken) String() string {
	return fmt.Sprintf("%s (%d, %d): %s", t.Domain, t.Line, t.Col, t.Attr)
}

type InvalidToken struct {
	TokenBase
	Attr string
}

func NewInvalidToken(line, col int, attr string) InvalidToken {
	return InvalidToken{
		TokenBase: TokenBase{
			Line:   line,
			Col:    col,
			Domain: Invalid,
		},
		Attr: attr,
	}
}

func (t InvalidToken) String() string {
	return fmt.Sprintf("syntax error (%d, %d)", t.Line, t.Col)
}

type Scanner interface {
	NextToken() (Token, error)
}

type ScannerImpl struct {
	Program []string
	Line    int
	Col     int
}

func NewScanner(lines []string) Scanner {
	return &ScannerImpl{
		Program: lines,
		Line:    0,
		Col:     0,
	}
}

func (si *ScannerImpl) Analyze(word string) TokenDomain {
	switch {
	case FibNumberRegex.FindString(word) == word:
		return FibNumber
	case IdentRegex.FindString(word) == word:
		return Ident
	default:
		return Invalid
	}
}

func (si *ScannerImpl) BuildToken(line, col int, word string) Token {
	line += 1
	col += 1
	domain := si.Analyze(word)
	switch domain {
	case FibNumber:
		return NewFibNumberToken(line, col, StringToFibNumder(word))
	case Ident:
		return NewIdentToken(line, col, word)
	default:
		return NewInvalidToken(line, col, word)
	}

}

func (si *ScannerImpl) NextToken() (Token, error) {
	for si.Line < len(si.Program) {
		for si.Col < len(si.Program[si.Line]) {
			curLine := si.Program[si.Line][si.Col:]

			fibNumWord := FibNumberRegex.FindStringIndex(curLine)
			if fibNumWord != nil {
				token := si.BuildToken(si.Line, si.Col, strings.TrimSpace(curLine[fibNumWord[0]:fibNumWord[1]]))
				si.Col += fibNumWord[1]
				return token, nil
			}

			identWord := IdentRegex.FindStringIndex(curLine)
			if identWord != nil {
				token := si.BuildToken(si.Line, si.Col, strings.TrimSpace(curLine[identWord[0]:identWord[1]]))
				si.Col += identWord[1]
				return token, nil
			}

			end := strings.IndexFunc(curLine, unicode.IsSpace)
			if end == -1 {
				token := si.BuildToken(si.Line, si.Col, curLine)
				si.Col += len(curLine) + 1
				return token, nil
			}
			token := si.BuildToken(si.Line, si.Col, curLine[:end])
			si.Col += end + 1
			return token, nil
		}
		si.Col = 0
		si.Line++
	}

	return InvalidToken{}, ErrFileEnd
}

func StringToFibNumder(word string) int {
	a, b := 2, 1
	sum := 0
	for i := len(word) - 1; i >= 0; i-- {
		s := word[i]
		snum, err := strconv.Atoi(string(s))
		if err != nil || (snum != 0 && snum != 1) {
			panic("invalid number")
		}
		sum += b * snum
		a, b = a+b, a
	}
	return sum
}

func main() {
	if len(os.Args) != 2 {
		panic("file name must be passed")
	}
	filename := os.Args[1]

	file, err := os.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	scanner := bufio.NewScanner(bytes.NewReader(file))
	lines := make([]string, 0)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}

	sc := NewScanner(lines)
	err = nil
	for err == nil {
		token, errr := sc.NextToken()
		if errr == nil {
			fmt.Println(token)
		}
		err = errr
	}
}
