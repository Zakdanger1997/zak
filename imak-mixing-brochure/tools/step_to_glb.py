#!/usr/bin/env python3
"""Convert an i.Mak STEP model (from i-Guide) to GLB for Blender, keeping parts and colours.

Usage: python3 tools/step_to_glb.py model.step out.glb [--deflection 0.4]
Needs `cadquery-ocp` (pip install cadquery-ocp). Units stay in millimetres.
"""
import sys

from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.IFSelect import IFSelect_RetDone
from OCP.Message import Message_ProgressRange
from OCP.RWGltf import RWGltf_CafWriter
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCP.collections import IndexedDataMap_TCollection_AsciiString_TCollection_AsciiString as FileInfo
from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool


def main(src, dst, deflection=0.4):
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    r = STEPCAFControl_Reader()
    r.SetColorMode(True)
    r.SetNameMode(True)
    if r.ReadFile(src) != IFSelect_RetDone:
        sys.exit("cannot read " + src)
    r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    labels = TDF_LabelSequence()
    st.GetFreeShapes(labels)
    for i in range(1, labels.Length() + 1):
        shape = st.GetShape_s(labels.Value(i))
        BRepMesh_IncrementalMesh(shape, deflection, False, 0.35, True)
    w = RWGltf_CafWriter(TCollection_AsciiString(dst), True)
    w.Perform(doc, FileInfo(), Message_ProgressRange())
    print("wrote", dst, "free shapes", labels.Length())


if __name__ == "__main__":
    d = float(sys.argv[sys.argv.index("--deflection") + 1]) if "--deflection" in sys.argv else 0.4
    main(sys.argv[1], sys.argv[2], d)
