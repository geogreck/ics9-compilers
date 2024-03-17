package main

import "fmt"

var x = 10

func main() {
	var y = 20
	z := 30
	if z > 0 {
		var a = 5
		fmt.Println(a)
	}
	for i := 10; i < 10; i++ {
		var x = i
		fmt.Println(x)
	}
	fmt.Println(x, y, z)

	a := func() {
		var x = 10
		fmt.Println(x)
	}
	a()
}
