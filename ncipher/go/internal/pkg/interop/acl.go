package interop

//#include <nfkm.h>
import "C"
import "log"

// Represents an access control list
type ACL struct {
	ssn  *Session
	Data C.M_ACL
}

func (a *ACL) Close() {
	C.NFastApp_FreeACL(a.ssn.app, a.ssn.cctx, nil, &a.Data)
}

func NewACL(world *World, params C.NFKM_MakeACLParams) (*ACL, error) {
	acl := ACL{ssn: world.ssn}
	status := C.NFKM_newkey_makeaclx(acl.ssn.app, acl.ssn.conn, world.Data, &params, &acl.Data, acl.ssn.cctx)
	if status != C.Status_OK {
		log.Fatalf("NFKM_newkey_makeaclx failed: %d", status)
	}

	return &acl, nil
}
