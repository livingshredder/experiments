package interop

//#include <nfkm.h>
import "C"
import (
	"fmt"
	"log"
	"unsafe"
)

// Attributes on a key that remain the same throughout its lifecycle
type KeyInfo struct {
	Type   C.M_KeyType
	Length int
	Hash   C.M_KeyHash
}

// Attributes on a key that are set at generation time
// and may be able to be changed throughout its lifecycle
type KeyProperties struct {
	// The key's access control list
	acl *ACL

	// Key-specific application data
	appdata *C.M_AppData
}

// Represents a key in the security world loaded onto a module
type Key struct {
	ssn *Session

	// have we already fetched the info?
	infoExists bool

	// Warning: There is no guarantee the members of
	// this struct are populated. Use FetchInfo() to fetch it.
	Info KeyInfo

	// Cached
	props KeyProperties

	// Handle to this key in the security world
	Id   C.M_KeyID
	Cert *C.M_ModuleCert
}

// Retrieves the key info, populating Type, Length, and Hash.
func (k *Key) FetchInfo() error {
	if k.infoExists {
		return nil
	}

	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_GetKeyInfoEx

	args := (*C.M_Cmd_GetKeyInfoEx_Args)(unsafe.Pointer(&cmd.args))
	args.key = k.Id

	reply, status := k.ssn.Transact(cmd)
	if status != C.Status_OK {
		return prettyError("Cmd_GetKeyInfoEx", status)
	}

	rreply := (*C.M_Cmd_GetKeyInfoEx_Reply)(unsafe.Pointer(&reply.reply))
	k.Info.Type = rreply._type
	k.Info.Length = int(rreply.length)
	k.Info.Hash = rreply.hash

	k.infoExists = true
	return nil
}

// Retrieves the ACL. If it isn't present, it's looked up using the KeyID.
func (k *Key) GetACL() (*ACL, error) {
	if k.props.acl != nil {
		return k.props.acl, nil
	}

	acl := ACL{ssn: k.ssn}

	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_GetACL

	args := (*C.M_Cmd_GetACL_Args)(unsafe.Pointer(&cmd.args))
	args.key = k.Id

	reply, status := k.ssn.Transact(cmd)
	if status != C.Status_OK {
		return nil, prettyError("Cmd_GetACL", status)
	}

	rreply := (*C.M_Cmd_GetACL_Reply)(unsafe.Pointer(&reply.reply))
	acl.Data = rreply.acl

	k.props.acl = &acl
	return k.props.acl, nil
}

// Sets a new ACL on the key. The permissions need to support this or it will return an error.
func (k *Key) SetACL(acl ACL) error {
	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_SetACL

	args := (*C.M_Cmd_SetACL_Args)(unsafe.Pointer(&cmd.args))
	args.key = k.Id
	args.newacl = acl.Data

	_, status := k.ssn.Transact(cmd)
	if status != C.Status_OK {
		return prettyError("Cmd_SetACL", status)
	}

	k.props.acl = &acl
	return nil
}

func (k *Key) GetAppData() (*C.M_AppData, error) {
	if k.props.appdata != nil {
		return k.props.appdata, nil
	}

	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_GetAppData

	args := (*C.M_Cmd_GetAppData_Args)(unsafe.Pointer(&cmd.args))
	args.key = k.Id

	reply, status := k.ssn.Transact(cmd)
	if status != C.Status_OK {
		return nil, prettyError("Cmd_GetAppData", status)
	}

	rreply := (*C.M_Cmd_GetAppData_Reply)(unsafe.Pointer(&reply.reply))
	k.props.appdata = &rreply.appdata

	return k.props.appdata, nil
}

func (k *Key) SetAppData(data C.M_AppData) error {
	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_SetAppData

	args := (*C.M_Cmd_SetAppData_Args)(unsafe.Pointer(&cmd.args))
	args.key = k.Id
	args.appdata = data

	_, status := k.ssn.Transact(cmd)
	if status != C.Status_OK {
		return prettyError("Cmd_SetAppData", status)
	}

	k.props.appdata = &data
	return nil
}

func (k *Key) Destroy() error {
	return k.ssn.Destroy(k.Id)
}

func (k *Key) String() string {
	return fmt.Sprintf("%d", k.Id)
}

//go:generate stringer -type=_Ctype_M_KeyType
func (k *Key) PrettyPrint() {
	err := k.FetchInfo()
	if err != nil {
		log.Fatalf("Failed to get key info: %s", err)
	}

	fmt.Printf("KeyID: %#x\n", k.Id)
	fmt.Printf("  Hash: %x\n", k.Info.Hash)
	fmt.Printf("  Length: %d\n", k.Info.Length)
	fmt.Printf("  Type: %s\n", enumValToStr(uint(k.Info.Type), unsafe.Pointer(&C.NF_KeyType_enumtable)))
}

func NewKey(world *World, id C.M_KeyID) (*Key, error) {
	key := Key{ssn: world.ssn, Id: id}
	return &key, nil
}

type KeyGenerationProperties struct {
	module C.M_ModuleID
	flags  C.M_Cmd_GenerateKey_Args_flags
}

type GenerateKeyArgs struct {
	key KeyProperties
	gen KeyGenerationProperties
}

type GenerateKeyPairArgs struct {
	publicKey  KeyProperties
	privateKey KeyProperties
	gen        KeyGenerationProperties
}

func generateKey(world *World, kargs GenerateKeyArgs, params C.M_KeyGenParams) (*Key, error) {
	key := Key{ssn: world.ssn, props: kargs.key}

	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_GenerateKey

	args := (*C.M_Cmd_GenerateKey_Args)(unsafe.Pointer(&cmd.args))
	args.flags = kargs.gen.flags
	args.module = kargs.gen.module
	args.params = params
	args.acl = kargs.key.acl.Data

	if kargs.key.appdata != nil {
		value := C.M_AppData(*kargs.key.appdata)
		args.appdata = &value
	}

	reply, status := key.ssn.Transact(cmd)
	if status != C.Status_OK {
		return nil, prettyError("Cmd_GenerateKey", status)
	}

	rreply := (*C.M_Cmd_GenerateKey_Reply)(unsafe.Pointer(&reply.reply))
	key.Id = rreply.key
	key.Cert = rreply.cert
	return &key, nil
}

func generateKeyPair(world *World, kargs GenerateKeyPairArgs, params C.M_KeyGenParams) (*Key, *Key, error) {
	publicKey := Key{ssn: world.ssn, props: kargs.publicKey}
	privateKey := Key{ssn: world.ssn, props: kargs.privateKey}

	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_GenerateKeyPair

	args := (*C.M_Cmd_GenerateKeyPair_Args)(unsafe.Pointer(&cmd.args))
	args.flags = kargs.gen.flags
	args.module = kargs.gen.module
	args.params = params
	args.aclpub = kargs.publicKey.acl.Data
	args.aclpriv = kargs.privateKey.acl.Data
	args.appdatapub = kargs.publicKey.appdata
	args.appdatapriv = kargs.privateKey.appdata

	reply, status := world.ssn.Transact(cmd)
	if status != C.Status_OK {
		return nil, nil, prettyError("Cmd_GenerateKeyPair", status)
	}

	rreply := (*C.M_Cmd_GenerateKeyPair_Reply)(unsafe.Pointer(&reply.reply))

	publicKey.Id = rreply.keypub
	publicKey.Cert = rreply.certpub
	privateKey.Id = rreply.keypriv
	privateKey.Cert = rreply.certpriv

	return &publicKey, &privateKey, nil
}

type GenerateKeyOptions struct {
	key KeyProperties
}

// Generates an AES key of bits length.
func GenerateAESKey(world *World, bits int, kargs GenerateKeyArgs) (*Key, error) {
	params := C.M_KeyGenParams{}
	params._type = C.KeyType_Rijndael

	gparams := (*C.M_KeyType_Random_GenParams)(unsafe.Pointer(&params.params))
	gparams.lenbytes = C.uint(bits / 8)

	return generateKey(world, kargs, params)
}
