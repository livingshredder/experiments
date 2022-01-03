package main

import (
	"log"

	"github.com/citadelcore/experiments/ncipher/go/internal/pkg/interop"
)

func main() {
	session, err := interop.NewSession()
	if err != nil {
		log.Fatalf("%s", err)
	}
	defer session.Close()

	world, err := session.GetWorld()
	if err != nil {
		log.Fatalf("%s", err)
	}
	defer world.Close()

	//fmt.Println(world)

	//fmt.Println(world)
	world.KeygenTest()

	//cmd.Execute()
	//C.NFKM_getinfo()
}
