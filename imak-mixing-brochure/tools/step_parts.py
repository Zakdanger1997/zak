#!/usr/bin/env python3
"""Split an i.Mak STEP envelope model into paint / steel / bore meshes for rendering.

Usage: python3 tools/step_parts.py model.step OUTDIR/name [--deflection 0.3]
Writes  name_paint.stl   housing and everything else (rendered i.Mak red)
        name_steel.stl   convex cylinders and cones up to a radius limit (shafts, rendered bright steel)
        name_bore.stl    concave cylinders (bores, hollow shafts, rendered machined grey)
        name.json        bounding box and every shaft cylinder (axis, centre, radius, length) in mm
Needs cadquery-ocp. Coordinates stay in the STEP's millimetres.
"""
import json
import sys

from OCP.BRep import BRep_Builder
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp, BRepGProp_Face
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Bnd import Bnd_Box
from OCP.GeomAbs import GeomAbs_Cone, GeomAbs_Cylinder
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Compound
from OCP.gp import gp_Pnt, gp_Vec


def main(src, out, defl=0.3):
    r = STEPControl_Reader()
    if r.ReadFile(src) != IFSelect_RetDone:
        sys.exit("cannot read " + src)
    r.TransferRoots()
    shape = r.OneShape()
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    x0, y0, z0 = box.GetXMin(), box.GetYMin(), box.GetZMin()
    x1, y1, z1 = box.GetXMax(), box.GetYMax(), box.GetZMax()
    maxdim = max(x1 - x0, y1 - y0, z1 - z0)
    rmax = 0.085 * maxdim
    BRepMesh_IncrementalMesh(shape, defl, False, 0.3, True)

    b = BRep_Builder()
    comps = {k: TopoDS_Compound() for k in ("paint", "steel", "bore")}
    for c in comps.values():
        b.MakeCompound(c)
    shafts = []
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face(ex.Current())
        s = BRepAdaptor_Surface(f)
        kind = "paint"
        t = s.GetType()
        if t in (GeomAbs_Cylinder, GeomAbs_Cone):
            if t == GeomAbs_Cylinder:
                cyl = s.Cylinder()
                rad = cyl.Radius()
                ax = cyl.Axis()
            else:
                cone = s.Cone()
                rad = cone.RefRadius()
                ax = cone.Axis()
            u = (s.FirstUParameter() + s.LastUParameter()) / 2
            v = (s.FirstVParameter() + s.LastVParameter()) / 2
            p = gp_Pnt()
            n = gp_Vec()
            BRepGProp_Face(f).Normal(u, v, p, n)       # accounts for face orientation
            loc = ax.Location()
            d = ax.Direction()
            w = gp_Vec(loc, p)
            radial = w - gp_Vec(d) * w.Dot(gp_Vec(d))
            convex = radial.Magnitude() > 1e-9 and radial.Dot(n) > 0
            span = abs(s.LastUParameter() - s.FirstUParameter())   # angular extent of the surface
            if convex and rad <= rmax and span > 0.9 * 3.14159:
                kind = "steel"
                if t == GeomAbs_Cylinder:
                    g = GProp_GProps()
                    BRepGProp.SurfaceProperties_s(f, g)
                    c = g.CentreOfMass()
                    shafts.append({"r": round(rad, 2), "axis": [round(d.X(), 3), round(d.Y(), 3), round(d.Z(), 3)],
                                   "c": [round(c.X(), 1), round(c.Y(), 1), round(c.Z(), 1)],
                                   "area": round(g.Mass(), 1)})
            elif not convex and span > 0.9 * 3.14159:
                kind = "bore"
        b.Add(comps[kind], f)
        ex.Next()
    for k, c in comps.items():
        w = StlAPI_Writer()
        w.ASCIIMode = False
        w.Write(c, f"{out}_{k}.stl")
    shafts.sort(key=lambda s: -s["area"])
    json.dump({"bbox": [x0, y0, z0, x1, y1, z1], "shafts": shafts[:12]}, open(out + ".json", "w"), indent=1)
    print(out, "bbox mm", [round(v) for v in (x1 - x0, y1 - y0, z1 - z0)], "shafts", len(shafts))


if __name__ == "__main__":
    d = float(sys.argv[sys.argv.index("--deflection") + 1]) if "--deflection" in sys.argv else 0.3
    main(sys.argv[1], sys.argv[2], d)
