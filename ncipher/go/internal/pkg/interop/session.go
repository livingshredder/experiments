package interop

//#include <nfkm.h>
import "C"
import (
	"unsafe"
)

// Represents an application session with the nCipher hardserver
type Session struct {
	app  C.NFast_AppHandle
	conn C.NFastApp_Connection
	cctx *C.struct_NFast_Call_Context
}

// Retrieves the current security world information.
// Warning: this is usually a very slow call
func (s *Session) GetWorld() (*World, error) {
	var data *C.NFKM_WorldInfo
	status := C.NFKM_getinfo(s.app, &data, nil)
	if status != C.Status_OK {
		return nil, prettyError("NFKM_getinfo", status)
	}

	// Not cached, it's possible it could change
	result := NewWorld(s, data)
	return &result, nil
}

// Destroys the given KeyID
func (s *Session) Destroy(id C.M_KeyID) error {
	cmd := C.M_Command{cmd: C.Cmd_Destroy}
	(*C.M_Cmd_Destroy_Args)(unsafe.Pointer(&cmd.args)).key = id

	_, status := s.Transact(cmd)
	if status != C.Status_OK {
		return prettyError("Cmd_Destroy", status)
	}

	return nil
}

// Performs a command transaction
func (s *Session) Transact(cmd C.M_Command) (C.M_Reply, C.M_Status) {
	reply := C.M_Reply{}
	status := C.NFastApp_Transact(s.conn, s.cctx, &cmd, &reply, nil)
	return reply, C.M_Status(status)
}

// Closes the session
func (s *Session) Close() {
	C.NFastApp_Finish(s.app, s.cctx)
}

func NewSession() (*Session, error) {
	session := Session{}
	status := C.M_Status(C.NFastApp_Init(&session.app, nil, nil, nil, nil))
	if status != C.Status_OK {
		return nil, prettyError("NFastApp_Init", status)
	}

	status = C.M_Status(C.NFastApp_Connect(session.app, &session.conn, 0, nil))
	if status != C.Status_OK {
		return nil, prettyError("NFastApp_Connect", status)
	}

	return &session, nil
}
