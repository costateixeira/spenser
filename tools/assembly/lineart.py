"""Hidden-line drawings of STL parts, written as SVG. Standard library only.

An edge is drawn when it is sharp, or when it is on the outline of the part from
where the viewer stands. A depth buffer decides which stretches of each edge can
actually be seen.
"""

import math
import struct

SHARP_DEGREES = 32
WELD = 1000.0  # vertices closer than 1/1000 mm are the same vertex


# ------------------------------------------------------------------- vectors

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    length = math.sqrt(dot(a, a)) or 1.0
    return (a[0] / length, a[1] / length, a[2] / length)


# -------------------------------------------------------------------- meshes

class Mesh:
    """Welded triangles, with the edges that could ever be worth drawing."""

    def __init__(self, triangles):
        self.vertices = []
        self.triangles = []
        index = {}
        for triangle in triangles:
            ids = []
            for point in triangle:
                key = tuple(round(c * WELD) for c in point)
                if key not in index:
                    index[key] = len(self.vertices)
                    self.vertices.append(tuple(point))
                ids.append(index[key])
            if len(set(ids)) == 3:
                self.triangles.append(tuple(ids))

        self.normals = []
        adjacent = {}
        for number, (a, b, c) in enumerate(self.triangles):
            va, vb, vc = self.vertices[a], self.vertices[b], self.vertices[c]
            self.normals.append(norm(cross(sub(vb, va), sub(vc, va))))
            for u, v in ((a, b), (b, c), (c, a)):
                adjacent.setdefault((min(u, v), max(u, v)), []).append(number)

        limit = math.cos(math.radians(SHARP_DEGREES))
        self.sharp = []
        self.smooth = []
        for edge, faces in adjacent.items():
            if len(faces) == 2:
                if dot(self.normals[faces[0]], self.normals[faces[1]]) < limit:
                    self.sharp.append(edge)
                elif dot(self.normals[faces[0]], self.normals[faces[1]]) < 0.99999:
                    self.smooth.append((edge, faces))
            else:
                self.sharp.append(edge)


def load_stl(path):
    data = open(path, 'rb').read()
    count = struct.unpack('<I', data[80:84])[0]
    triangles = []
    for i in range(count):
        offset = 84 + 50 * i + 12
        triangles.append([struct.unpack('<3f', data[offset + 12 * j:offset + 12 * j + 12]) for j in range(3)])
    return Mesh(triangles)


def box(x0, x1, y0, y1, z0, z1):
    p = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return [[p[a], p[b], p[c]] for a, b, c, d in quads] + [[p[a], p[c], p[d]] for a, b, c, d in quads]


def cylinder(cx, cy, z0, z1, radius, segments=40):
    triangles = []
    for i in range(segments):
        t0 = 2 * math.pi * i / segments
        t1 = 2 * math.pi * (i + 1) / segments
        a = (cx + radius * math.cos(t0), cy + radius * math.sin(t0))
        b = (cx + radius * math.cos(t1), cy + radius * math.sin(t1))
        triangles.append([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1)])
        triangles.append([(a[0], a[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)])
        triangles.append([(cx, cy, z1), (a[0], a[1], z1), (b[0], b[1], z1)])
        triangles.append([(cx, cy, z0), (b[0], b[1], z0), (a[0], a[1], z0)])
    return triangles


def mesh_of(*shapes):
    return Mesh([triangle for shape in shapes for triangle in shape])


# ---------------------------------------------------------------- transforms

def rotate_z(degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def rotate_x(degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return ((1, 0, 0), (0, c, -s), (0, s, c))


def rotate_y(degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return ((c, 0, s), (0, 1, 0), (-s, 0, c))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def place(mesh, rotation=IDENTITY, move=(0, 0, 0), about=(0, 0, 0)):
    """A copy of the mesh's vertices: rotated about a point, then moved."""
    result = []
    for v in mesh.vertices:
        d = sub(v, about)
        result.append((
            rotation[0][0] * d[0] + rotation[0][1] * d[1] + rotation[0][2] * d[2] + about[0] + move[0],
            rotation[1][0] * d[0] + rotation[1][1] * d[1] + rotation[1][2] * d[2] + about[1] + move[1],
            rotation[2][0] * d[0] + rotation[2][1] * d[1] + rotation[2][2] * d[2] + about[2] + move[2],
        ))
    return result


class Camera:
    """Orthographic. Screen x runs right, screen y runs down, depth runs towards the viewer."""

    def __init__(self, azimuth=35.0, elevation=28.0):
        az, el = math.radians(azimuth), math.radians(elevation)
        self.right = (math.cos(az), math.sin(az), 0.0)
        self.toward = (math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))
        self.up = cross(self.toward, self.right)
        self.up = (-self.up[0], -self.up[1], -self.up[2]) if self.up[2] < 0 else self.up

    def project(self, p):
        return (dot(p, self.right), -dot(p, self.up), dot(p, self.toward))


# -------------------------------------------------------------------- drawing

class Drawing:
    """Parts placed in a scene, rendered to visible line segments."""

    def __init__(self, camera, width=800, height=600, margin=30):
        self.camera = camera
        self.width, self.height, self.margin = width, height, margin
        self.parts = []

    def add(self, mesh, rotation=IDENTITY, move=(0, 0, 0), about=(0, 0, 0), weight=1.6, ghost=False):
        self.parts.append(dict(mesh=mesh, world=place(mesh, rotation, move, about), weight=weight, ghost=ghost))
        return self

    def _fit(self, extra=()):
        points = [self.camera.project(p) for part in self.parts for p in part['world']]
        points += [self.camera.project(p) for p in extra]
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        span_x, span_y = (max(xs) - min(xs)) or 1, (max(ys) - min(ys)) or 1
        scale = min((self.width - 2 * self.margin) / span_x, (self.height - 2 * self.margin) / span_y)
        self.scale = scale
        self.ox = (self.width - scale * (max(xs) + min(xs))) / 2
        self.oy = (self.height - scale * (max(ys) + min(ys))) / 2

    def to_screen(self, p):
        x, y, z = self.camera.project(p)
        return (self.ox + self.scale * x, self.oy + self.scale * y, z)

    def _depth_buffer(self, factor):
        w, h = int(self.width * factor), int(self.height * factor)
        depth = [None] * (w * h)
        for part in self.parts:
            if part['ghost']:
                continue
            screen = [self.to_screen(p) for p in part['world']]
            for a, b, c in part['mesh'].triangles:
                ax, ay, az = screen[a][0] * factor, screen[a][1] * factor, screen[a][2]
                bx, by, bz = screen[b][0] * factor, screen[b][1] * factor, screen[b][2]
                cx, cy, cz = screen[c][0] * factor, screen[c][1] * factor, screen[c][2]
                area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
                if abs(area) < 1e-9:
                    continue
                x0, x1 = max(0, int(min(ax, bx, cx))), min(w - 1, int(max(ax, bx, cx)) + 1)
                y0, y1 = max(0, int(min(ay, by, cy))), min(h - 1, int(max(ay, by, cy)) + 1)
                for y in range(y0, y1 + 1):
                    row = y * w
                    for x in range(x0, x1 + 1):
                        l0 = ((bx - x) * (cy - y) - (by - y) * (cx - x)) / area
                        l1 = ((cx - x) * (ay - y) - (cy - y) * (ax - x)) / area
                        l2 = 1 - l0 - l1
                        if l0 < -0.001 or l1 < -0.001 or l2 < -0.001:
                            continue
                        z = l0 * az + l1 * bz + l2 * cz
                        here = depth[row + x]
                        if here is None or z > here:
                            depth[row + x] = z
        return depth, w, h

    def visible_lines(self, factor=2):
        depth, w, h = self._depth_buffer(factor)
        tolerance = 0.3 + 1.0 / self.scale

        def can_see(x, y, z):
            # Seen if any neighbouring pixel leaves it unobstructed. Comparing
            # against the nearest neighbour instead would hide every outline on
            # a surface seen at a grazing angle, where depth changes fastest.
            px, py = int(round(x * factor)), int(round(y * factor))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    qx, qy = px + dx, py + dy
                    if 0 <= qx < w and 0 <= qy < h:
                        d = depth[qy * w + qx]
                        if d is None or z >= d - tolerance:
                            return True
            return False

        toward = self.camera.toward
        output = []
        for part in self.parts:
            mesh = part['mesh']
            world = part['world']
            screen = [self.to_screen(p) for p in world]
            edges = list(mesh.sharp)
            for edge, faces in mesh.smooth:
                n = []
                for f in faces:
                    a, b, c = (world[i] for i in mesh.triangles[f])
                    n.append(dot(cross(sub(b, a), sub(c, a)), toward))
                if (n[0] > 0) != (n[1] > 0):
                    edges.append(edge)
            segments = []
            for u, v in edges:
                a, b = screen[u], screen[v]
                length = math.hypot(b[0] - a[0], b[1] - a[1])
                if length < 0.01:
                    continue
                steps = max(1, int(length / 1.5))
                run_start = None
                last = None
                for i in range(steps + 1):
                    t = i / steps
                    x, y, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
                    seen = part['ghost'] or can_see(x, y, z)
                    if seen and run_start is None:
                        run_start = (x, y)
                    if not seen and run_start is not None:
                        segments.append((run_start, last))
                        run_start = None
                    last = (x, y)
                if run_start is not None:
                    segments.append((run_start, last))
            # A few isolated pixels are slivers of geometry, not lines anyone drew.
            paths = [path for path in join_segments(segments) if path_length(path) >= 5]
            output.append((part, paths))
        return output


def path_length(path):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


def join_segments(segments):
    """Chain segments end to end, so a curve is one path rather than hundreds."""
    def key(p):
        return (round(p[0], 1), round(p[1], 1))

    ends = {}
    for number, (a, b) in enumerate(segments):
        ends.setdefault(key(a), []).append((number, 0))
        ends.setdefault(key(b), []).append((number, 1))
    used = [False] * len(segments)
    paths = []
    for number, (a, b) in enumerate(segments):
        if used[number] or (abs(a[0] - b[0]) + abs(a[1] - b[1])) < 0.05:
            continue
        used[number] = True
        path = [a, b]
        for forward in (True, False):
            while True:
                tip = path[-1] if forward else path[0]
                found = None
                for other, side in ends.get(key(tip), ()):
                    if not used[other]:
                        found = (other, side)
                        break
                if not found:
                    break
                used[found[0]] = True
                next_point = segments[found[0]][1 - found[1]]
                if forward:
                    path.append(next_point)
                else:
                    path.insert(0, next_point)
        paths.append(path)
    return paths


def path_data(paths):
    parts = []
    for path in paths:
        parts.append('M' + ' '.join('%.1f %.1f' % p for p in simplify(path)))
    return ''.join(parts)


def simplify(path, tolerance=0.12):
    if len(path) < 3:
        return path
    kept = [path[0]]
    for i in range(1, len(path) - 1):
        ax, ay = kept[-1]
        bx, by = path[i]
        cx, cy = path[i + 1]
        length = math.hypot(cx - ax, cy - ay) or 1
        if abs((cx - ax) * (ay - by) - (ax - bx) * (cy - ay)) / length > tolerance:
            kept.append(path[i])
    kept.append(path[-1])
    return kept
