package interop

//#include <nfkm.h>
import "C"
import (
	"fmt"
	"log"
)

// Represents a nCipher Security World
type World struct {
	ssn  *Session
	Data *C.NFKM_WorldInfo
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
		log.Fatalf("NewACL failed: %s", err)
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
		log.Fatalf("NewKey failed: %s", err)
	}

	key.PrettyPrint()
}
