#!/usr/bin/env python3
"""Square face crops for the round portraits: assets/faces/<slug>.jpg -> assets/faces_c/<slug>.jpg (OpenCV YuNet face detector,
model face_detection_yunet_2023mar.onnx from huggingface.co/opencv/face_detection_yunet, path in $YUNET;
the face fills ~42% of the crop, a bit above centre). Falls back to a top-weighted square crop when no face is found."""
import glob
import os

import cv2

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MODEL = os.environ.get("YUNET", "/tmp/claude-0/models/yunet.onnx")
for f in sorted(glob.glob(os.path.join(ROOT, "assets", "faces", "*.jpg"))):
    im = cv2.imread(f); h, w = im.shape[:2]
    det = cv2.FaceDetectorYN.create(MODEL, "", (w, h), 0.7)
    faces = det.detect(im)[1]
    faces = [] if faces is None else [r[:4].astype(int) for r in faces]
    if len(faces):
        x, y, fw, fh = max(faces, key=lambda r: r[2] * r[3])
        side = min(int(fw / .42), w, h); cx, cy = x + fw / 2, y + fh / 2 + fh * .25
    else:
        side = min(w, h); cx, cy = w / 2, side / 2
    x0 = int(min(max(cx - side / 2, 0), w - side)); y0 = int(min(max(cy - side / 2, 0), h - side))
    out = cv2.resize(im[y0:y0 + side, x0:x0 + side], (600, 600), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(os.path.join(ROOT, "assets", "faces_c", os.path.basename(f)), out, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"{os.path.basename(f):26s} {'face' if len(faces) else 'NO FACE'} side={side}")
