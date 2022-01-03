package interop

//#include <nfkm.h>
import "C"
import "unsafe"

// Represents a physical module in the security world
type Module struct {
	ssn  *Session
	Data C.NFKM_ModuleInfo

	// data extracted from Data section
	Slots []Slot
}

func NewModule(ssn *Session, data C.NFKM_ModuleInfo) Module {
	module := Module{ssn: ssn, Data: data}

	// Build the slots attribute
	if module.Data.slots != nil {
		len := module.Data.n_slots
		result := []Slot{}
		data := (*[1 << 28]C.NFKM_opt_SlotInfo)(unsafe.Pointer(module.Data.slots))[:len:len]

		for i := range data {
			if data[i] != nil {
				result = append(result, Slot{ssn: module.ssn, Data: *data[i]})
			}
		}

		module.Slots = result
	}

	return module
}
