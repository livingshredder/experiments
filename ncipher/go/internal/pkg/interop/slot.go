package interop

//#include <nfkm.h>
import "C"

// Represents a slot in a physical module
type Slot struct {
	ssn  *Session
	Data C.NFKM_SlotInfo
}
