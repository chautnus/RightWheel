"""Windows Core Audio endpoint volume service via direct ctypes COM."""
from __future__ import annotations

import ctypes
from ctypes import wintypes

ole32 = ctypes.windll.ole32


class _GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, l: int, w1: int, w2: int, b: list[int]) -> None:
        super().__init__(l, w1, w2, (ctypes.c_ubyte * 8)(*b))


_CLSID_MMDeviceEnumerator = _GUID(0xBCDE0395, 0xE52F, 0x467C, [0x8E, 0x3D, 0xC4, 0x57, 0x92, 0x69, 0x2E])
_IID_IMMDeviceEnumerator  = _GUID(0xA95664D2, 0x9614, 0x4F35, [0xA7, 0x46, 0xDE, 0x8D, 0xB6, 0x36, 0x17, 0xE6])
_IID_IAudioEndpointVolume = _GUID(0x5CDF2C82, 0x841E, 0x4546, [0x97, 0x22, 0x0C, 0xF7, 0x40, 0x78, 0x22, 0x9A])


def _get_endpoint_volume():
    """Retrieve the master IAudioEndpointVolume interface pointer and vtable."""
    try:
        ole32.CoInitialize(None)
    except Exception:
        pass

    enumerator = ctypes.c_void_p()
    hr = ole32.CoCreateInstance(
        ctypes.byref(_CLSID_MMDeviceEnumerator),
        None,
        1,  # CLSCTX_INPROC_SERVER
        ctypes.byref(_IID_IMMDeviceEnumerator),
        ctypes.byref(enumerator),
    )
    if hr != 0 or not enumerator:
        return None, None

    enum_vtbl = ctypes.cast(
        ctypes.cast(enumerator, ctypes.POINTER(ctypes.c_void_p)).contents,
        ctypes.POINTER(ctypes.c_void_p),
    )
    get_def_proto = ctypes.WINFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)
    )
    get_def = get_def_proto(enum_vtbl[4])

    device = ctypes.c_void_p()
    # eRender = 0, eMultimedia = 1
    hr = get_def(enumerator, 0, 1, ctypes.byref(device))
    if hr != 0 or not device:
        return None, None

    dev_vtbl = ctypes.cast(
        ctypes.cast(device, ctypes.POINTER(ctypes.c_void_p)).contents,
        ctypes.POINTER(ctypes.c_void_p),
    )
    act_proto = ctypes.WINFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(_GUID), wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)
    )
    activate = act_proto(dev_vtbl[3])

    endpoint_vol = ctypes.c_void_p()
    hr = activate(device, ctypes.byref(_IID_IAudioEndpointVolume), 1, None, ctypes.byref(endpoint_vol))
    if hr != 0 or not endpoint_vol:
        return None, None

    vol_vtbl = ctypes.cast(
        ctypes.cast(endpoint_vol, ctypes.POINTER(ctypes.c_void_p)).contents,
        ctypes.POINTER(ctypes.c_void_p),
    )
    return endpoint_vol, vol_vtbl


def get_master_volume() -> float:
    """Return actual Windows master volume as a float between 0.0 and 1.0."""
    try:
        ep, vtbl = _get_endpoint_volume()
        if not ep or not vtbl:
            return 0.5
        proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float))
        get_vol = proto(vtbl[9])
        val = ctypes.c_float()
        if get_vol(ep, ctypes.byref(val)) == 0:
            return float(max(0.0, min(1.0, val.value)))
    except Exception:
        pass
    return 0.5


def set_master_volume(level: float) -> None:
    """Set actual Windows master volume to a float between 0.0 and 1.0."""
    try:
        ep, vtbl = _get_endpoint_volume()
        if not ep or not vtbl:
            return
        proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_float, ctypes.c_void_p)
        set_vol = proto(vtbl[7])
        f_val = ctypes.c_float(max(0.0, min(1.0, float(level))))
        set_vol(ep, f_val, None)
    except Exception:
        pass


def step_volume(delta: int, step: float = 0.05) -> float:
    """Adjust actual master volume by (delta * step) and return the new level."""
    cur = get_master_volume()
    target = max(0.0, min(1.0, cur + delta * step))
    set_master_volume(target)
    return target


def get_mute() -> bool:
    """Return True if system audio is muted."""
    try:
        ep, vtbl = _get_endpoint_volume()
        if not ep or not vtbl:
            return False
        proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(wintypes.BOOL))
        get_m = proto(vtbl[15])
        val = wintypes.BOOL()
        if get_m(ep, ctypes.byref(val)) == 0:
            return bool(val.value)
    except Exception:
        pass
    return False


def set_mute(mute: bool) -> None:
    """Mute or unmute system audio."""
    try:
        ep, vtbl = _get_endpoint_volume()
        if not ep or not vtbl:
            return
        proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, wintypes.BOOL, ctypes.c_void_p)
        set_m = proto(vtbl[14])
        set_m(ep, wintypes.BOOL(mute), None)
    except Exception:
        pass
