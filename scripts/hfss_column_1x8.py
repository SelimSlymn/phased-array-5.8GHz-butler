# -*- coding: utf-8 -*-
# HFSS 1x8 patch column - early corporate-fed (inset-fed patches) variant,
# explored before the final series-fed column was chosen
# F4BM265 (er=2.65, tand=0.001), h=0.8 mm, 5.8 GHz
# Run: Automation -> Run Script  (or Tools -> Run Script)

import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()

def msg(t):
    try:
        oDesktop.AddMessage("", "", 0, "[script] " + t)
    except:
        pass

# ---------------- Project and design ----------------
oProject = oDesktop.NewProject()
try:
    oProject.InsertDesign("HFSS", "column_1x8", "HFSS Modal Network", "")
except:
    oProject.InsertDesign("HFSS", "column_1x8", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("column_1x8")
oEditor = oDesign.SetActiveEditor("3D Modeler")
oEditor.SetModelUnits(["NAME:Units Parameter", "Units:=", "mm", "Rescale:=", False])

# ---------------- Variables ----------------
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
var("xl", "-50mm")      # left edge of the board (port here)
var("xr", "25mm")       # right edge of the board
var("pad", "13mm")      # air box margin (~lambda/4)
msg("Variables defined")

# ---------------- Material ----------------
oDef = oProject.GetDefinitionManager()
try:
    oDef.AddMaterial(["NAME:F4BM265", "CoordinateSystemType:=", "Cartesian",
        "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
        "permittivity:=", "2.65", "dielectric_loss_tangent:=", "0.001"])
    msg("F4BM265 material added")
except:
    msg("F4BM265 already exists")

# ---------------- Helper functions ----------------
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
    # sheet normal to Z: Width = X direction, Height = Y direction
    oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True,
        "XStart:=", x, "YStart:=", y, "ZStart:=", z,
        "Width:=", wx, "Height:=", hy, "WhichAxis:=", "Z"],
        attrs(name, "vacuum", color, 0))

def rectx(name, x, y, z, wy, hz):
    # sheet normal to X (port): Width = Y direction, Height = Z direction
    oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True,
        "XStart:=", x, "YStart:=", y, "ZStart:=", z,
        "Width:=", wy, "Height:=", hz, "WhichAxis:=", "X"],
        attrs(name, "vacuum", "(255 0 0)", 0))

# ---------------- Substrate and ground ----------------
box("Substrate", "xl", "-ls/2", "0mm", "xr-xl", "ls", "h", "F4BM265")
rectz("Ground", "xl", "-ls/2", "0mm", "xr-xl", "ls", "(200 120 50)")
msg("Substrate and ground drawn")

# ---------------- 8 patches (inset-fed) ----------------
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
    # feed stub
    rectz(p + "_stub", "-w50/2", yc + "-l/2-lf", "h", "w50", "lf+y0")
    top += [p, p + "_stub"]
msg("8 patches drawn")

# ---------------- Feed tree (corporate, 3 stages) ----------------
# A: horizontal 50 ohm lines from the stubs to the first branch
for k in range(8):
    s = "(%g)*d+yb" % (k - 3.5)
    n = "A%d" % k
    rectz(n, "-x1-w50/2", s + "-w50/2", "h", "x1+w50", "w50")
    top.append(n)
# B: first branch, vertical 50 ohm
for j in range(4):
    n = "B%d" % j
    rectz(n, "-x1-w50/2", "(%g)*d+yb" % (2 * j - 3.5), "h", "w50", "d")
    top.append(n)
# C: stage 1 quarter-wave, 35.4 ohm
for j in range(4):
    n = "C%d" % j
    rectz(n, "-x2", "(%g)*d+yb-w35/2" % (2 * j - 3), "h", "lam4", "w35")
    top.append(n)
# D: second branch, vertical 50 ohm
for i in range(2):
    n = "D%d" % i
    rectz(n, "-x2-w50/2", "(%g)*d+yb" % (4 * i - 3), "h", "w50", "2*d")
    top.append(n)
# E: stage 2 quarter-wave
for i in range(2):
    n = "E%d" % i
    rectz(n, "-x3", "(%g)*d+yb-w35/2" % (4 * i - 2), "h", "lam4", "w35")
    top.append(n)
# F: third branch, vertical 50 ohm
rectz("F0", "-x3-w50/2", "-2*d+yb", "h", "w50", "4*d")
top.append("F0")
# G: last quarter-wave
rectz("G0", "-x4", "yb-w35/2", "h", "lam4", "w35")
top.append("G0")
# H: port line (to the board edge)
rectz("H0", "xl", "yb-w50/2", "h", "-x4-xl", "w50")
top.append("H0")

oEditor.Unite(["NAME:Selections", "Selections:=", ",".join(top)],
              ["NAME:UniteParameters", "KeepOriginals:=", False])
oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab",
    ["NAME:PropServers", "P0"], ["NAME:ChangedProps", ["NAME:Name", "Value:=", "Top"]]]])
msg("Feed tree drawn and united (Top)")

# ---------------- Air box ----------------
box("Airbox", "xl", "-ls/2-pad", "-pad", "xr-xl+pad", "ls+2*pad", "h+2*pad",
    "air", "(200 220 255)", 0.9)

# ---------------- Port sheet ----------------
rectx("PortSheet", "xl", "yb-6mm", "0mm", "12mm", "5mm")

# ---------------- Boundary conditions ----------------
oB = oDesign.GetModule("BoundarySetup")
for obj in ["Top", "Ground"]:
    try:
        oB.AssignFiniteCond(["NAME:Cu_" + obj, "Objects:=", [obj], "UseMaterial:=", True,
            "Material:=", "copper", "UseThickness:=", False, "Roughness:=", "0um",
            "InfGroundPlane:=", False, "IsTwoSided:=", False, "IsInternal:=", True])
    except:
        oB.AssignPerfectE(["NAME:PerfE_" + obj, "Objects:=", [obj], "InfGroundPlane:=", False])
        msg("PerfectE used for " + obj)
oB.AssignRadiation(["NAME:Rad1", "Objects:=", ["Airbox"]])
oB.AssignWavePort(["NAME:1", "Objects:=", ["PortSheet"], "NumModes:=", 1,
    "UseLineModeAlignment:=", False, "DoDeembed:=", False,
    "RenormalizeAllTerminals:=", True,
    ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", False,
                    "AlignmentGroup:=", 0, "CharImp:=", "Zpi", "RenormImp:=", "50ohm"]],
    "ShowReporterFilter:=", False, "ReporterFilter:=", [True],
    "UseAnalyticAlignment:=", False])
msg("Copper, radiation boundary and wave port assigned")

# ---------------- Analysis setup ----------------
oA = oDesign.GetModule("AnalysisSetup")
oA.InsertSetup("HfssDriven", ["NAME:Setup1", "Frequency:=", "5.8GHz",
    "MaxDeltaS:=", 0.02, "MaximumPasses:=", 15, "MinimumPasses:=", 2,
    "MinimumConvergedPasses:=", 2, "PercentRefinement:=", 30])
oA.InsertFrequencySweep("Setup1", ["NAME:Sweep", "IsEnabled:=", True,
    "RangeType:=", "LinearCount", "RangeStart:=", "5GHz", "RangeEnd:=", "6.6GHz",
    "RangeCount:=", 161, "Type:=", "Interpolating", "SaveFields:=", False])
msg("Setup1 (5.8 GHz) and 5-6.6 GHz sweep added")

# ---------------- Farfield sphere ----------------
try:
    oR = oDesign.GetModule("RadField")
    oR.InsertInfiniteSphereSetup(["NAME:Sphere", "UseCustomRadiationSurface:=", False,
        "ThetaStart:=", "-180deg", "ThetaStop:=", "180deg", "ThetaStep:=", "1deg",
        "PhiStart:=", "0deg", "PhiStop:=", "90deg", "PhiStep:=", "90deg",
        "UseLocalCS:=", False])
    msg("Farfield sphere added (phi=0 and phi=90)")
except:
    msg("Farfield sphere must be added manually")

oEditor.FitAll()
msg("DONE - HFSS > Validation Check, then Analyze All")
