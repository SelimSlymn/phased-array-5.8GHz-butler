# -*- coding: utf-8 -*-
# HFSS 1x8 patch sutunu - CST'deki tasarimin birebir aynisi
# F4BM265 (er=2.65, tand=0.001), h=0.8 mm, 5.8 GHz
# Calistirma: Automation -> Run Script  (ya da Tools -> Run Script)

import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()

def msg(t):
    try:
        oDesktop.AddMessage("", "", 0, "[script] " + t)
    except:
        pass

# ---------------- Proje ve tasarim ----------------
oProject = oDesktop.NewProject()
try:
    oProject.InsertDesign("HFSS", "sutun_1x8", "HFSS Modal Network", "")
except:
    oProject.InsertDesign("HFSS", "sutun_1x8", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("sutun_1x8")
oEditor = oDesign.SetActiveEditor("3D Modeler")
oEditor.SetModelUnits(["NAME:Units Parameter", "Units:=", "mm", "Rescale:=", False])

# ---------------- Degiskenler ----------------
def var(name, val):
    oDesign.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
        ["NAME:PropServers", "LocalVariables"],
        ["NAME:NewProps", ["NAME:" + name, "PropType:=", "VariableProp",
                           "UserDef:=", True, "Value:=", val]]]])

var("h", "0.8mm")
var("d", "25.9mm")
var("W", "19.1mm")
var("l", "15.02mm")
var("lf", "5mm")
var("y0", "5mm")
var("g", "0.8mm")
var("w50", "2.2mm")
var("w35", "3.61mm")
var("lam4", "8.61mm")
var("x1", "16mm")
var("x2", "x1+lam4")
var("x3", "x2+lam4")
var("x4", "x3+lam4")
var("yb", "-l/2-lf")
var("ls", "7*d+l+26mm")
var("xl", "-50mm")      # kartin sol kenari (port burada)
var("xr", "25mm")       # kartin sag kenari
var("pad", "13mm")      # hava kutusu payi (~lambda/4)
msg("Degiskenler tanimlandi")

# ---------------- Malzeme ----------------
oDef = oProject.GetDefinitionManager()
try:
    oDef.AddMaterial(["NAME:F4BM265", "CoordinateSystemType:=", "Cartesian",
        "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
        "permittivity:=", "2.65", "dielectric_loss_tangent:=", "0.001"])
    msg("F4BM265 malzemesi eklendi")
except:
    msg("F4BM265 zaten var")

# ---------------- Yardimci fonksiyonlar ----------------
def attrs(name, mat, color, transp, solve=True):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", color,
            "Transparency:=", transp, "PartCoordinateSystem:=", "Global", "UDMId:=", "",
            "MaterialValue:=", "\"" + mat + "\"", "SurfaceMaterialValue:=", "\"\"",
            "SolveInside:=", solve, "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False, "IsLightweight:=", False]

def box(name, x, y, z, dx, dy, dz, mat, color="(143 175 143)", transp=0.6):
    oEditor.CreateBox(["NAME:BoxParameters", "XPosition:=", x, "YPosition:=", y,
        "ZPosition:=", z, "XSize:=", dx, "YSize:=", dy, "ZSize:=", dz],
        attrs(name, mat, color, transp))

def rectz(name, x, y, z, wx, hy, color="(255 200 0)"):
    # Z eksenine dik levha: Width = X yonu, Height = Y yonu
    oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True,
        "XStart:=", x, "YStart:=", y, "ZStart:=", z,
        "Width:=", wx, "Height:=", hy, "WhichAxis:=", "Z"],
        attrs(name, "vacuum", color, 0))

def rectx(name, x, y, z, wy, hz):
    # X eksenine dik levha (port): Width = Y yonu, Height = Z yonu
    oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True,
        "XStart:=", x, "YStart:=", y, "ZStart:=", z,
        "Width:=", wy, "Height:=", hz, "WhichAxis:=", "X"],
        attrs(name, "vacuum", "(255 0 0)", 0))

# ---------------- Alt tas ve ground ----------------
box("Substrate", "xl", "-ls/2", "0mm", "xr-xl", "ls", "h", "F4BM265")
rectz("Ground", "xl", "-ls/2", "0mm", "xr-xl", "ls", "(200 120 50)")
msg("Alt tas ve ground cizildi")

# ---------------- 8 patch (inset beslemeli) ----------------
top = []
for k in range(8):
    yc = "(%g)*d" % (k - 3.5)
    p = "P%d" % k
    rectz(p, "-W/2", yc + "-l/2", "h", "W", "l")
    rectz(p + "_g1", "w50/2", yc + "-l/2", "h", "g", "y0")
    rectz(p + "_g2", "-w50/2-g", yc + "-l/2", "h", "g", "y0")
    oEditor.Subtract(["NAME:Selections", "Blank Parts:=", p,
                      "Tool Parts:=", p + "_g1," + p + "_g2"],
                     ["NAME:SubtractParameters", "KeepOriginals:=", False])
    # besleme sapi
    rectz(p + "_sap", "-w50/2", yc + "-l/2-lf", "h", "w50", "lf+y0")
    top += [p, p + "_sap"]
msg("8 patch cizildi")

# ---------------- Besleme agaci (corporate, 3 kademe) ----------------
# A: saplardan 1. kolona yatay 50 ohm hatlar
for k in range(8):
    s = "(%g)*d+yb" % (k - 3.5)
    n = "A%d" % k
    rectz(n, "-x1-w50/2", s + "-w50/2", "h", "x1+w50", "w50")
    top.append(n)
# B: 1. kolon dikey 50 ohm
for j in range(4):
    n = "B%d" % j
    rectz(n, "-x1-w50/2", "(%g)*d+yb" % (2 * j - 3.5), "h", "w50", "d")
    top.append(n)
# C: 1. kademe lambda/4 35.4 ohm
for j in range(4):
    n = "C%d" % j
    rectz(n, "-x2", "(%g)*d+yb-w35/2" % (2 * j - 3), "h", "lam4", "w35")
    top.append(n)
# D: 2. kolon dikey 50 ohm
for i in range(2):
    n = "D%d" % i
    rectz(n, "-x2-w50/2", "(%g)*d+yb" % (4 * i - 3), "h", "w50", "2*d")
    top.append(n)
# E: 2. kademe lambda/4
for i in range(2):
    n = "E%d" % i
    rectz(n, "-x3", "(%g)*d+yb-w35/2" % (4 * i - 2), "h", "lam4", "w35")
    top.append(n)
# F: 3. kolon dikey 50 ohm
rectz("F0", "-x3-w50/2", "-2*d+yb", "h", "w50", "4*d")
top.append("F0")
# G: son lambda/4
rectz("G0", "-x4", "yb-w35/2", "h", "lam4", "w35")
top.append("G0")
# H: port hatti (kart kenarina kadar)
rectz("H0", "xl", "yb-w50/2", "h", "-x4-xl", "w50")
top.append("H0")

oEditor.Unite(["NAME:Selections", "Selections:=", ",".join(top)],
              ["NAME:UniteParameters", "KeepOriginals:=", False])
oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab",
    ["NAME:PropServers", "P0"], ["NAME:ChangedProps", ["NAME:Name", "Value:=", "Top"]]]])
msg("Besleme agaci cizildi ve birlestirildi (Top)")

# ---------------- Hava kutusu ----------------
box("Airbox", "xl", "-ls/2-pad", "-pad", "xr-xl+pad", "ls+2*pad", "h+2*pad",
    "air", "(200 220 255)", 0.9)

# ---------------- Port levhasi ----------------
rectx("PortSheet", "xl", "yb-6mm", "0mm", "12mm", "5mm")

# ---------------- Sinir kosullari ----------------
oB = oDesign.GetModule("BoundarySetup")
for obj in ["Top", "Ground"]:
    try:
        oB.AssignFiniteCond(["NAME:Cu_" + obj, "Objects:=", [obj], "UseMaterial:=", True,
            "Material:=", "copper", "UseThickness:=", False, "Roughness:=", "0um",
            "InfGroundPlane:=", False, "IsTwoSided:=", False, "IsInternal:=", True])
    except:
        oB.AssignPerfectE(["NAME:PerfE_" + obj, "Objects:=", [obj], "InfGroundPlane:=", False])
        msg(obj + " icin PerfectE kullanildi")
oB.AssignRadiation(["NAME:Rad1", "Objects:=", ["Airbox"]])
oB.AssignWavePort(["NAME:1", "Objects:=", ["PortSheet"], "NumModes:=", 1,
    "UseLineModeAlignment:=", False, "DoDeembed:=", False,
    "RenormalizeAllTerminals:=", True,
    ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", False,
                    "AlignmentGroup:=", 0, "CharImp:=", "Zpi", "RenormImp:=", "50ohm"]],
    "ShowReporterFilter:=", False, "ReporterFilter:=", [True],
    "UseAnalyticAlignment:=", False])
msg("Bakir, radyasyon siniri ve wave port atandi")

# ---------------- Analiz ayarlari ----------------
oA = oDesign.GetModule("AnalysisSetup")
oA.InsertSetup("HfssDriven", ["NAME:Setup1", "Frequency:=", "5.8GHz",
    "MaxDeltaS:=", 0.02, "MaximumPasses:=", 15, "MinimumPasses:=", 2,
    "MinimumConvergedPasses:=", 2, "PercentRefinement:=", 30])
oA.InsertFrequencySweep("Setup1", ["NAME:Sweep", "IsEnabled:=", True,
    "RangeType:=", "LinearCount", "RangeStart:=", "5GHz", "RangeEnd:=", "6.6GHz",
    "RangeCount:=", 161, "Type:=", "Interpolating", "SaveFields:=", False])
msg("Setup1 (5.8 GHz) ve 5-6.6 GHz taramasi eklendi")

# ---------------- Uzak alan kuresi ----------------
try:
    oR = oDesign.GetModule("RadField")
    oR.InsertInfiniteSphereSetup(["NAME:Kure", "UseCustomRadiationSurface:=", False,
        "ThetaStart:=", "-180deg", "ThetaStop:=", "180deg", "ThetaStep:=", "1deg",
        "PhiStart:=", "0deg", "PhiStop:=", "90deg", "PhiStep:=", "90deg",
        "UseLocalCS:=", False])
    msg("Uzak alan kuresi eklendi (phi=0 ve phi=90)")
except:
    msg("Uzak alan kuresi elle eklenmeli")

oEditor.FitAll()
msg("BITTI - HFSS > Validation Check, sonra Analyze All")
