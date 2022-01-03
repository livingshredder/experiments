package interop

//#include <nfkm.h>
import "C"
import (
	"unsafe"
)

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
		return nil, prettyError("NFKM_newkey_makeaclx", status)
	}

	return &acl, nil
}

type ACLBuilder struct {
	ssn  *Session
	data C.M_ACL

	groups []C.M_PermissionGroup
}

func (a ACLBuilder) WithGroup(group C.M_PermissionGroup) ACLBuilder {
	a.groups = append(a.groups, group)
	return a
}

// Adds default permissions for the Security World to the ACL
// This includes blobbing for the HKM, full control from HKNSO, and HKRE if recovery is enabled
func (a ACLBuilder) WithWorld(world *World, recovery bool) ACLBuilder {
	a.groups = append(a.groups,
		NewPermissionGroupBuilder().
			WithLimit(C.M_UseLimit{}).Build(),
	)

	return a
}

func NewACLBuilder(ssn *Session) ACLBuilder {
	return ACLBuilder{ssn: ssn}
}

type PermissionGroupBuilder struct {
	group C.M_PermissionGroup

	limits  []C.M_UseLimit
	actions []C.M_Action
}

func (p PermissionGroupBuilder) WithFlags(flags C.M_PermissionGroup_flags) PermissionGroupBuilder {
	p.group.flags += flags
	return p
}

func (p PermissionGroupBuilder) WithLimit(limit C.M_UseLimit) PermissionGroupBuilder {
	p.limits = append(p.limits, limit)
	return p
}

func (p PermissionGroupBuilder) WithAction(action C.M_Action) PermissionGroupBuilder {
	p.actions = append(p.actions, action)
	return p
}

func (p PermissionGroupBuilder) WithCertifier(hash C.M_KeyHash) PermissionGroupBuilder {
	p.group.flags += C.PermissionGroup_flags_certifier_present
	p.group.certifier = &hash
	return p
}

func (p PermissionGroupBuilder) WithCertifierAndMech(hashAndMech C.M_KeyHashAndMech) PermissionGroupBuilder {
	p.group.flags += C.PermissionGroup_flags_certifier_present | C.PermissionGroup_flags_certmech_present
	p.group.certmech = &hashAndMech
	return p
}

func (p PermissionGroupBuilder) WithModuleSerial(serial C.M_ASCIIString) PermissionGroupBuilder {
	p.group.moduleserial = &serial
	return p
}

func (p PermissionGroupBuilder) Build() C.M_PermissionGroup {
	group := p.group
	if l := len(p.limits); l > 0 {
		group.n_limits = C.int(l)
		group.limits = (C.M_vec_UseLimit)(unsafe.Pointer(&p.limits[0]))
	}

	if l := len(p.actions); l > 0 {
		group.n_actions = C.int(l)
		group.actions = (C.M_vec_Action)(unsafe.Pointer(&p.actions[0]))
	}

	return p.group
}

func NewPermissionGroupBuilder() PermissionGroupBuilder {
	return PermissionGroupBuilder{}
}
