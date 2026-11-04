#!/usr/bin/env python3
"""Erzeugt E2Lite_TC2030_Adapter_V1.kicad_pcb (mit KiCad-Python ausfuehren).

2 Lagen, 26 x 19,5 mm, alle SMD-Teile oben, zum Handloeten; GND auf F.Cu und B.Cu.
Netze und Footprints kommen aus gen/netlist.xml (kicad-cli sch export netlist).
Routing von Hand nach WISSEN.md: Signale 0,15 mm (R3), VCC 0,3 mm, kein Via im Pad (R9),
GND-Inseln mit >= 2 Vias (K2), keine Referenzen im Silk (P12), Pin-1-Marke frei (P41).
"""
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew

P = Path(__file__).resolve().parent.parent
NAME = "E2Lite_TC2030_Adapter_V1"
LIBDIR = str(P / "lib" / "E2L_TC.pretty")
MM = pcbnew.FromMM

X0, Y0, W, H = 100.0, 100.0, 26.0, 19.5

# Fassung zum Handloeten (4.11.2026): J1 = 20-pol. 1,27-mm-Wanne THT, R/C 0603 Handloet-Pads,
# U1 SC-70-6 mit laengeren Pads. Nur die Leiterplatte kommt von JLC.
# Verkleinert (4.11.2026): U1 mit C1-C3 in die freie Flaeche unten Mitte, VCC_E2 und VCC_T
# laufen auf B.Cu; Silk ueberall >= 0,5 mm vom Rand.
# ref -> (x, y, Drehung)
PLATZ = {
    "J1": (104.2, 103.4, 0),
    "J2": (119.0, 106.21, 0),
    "R1": (110.0, 103.4, 0),
    "R2": (113.4, 104.67, 0),
    "R3": (110.0, 108.48, 0),
    "U1": (111.6, 113.6, 180),
    "C3": (109.0, 116.6, 270),
    "C2": (110.625, 116.6, 270),
    "C1": (113.6, 116.6, 270),
}

SIG, PWR = 0.15, 0.3
# (Netz, Lage, Breite, Punkte)
BAHNEN = [
    ("/SWDIO_E", "F.Cu", SIG, [(105.47, 103.4), (109.0875, 103.4)]),
    ("/SWDIO_T", "F.Cu", SIG, [(110.9125, 103.4), (121.54, 103.4), (121.54, 106.21)]),
    ("/SWCLK_E", "F.Cu", SIG, [(105.47, 104.67), (112.4875, 104.67)]),
    ("/SWCLK_T", "F.Cu", SIG, [(114.3125, 104.67), (114.6, 104.67), (117.41, 107.48), (120.27, 107.48), (121.54, 108.75)]),
    ("/RES_E", "F.Cu", SIG, [(105.47, 108.48), (109.0875, 108.48)]),
    ("/NRESET_T", "F.Cu", SIG, [(110.9125, 108.48), (116.4, 108.48), (116.67, 108.75), (119.0, 108.75)]),
    # VCC_T: J2.1 auf B.Cu zum Via an C1, dann F.Cu an U1-VIN
    ("/VCC_T", "B.Cu", PWR, [(119.0, 106.21), (117.0, 108.21), (117.0, 113.5875), (114.85, 115.7375)]),
    ("/VCC_T", "F.Cu", PWR, [(114.85, 115.7375), (113.6, 115.7375)]),
    ("/VCC_T", "F.Cu", PWR, [(113.6, 115.7375), (113.6, 114.25), (112.575, 114.25)]),
    # VCC_E2: U1-VOUT -> C2 -> C3 -> Via, auf B.Cu nach J1.1
    ("/VCC_E2", "F.Cu", PWR, [(110.625, 114.25), (110.625, 115.7375)]),
    ("/VCC_E2", "F.Cu", PWR, [(110.625, 115.7375), (109.0, 115.7375)]),
    ("/VCC_E2", "F.Cu", PWR, [(109.0, 115.7375), (109.0, 114.3)]),
    ("/VCC_E2", "B.Cu", PWR, [(109.0, 114.3), (107.4, 112.7), (107.4, 102.4), (104.2, 102.4), (104.2, 103.4)]),
    # U1: CE (3) an VCC_E2 = VOUT, Rueckstromsperre nach TI 8.3.2
    ("/VCC_E2", "F.Cu", PWR, [(112.575, 112.95), (112.575, 112.3), (109.0, 112.3), (109.0, 114.3)]),
    # U1: ST (5) unter dem Gehaeuse an GND (2), GND (2) zum Via
    ("/GND", "F.Cu", 0.2, [(110.625, 113.6), (112.575, 113.6)]),
    ("/GND", "F.Cu", PWR, [(112.575, 113.6), (114.3, 113.6)]),
    ("/GND", "F.Cu", PWR, [(109.0, 117.4625), (113.6, 117.4625)]),
    ("/GND", "F.Cu", PWR, [(112.1, 117.4625), (112.1, 118.45)]),
    # J1.3 hat oben VCC_E2 und rechts SWCLK als Nachbarn: direkt an J1.5 und zum Rand-Via
    ("/GND", "F.Cu", PWR, [(104.2, 104.67), (104.2, 105.94)]),
    ("/GND", "F.Cu", PWR, [(104.2, 104.67), (101.0, 104.67)]),
]
VIAS = [
    ("/VCC_T", 114.85, 115.7375), ("/VCC_E2", 109.0, 114.3),
    ("/GND", 114.3, 113.6), ("/GND", 112.1, 118.45),
    # Stitching
    ("/GND", 101.0, 101.3), ("/GND", 101.0, 104.67), ("/GND", 101.0, 108.5), ("/GND", 101.0, 112.5),
    ("/GND", 101.0, 117.5), ("/GND", 109.0, 106.5), ("/GND", 114.0, 107.0), ("/GND", 116.0, 110.6),
    ("/GND", 112.0, 101.6), ("/GND", 117.0, 101.6), ("/GND", 125.3, 102.0), ("/GND", 125.3, 109.0),
    ("/GND", 125.3, 116.0), ("/GND", 117.0, 117.3), ("/GND", 108.9, 118.75), ("/GND", 116.5, 116.0),
]
# Text, Lage, x, y, Groesse, Drehung, gespiegelt
TEXTE = [
    ("E2 Lite", "F.Silkscreen", 104.2, 118.15, 1.0, 0, False),
    ("TC2030-IDC", "F.Silkscreen", 120.3, 118.15, 1.0, 0, False),
    ("Power target: NO", "B.Silkscreen", 113.0, 101.45, 1.0, 0, True),
    ("E2L-TC V1  1V8 SWD", "B.Silkscreen", 113.0, 118.15, 1.0, 0, True),
    ("VT", "B.Silkscreen", 116.0, 106.21, 1.0, 0, True),
    ("RST", "B.Silkscreen", 115.7, 108.75, 1.0, 0, True),
    ("GND", "B.Silkscreen", 115.7, 111.29, 1.0, 0, True),
    ("DIO", "B.Silkscreen", 123.6, 106.21, 1.0, 0, True),
    ("CLK", "B.Silkscreen", 123.6, 108.75, 1.0, 0, True),
    ("nc", "B.Silkscreen", 123.3, 111.29, 1.0, 0, True),
]


STACKUP = """\t\t(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen") (color "White"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (color "Black") (thickness 0.01))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (color "Black") (thickness 0.01))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
\t\t\t(copper_finish "HAL lead-free")
\t\t\t(dielectric_constraints no)
\t\t)
"""


def netzliste():
    root = ET.parse(P / "gen" / "netlist.xml").getroot()
    teile = {}
    for c in root.find("components"):
        felder = {f.get("name"): (f.text or "") for f in c.find("fields")} if c.find("fields") is not None else {}
        felder["Datasheet"] = c.findtext("datasheet") or ""
        felder["Description"] = c.findtext("description") or ""
        teile[c.get("ref")] = dict(value=c.findtext("value"), fp=c.findtext("footprint"), felder=felder)
    pads = {}
    for n in root.find("nets"):
        for node in n:
            pads[(node.get("ref"), node.get("pin"))] = n.get("name")
    return teile, pads


def main():
    teile, pads = netzliste()
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(MM(1.6))

    netze = {}
    for name in sorted(set(pads.values())):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netze[name] = ni

    for ref in sorted(teile):
        t = teile[ref]
        lib, fpname = t["fp"].split(":")
        fp = pcbnew.FootprintLoad(LIBDIR, fpname)
        if fp is None:
            raise SystemExit(f"Footprint fehlt: {t['fp']}")
        fp.SetFPID(pcbnew.LIB_ID(lib, fpname))
        fp.SetReference(ref)
        fp.SetValue(t["value"])
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        for k in ("Datasheet", "Description", "MPN", "Manufacturer", "Quelle"):
            if t["felder"].get(k):
                fp.SetField(k, t["felder"][k])
                fp.GetField(k).SetVisible(False)
        x, y, rot = PLATZ[ref]
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            net = pads.get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(netze[net])

    # Umriss mit 1-mm-Ecken
    r = 1.0
    def seg(a, b):
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        board.Add(s)
    def bogen(c, a, ang):
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
        s.SetCenter(pcbnew.VECTOR2I(MM(c[0]), MM(c[1]))); s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
        board.Add(s)
    x1, y1, x2, y2 = X0, Y0, X0 + W, Y0 + H
    seg((x1 + r, y1), (x2 - r, y1)); seg((x2, y1 + r), (x2, y2 - r))
    seg((x2 - r, y2), (x1 + r, y2)); seg((x1, y2 - r), (x1, y1 + r))
    bogen((x2 - r, y1 + r), (x2 - r, y1), 90); bogen((x2 - r, y2 - r), (x2, y2 - r), 90)
    bogen((x1 + r, y2 - r), (x1 + r, y2), 90); bogen((x1 + r, y1 + r), (x1, y1 + r), 90)

    for net, lage, breite, pts in BAHNEN:
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            t.SetWidth(MM(breite)); t.SetLayer(board.GetLayerID(lage)); t.SetNet(netze[net])
            board.Add(t)
    for net, x, y in VIAS:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetNet(netze[net])
        board.Add(v)

    for lage in ("F.Cu", "B.Cu"):
        z = pcbnew.ZONE(board)
        z.SetLayer(board.GetLayerID(lage)); z.SetNet(netze["/GND"])
        z.SetLocalClearance(MM(0.2)); z.SetMinThickness(MM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
        z.SetThermalReliefGap(MM(0.3)); z.SetThermalReliefSpokeWidth(MM(0.4))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        o = z.Outline(); o.NewOutline()
        for px, py in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            o.Append(MM(px), MM(py))
        board.Add(z)

    for text, lage, x, y, gr, rot, spiegel in TEXTE:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text); t.SetLayer(board.GetLayerID(lage))
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetTextSize(pcbnew.VECTOR2I(MM(gr), MM(gr))); t.SetTextThickness(MM(0.15))
        t.SetTextAngleDegrees(rot); t.SetMirrored(spiegel)
        board.Add(t)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    # Save() legt eine Standard-.kicad_pro daneben (Autorouter CLAUDE.md): erst in build/, dann kopieren
    bau = P / "gen" / "build"
    bau.mkdir(exist_ok=True)
    board.Save(str(bau / f"{NAME}.kicad_pcb"))
    # Lagenaufbau schwarz/HASL von Hand einsetzen (Stackup ist in der Python-API nicht erreichbar).
    # WISSEN F5: 2 Lagen schwarz geht mit Economic-PCBA nur mit HASL.
    txt = (bau / f"{NAME}.kicad_pcb").read_text()
    if "(stackup" not in txt:
        txt = txt.replace("\t(setup\n", "\t(setup\n" + STACKUP, 1)
    (P / f"{NAME}.kicad_pcb").write_text(txt)
    print("geschrieben:", P / f"{NAME}.kicad_pcb")
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            p = pad.GetPosition()
            print(f"{fp.GetReference()}.{pad.GetNumber():>2} {pcbnew.ToMM(p.x):8.3f} {pcbnew.ToMM(p.y):8.3f} {pad.GetNetname()}")


if __name__ == "__main__":
    main()
