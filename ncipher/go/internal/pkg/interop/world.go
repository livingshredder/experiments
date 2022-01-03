package interop

//#include <nfkm.h>
import "C"
import (
	"fmt"
	"log"
	"unsafe"
)

// Represents a nCipher Security World
type World struct {
	ssn  *Session
	Data *C.NFKM_WorldInfo

	// data extracted from Data section
	Modules []Module
}

func (w *World) Close() {
	C.NFKM_freeinfo(w.ssn.app, &w.Data, w.ssn.cctx)
}

func (w *World) KeygenTest() {
	params := C.NFKM_MakeACLParams{}
	params.f = C.NFKM_NKF_RecoveryEnabled | C.NFKM_NKF_ProtectionModule
	params.op_base = C.NFKM_DEFOPPERMS_ENCRYPT | C.NFKM_DEFOPPERMS_DECRYPT

	acl, err := NewACL(w, params)
	if err != nil {
		log.Fatalf("%s", err)
	}
	defer acl.Close()

	fmt.Println("generating key...")
	key, err := GenerateAESKey(w, 256, GenerateKeyArgs{
		key: KeyProperties{acl: acl},
		gen: KeyGenerationProperties{
			flags: C.Cmd_GenerateKey_Args_flags_Certify,
		},
	})

	if err != nil {
		log.Fatalf("%s", err)
	}

	key.PrettyPrint()
}

func NewWorld(ssn *Session, data *C.NFKM_WorldInfo) World {
	world := World{ssn: ssn, Data: data}

	// Build the modules attribute
	if world.Data.modules != nil {
		len := world.Data.n_modules
		result := []Module{}
		data := (*[1 << 28]C.NFKM_opt_ModuleInfo)(unsafe.Pointer(world.Data.modules))[:len:len]

		for i := range data {
			if data[i] != nil {
				result = append(result, NewModule(ssn, *data[i]))
			}
		}

		world.Modules = result
	}

	return world
}
