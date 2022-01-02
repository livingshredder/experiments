package interop

//#include <nfkm.h>
import "C"
import (
	"unsafe"
)

// Converts enum value val to a string using the lookup table vit
func enumValToStr(val uint, vit unsafe.Pointer) string {
	result := C.NF_Lookup(C.uint(val), (*C.NF_ValInfo)(vit))
	if result == nil {
		return ""
	}

	return C.GoString(result)
}

// Converts symbol sym to a enum value using the lookup table vit
func enumValFromStr(sym string, vit unsafe.Pointer) *uint {
	result := C.M_Word(0)

	cstr := C.CString(sym)
	defer C.free(unsafe.Pointer(cstr))

	ret := C.NF_LookupString(cstr, &result, (*C.NF_ValInfo)(vit))
	if ret != 0 {
		return nil
	}

	rsv := uint(result)
	return &rsv
}
