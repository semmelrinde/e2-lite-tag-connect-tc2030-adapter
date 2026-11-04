#!/usr/bin/env python3
"""Erzeugt den Schaltplan E2Lite_TC2030_Adapter_V1.kicad_sch.

Renesas E2 emulator Lite (RA, 20-pol. 1,27 mm ueber normales 20-pol. Flachbandkabel)
-> TC2030-IDC (2x3 2,54 mm) -> TC2030-Pad auf dem Zielboard (1,8-5,5 V).

Belegung E2-Seite: Renesas R20UT4686 Rev.3.60, Tabelle 2.3 (SWD).
Belegung TC2030-Seite: Standard 1 VTref, 2 SWDIO, 3 nRESET, 4 SWCLK, 5 GND, 6 SWO = TC2030-IDC Pin n.
Jedes Pin bekommt ein Label direkt am Pin-Ende, keine Draehte.
"""
import re
import sys
import uuid
from pathlib import Path

LIB = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
OUT = Path(__file__).resolve().parent.parent / "E2Lite_TC2030_Adapter_V1.kicad_sch"
PROJ = "E2Lite_TC2030_Adapter_V1"
SCH_UUID = "5e2c0a1d-7c3b-4f2e-9a61-2b1e0c7d4a11"


def uid(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{PROJ}/{tag}"))


def block(text, start):
    """Klammerblock ab Index start (zeigt auf '(')."""
    d = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "(":
            d += 1
        elif c == ")":
            d -= 1
            if d == 0:
                return text[start:i + 1]
    raise ValueError("Klammer offen")


_cache = {}


def lib_symbol(lib_id):
    lib, name = lib_id.split(":")
    if lib not in _cache:
        _cache[lib] = (LIB / f"{lib}.kicad_sym").read_text()
    text = _cache[lib]
    i = text.find(f'(symbol "{name}"')
    if i < 0:
        sys.exit(f"Symbol fehlt: {lib_id}")
    b = block(text, i)
    if "(extends " in b:
        sys.exit(f"Abgeleitetes Symbol nicht unterstuetzt: {lib_id}")
    return b.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)


def pins(lib_id):
    b = lib_symbol(lib_id)
    out = {}
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\).*?\(number "([^"]*)"', b, re.S):
        out[m.group(4)] = (float(m.group(1)), float(m.group(2)), int(float(m.group(3))))
    return out


def prop(name, value, x, y, hide=True, angle=0):
    h = "(hide yes)" if hide else ""
    return (f'(property "{name}" "{value}" (at {x:.2f} {y:.2f} {angle}) {h} '
            f'(show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))')


# ---------------------------------------------------------------- Bauteile
# Fassung zum Handloeten mit AliExpress-Teilen (4.11.2026): J1 = 20-pol. 1,27-mm-Wanne THT
# fuer ein normales 20-pol. 1,27-mm-Flachbandkabel; R/C 0603 mit Handloet-Pads.
# ref, lib_id, value, footprint, x, y, felder, pin->netz (None = no_connect)
FP_J1 = "E2L_TC:BoxHeader_2x10_P1.27mm_Vertical_DC3"
FP_J2 = "E2L_TC:IDC-Header_2x03_P2.54mm_Vertical"
FP_R = "E2L_TC:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder"
FP_C = "E2L_TC:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"
J1_NETZE = {"1": "VCC_E2", "2": "SWDIO_E", "3": "GND", "4": "SWCLK_E", "5": "GND", "9": "GND",
            "10": "RES_E", "15": "GND", "17": "GND", "19": "GND"}
TEILE = [
    ("J1", "Connector_Generic:Conn_02x10_Odd_Even", "E2 Lite 20-pol. 1,27 mm", FP_J1, 45.72, 76.20,
     {"MPN": "DC3 Wannenstecker 2x10 1,27 mm gerade THT", "Quelle": "AliExpress",
      "Datasheet": "https://www.renesas.com/en/document/mat/e2-emulator-e2-emulator-lite-additional-document-users-manual-notes-connection-ra-devices",
      "Description": "Renesas R20UT4686 Tab. 2.3: 1 VCC, 2 SWDIO, 3/5/15/17/19 GND, 4 SWCLK, 6 TxD9, 8 RxD9, 9 UCON (an GND), 10 RES#, Rest NC"},
     {str(n): J1_NETZE.get(str(n)) for n in range(1, 21)}),
    ("J2", "Connector_Generic:Conn_02x03_Odd_Even", "TC2030-IDC (2x3 Wanne)", FP_J2, 152.40, 76.20,
     {"MPN": "Wannenstecker 2x3 2,54 mm gerade THT", "Quelle": "AliExpress",
      "Description": "TC2030-IDC: 1 VTref, 2 SWDIO, 3 nRESET, 4 SWCLK, 5 GND, 6 SWO; Kerbe auf Seite 1/3/5"},
     {"1": "VCC_T", "2": "SWDIO_T", "3": "NRESET_T", "4": "SWCLK_T", "5": "GND", "6": None}),
    ("R1", "Device:R", "100", FP_R, 99.06, 63.50,
     {"MPN": "100 Ohm 0603", "Quelle": "eigener 0603-Satz",
      "Description": "SWDIO in Reihe: daempft das Kabel, begrenzt Strom bei falscher Emulator-Speisung"},
     {"1": "SWDIO_E", "2": "SWDIO_T"}),
    ("R2", "Device:R", "100", FP_R, 109.22, 63.50,
     {"MPN": "100 Ohm 0603", "Quelle": "eigener 0603-Satz", "Description": "SWCLK in Reihe"},
     {"1": "SWCLK_E", "2": "SWCLK_T"}),
    ("R3", "Device:R", "100", FP_R, 119.38, 63.50,
     {"MPN": "100 Ohm 0603", "Quelle": "eigener 0603-Satz", "Description": "RES# in Reihe"},
     {"1": "RES_E", "2": "NRESET_T"}),
    ("U1", "Power_Management:LM66100DCK", "LM66100DCKR", "E2L_TC:SOT-363_SC-70-6_HandSolder", 106.68, 101.60,
     {"MPN": "LM66100DCKR", "Manufacturer": "TI", "Quelle": "AliExpress",
      "Datasheet": "https://www.ti.com/lit/ds/symlink/lm66100.pdf",
      "Description": "Idealdiode, CE an VOUT (TI 8.3.2 Rueckstromsperre), ST an GND: Board-1V8 speist die E2-Puffer; sperrt sicher nur bei ausgeschaltetem Board"},
     {"1": "VCC_T", "2": "GND", "3": "VCC_E2", "4": None, "5": "GND", "6": "VCC_E2"}),
    ("C1", "Device:C", "100n", FP_C, 86.36, 101.60,
     {"MPN": "100 nF 0603", "Quelle": "eigener 0603-Satz", "Description": "VIN Idealdiode"},
     {"1": "VCC_T", "2": "GND"}),
    ("C2", "Device:C", "100n", FP_C, 127.00, 101.60,
     {"MPN": "100 nF 0603", "Quelle": "eigener 0603-Satz", "Description": "VCC E2-Puffer"},
     {"1": "VCC_E2", "2": "GND"}),
    ("C3", "Device:C", "1u", FP_C, 137.16, 101.60,
     {"MPN": "1 uF 0603", "Quelle": "eigener 0603-Satz", "Description": "VCC E2-Puffer, ca. 20 mA"},
     {"1": "VCC_E2", "2": "GND"}),
]
# SWO bleibt offen: E2 Lite hat kein SWO-Trace, Pin 6 ist dort TxD9 (SCI-Boot, ungenutzt).
# Messpunkte sind die sechs Loetstellen von J2 auf der Unterseite (beschriftet).
# PWR_FLAG fuer die extern gespeisten Netze
PWR = [("#FLG01", "GND", 60.96, 101.60), ("#FLG02", "VCC_T", 73.66, 101.60)]


def label(net, x, y, ang):
    just = "left bottom" if ang in (0, 90) else "right bottom"
    return (f'(label "{net}" (at {x:.2f} {y:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {just})) '
            f'(uuid "{uid("lab/" + net + f"/{x:.2f}/{y:.2f}")}"))')


def symbol_inst(ref, lib_id, value, fp, x, y, felder, dnp=False, in_bom=True):
    fl = dict(felder)
    ds = fl.pop("Datasheet", "")
    desc = fl.pop("Description", "")
    p = [prop("Reference", ref, x, y - 8.89, hide=ref.startswith("#")),
         prop("Value", value, x, y + 8.89, hide=ref.startswith("#")),
         prop("Footprint", fp, x, y), prop("Datasheet", ds, x, y), prop("Description", desc, x, y)]
    for k, v in fl.items():
        p.append(prop(k, v, x, y))
    pin_u = "".join(f'(pin "{n}" (uuid "{uid(ref + "/pin/" + n)}"))' for n in pins(lib_id))
    return (f'(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1) (body_style 1) (exclude_from_sim no) '
            f'(in_bom {"yes" if in_bom else "no"}) (on_board {"no" if ref.startswith("#") else "yes"}) '
            f'(in_pos_files yes) (dnp {"yes" if dnp else "no"}) (uuid "{uid("sym/" + ref)}") '
            + " ".join(p) + " " + pin_u +
            f'(instances (project "{PROJ}" (path "/{SCH_UUID}" (reference "{ref}") (unit 1)))))')


def main():
    used = sorted({t[1] for t in TEILE} | {"power:PWR_FLAG"})
    teile = []
    extras = []
    for ref, lib_id, value, fp, x, y, felder, netze in TEILE:
        teile.append(symbol_inst(ref, lib_id, value, fp, x, y, felder))
        pp = pins(lib_id)
        if set(netze) != set(pp):
            sys.exit(f"{ref}: Pins {sorted(pp)} != Zuordnung {sorted(netze)}")
        for num, net in netze.items():
            px, py, r = pp[num]
            sx, sy = x + px, y - py
            if net is None:
                extras.append(f'(no_connect (at {sx:.2f} {sy:.2f}) (uuid "{uid("nc/" + ref + num)}"))')
            else:
                extras.append(label(net, sx, sy, (r + 180) % 360))
    for ref, net, x, y in PWR:
        teile.append(symbol_inst(ref, "power:PWR_FLAG", "PWR_FLAG", "", x, y, {}, in_bom=False))
        px, py, r = pins("power:PWR_FLAG")["1"]
        extras.append(label(net, x + px, y - py, (r + 180) % 360))

    libs = "\n".join(lib_symbol(l) for l in used)
    s = f'''(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0")
(uuid "{SCH_UUID}") (paper "A4")
(title_block (title "E2 Lite (RA) -> TC2030-IDC Adapter V1") (date "2026-11-04") (rev "V1") (company "github.com/semmelrinde")
 (comment 1 "E2 Lite 20-pol. 1,27 mm -> Flachbandkabel 20-pol. (oder Renesas RTE0T00020KCAC0000J) -> J1; TC2030-IDC -> J2")
 (comment 2 "E2-Belegung: Renesas R20UT4686 Rev.3.60 Tab. 2.3; Ziel: TC2030-Pad, VTref 1,8-5,5 V")
 (comment 3 "U1 sperrt 3,3 V vom Emulator nur bei ausgeschaltetem Board sicher: im Werkzeug immer 'Power target: No'"))
(lib_symbols
{libs}
)
{chr(10).join(teile)}
{chr(10).join(extras)}
(sheet_instances (path "/" (page "1")))
(embedded_fonts no)
)
'''
    OUT.write_text(s)
    print("geschrieben:", OUT)


if __name__ == "__main__":
    main()
