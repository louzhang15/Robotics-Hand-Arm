"""Basic mesh topology/dimension checks. No fit, slicer or strength certification."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import struct


def triangles(path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0] if len(data) >= 84 else 0
    if len(data) == 84 + 50 * count:
        for offset in range(84, len(data), 50):
            values = struct.unpack_from("<12fH", data, offset)
            yield [tuple(round(v, 6) for v in values[i:i + 3]) for i in (3, 6, 9)]
    else:
        vertices = [tuple(float(v) for v in line.split())
                    for line in re.findall(r"\bvertex\s+([^\r\n]+)", data.decode("ascii"))]
        if len(vertices) % 3 or any(len(v) != 3 for v in vertices):
            raise ValueError(f"Invalid ASCII triangle list: {path}")
        for i in range(0, len(vertices), 3):
            yield [tuple(round(v, 6) for v in vertex) for vertex in vertices[i:i + 3]]


def inspect(path):
    faces = list(triangles(path))
    if not faces:
        raise ValueError(f"Empty mesh: {path}")
    edges = Counter()
    directed = Counter()
    vertices = set()
    parents = {}
    degenerate = 0
    signed_volume = 0

    def find(v):
        parents.setdefault(v, v)
        while parents[v] != v:
            parents[v] = parents[parents[v]]
            v = parents[v]
        return v

    for a, b, c in faces:
        vertices.update((a, b, c))
        ab, ac = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        cross = (ab[1]*ac[2] - ab[2]*ac[1], ab[2]*ac[0] - ab[0]*ac[2], ab[0]*ac[1] - ab[1]*ac[0])
        if sum(v*v for v in cross) < 1e-16:
            degenerate += 1
        signed_volume += sum(a[i] * (b[(i+1)%3]*c[(i+2)%3] - b[(i+2)%3]*c[(i+1)%3]) for i in range(3)) / 6
        for u, v in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted((u, v)))] += 1
            directed[(u, v)] += 1
            parents[find(u)] = find(v)
    extents = [round(max(v[i] for v in vertices) - min(v[i] for v in vertices), 4) for i in range(3)]
    return {"file": path.as_posix(), "triangles": len(faces), "extents_mm": extents,
            "fits_256mm_cube": all(v <= 256 for v in extents),
            "components": len({find(v) for v in vertices}),
            "boundary_edges": sum(n == 1 for n in edges.values()),
            "nonmanifold_edges": sum(n > 2 for n in edges.values()),
            "winding_errors": sum(directed[(a,b)] != directed[(b,a)] for a,b in edges),
            "degenerate_faces": degenerate, "signed_volume_mm3": round(signed_volume, 2)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args()
    reports = [inspect(path) for path in args.paths]
    print(json.dumps(reports, indent=2))
    if any(r["boundary_edges"] or r["nonmanifold_edges"] or r["winding_errors"]
           or r["degenerate_faces"] or not r["fits_256mm_cube"] for r in reports):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
