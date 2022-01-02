package interop

//#include <nfkm.h>
import "C"
import "fmt"

// Represents an application session with the nCipher hardserver
type Session struct {
	app   C.NFast_AppHandle
	conn  C.NFastApp_Connection
	cctx  *C.struct_NFast_Call_Context
	world *World
}

func (s *Session) GetWorld() (*World, error) {
	if s.world != nil {
		return s.world, nil
	}

	world := World{ssn: s}
	status := C.NFKM_getinfo(s.app, &world.Data, nil)
	if status != C.Status_OK {
		return nil, fmt.Errorf("NFKM_getinfo failed: %d", status)
	}

	s.world = &world
	return s.world, nil
}

func (s *Session) Transact(cmd C.M_Command) (C.M_Reply, C.M_Status) {
	reply := C.M_Reply{}
	status := C.NFastApp_Transact(s.conn, s.cctx, &cmd, &reply, nil)
	return reply, C.M_Status(status)
}

func (s *Session) Close() {
	C.NFastApp_Finish(s.app, s.cctx)
}

func NewSession() (*Session, error) {
	session := Session{}
	status := C.M_Status(C.NFastApp_Init(&session.app, nil, nil, nil, nil))
	if status != C.Status_OK {
		return nil, fmt.Errorf("NFastApp_Init failed: %d", status)
	}

	status = C.M_Status(C.NFastApp_Connect(session.app, &session.conn, 0, nil))
	if status != C.Status_OK {
		return nil, fmt.Errorf("NFastApp_Connect failed: %d", status)
	}

	return &session, nil
}
