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
	Hash   KeyHash
}

// Attributes on a key that are set at generation time
// and may be able to be changed throughout its lifecycle
type KeyProperties struct {
	// The key's access control list
	acl *ACL

	// Key-specific application data
	appdata *C.M_AppData
}

type KeyHash [20]byte

// Represents a key in the security world loaded onto a module
type Key struct {
	ssn *Session

	// Cached
	info  *KeyInfo
	props KeyProperties

	// Handle to this key in the security world
	Id   C.M_KeyID
	Cert *C.M_ModuleCert
}

// Retrieves the key info.
func (k *Key) GetInfo() (*KeyInfo, error) {
	if k.info != nil {
		return k.info, nil
	}

	info := KeyInfo{}

	cmd := C.M_Command{}
	cmd.cmd = C.Cmd_GetKeyInfoEx

	args := (*C.M_Cmd_GetKeyInfoEx_Args)(unsafe.Pointer(&cmd.args))
	args.key = k.Id

	reply, status := k.ssn.Transact(cmd)
	if status != C.Status_OK {
		return nil, fmt.Errorf("Cmd_GetKeyInfoEx failed: %d", status)
	}

	rreply := (*C.M_Cmd_GetKeyInfoEx_Reply)(unsafe.Pointer(&reply.reply))
	info.Type = rreply._type
	info.Length = int(rreply.length)
	info.Hash = KeyHash(rreply.hash)
	return &info, nil
}

// Returns the type of the key
func (k *Key) GetType() (*C.M_KeyType, error) {
	info, err := k.GetInfo()
	if err != nil {
		return nil, err
	}

	return &info.Type, nil
}

// Returns the length of the key in bits
func (k *Key) GetLength() (*int, error) {
	info, err := k.GetInfo()
	if err != nil {
		return nil, err
	}

	return &info.Length, nil
}

// Returns the hash of the key
func (k *Key) GetHash() (*KeyHash, error) {
	info, err := k.GetInfo()
	if err != nil {
		return nil, err
	}

	return &info.Hash, nil
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
		return nil, fmt.Errorf("Cmd_GetACL failed: %d", status)
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
		return fmt.Errorf("Cmd_SetACL failed: %d", status)
	}

	k.props.acl = &acl
	return nil
}

func (k *Key) String() string {
	return fmt.Sprintf("%d", k.Id)
}

//go:generate stringer -type=_Ctype_M_KeyType
func (k *Key) PrettyPrint() {
	info, err := k.GetInfo()
	if err != nil {
		log.Fatalf("Failed to get key info: %s", err)
	}

	fmt.Printf("KeyID: %#x\n", k.Id)
	fmt.Printf("  Hash: %x\n", info.Hash)
	fmt.Printf("  Length: %d\n", info.Length)
	fmt.Printf("  Type: %s\n", enumValToStr(uint(info.Type), unsafe.Pointer(&C.NF_KeyType_enumtable)))
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
	args.appdata = kargs.key.appdata

	reply, status := key.ssn.Transact(cmd)
	if status != C.Status_OK {
		return nil, fmt.Errorf("NFastApp_Transact failed: %d", status)
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
		return nil, nil, fmt.Errorf("NFastApp_Transact failed: %d", status)
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

func GenerateAESKey(world *World, length int, kargs GenerateKeyArgs) (*Key, error) {
	params := C.M_KeyGenParams{}
	params._type = C.KeyType_Rijndael

	gparams := (*C.M_KeyType_Random_GenParams)(unsafe.Pointer(&params.params))
	gparams.lenbytes = C.uint(length / 8)

	return generateKey(world, kargs, params)
}
