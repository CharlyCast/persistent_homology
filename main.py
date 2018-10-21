class Simplex:
    dim = 0
    val = 0
    vertices = ()

    def __init__(self, dim, val, vertices):
        self.dim = dim
        self.val = val
        self.vertices = vertices
        self.vertices.sort()
        self.vertices = tuple(vertices)

    def __str__(self):
        return "val: {}; dim {}; vertices: {}".format(self.val, self.dim, self.vertices)

    def boundaries(self):
        b = []
        for i in range(len(self.vertices)):
            t = tuple(self.vertices[0:i] + self.vertices[i + 1 :])
            if t != ():
                b.append(t)
        return b


class Column:
    vertices = []
    sid = {}
    val = 0
    dim = 0

    def __init__(self, s: Simplex, sid):
        boundaries = s.boundaries()
        self.vertices = []
        for b in boundaries:
            self.vertices.append(sid[b])
        self.vertices.sort()
        self.val = s.val
        self.dim = s.dim

    def __add__(self, other):
        result = []
        i, j = 0, 0
        v1, v2 = self.vertices, other.vertices
        while i < len(v1) or j < len(v2):
            if i >= len(v1):
                result.append(v2[j])
                j += 1
            elif j >= len(v2):
                result.append(v1[i])
                i += 1
            else:
                val1 = v1[i]
                val2 = v2[j]
                if val1 < val2:
                    result.append(val1)
                    i += 1
                elif val2 < val1:
                    result.append(val2)
                    j += 1
                else:
                    i += 1
                    j += 1
        return result

    def __iadd__(self, other):
        self.vertices = self.__add__(other)
        return self

    def __str__(self):
        return str(self.vertices)

    def lower(self):
        if len(self.vertices) == 0:
            return None
        else:
            return self.vertices[-1]


class BoundaryMatrix:
    columns = []
    simplices = []
    sid = {}  # simplices id
    pivots = {}

    def __init__(self, simplices):
        self.simplices = simplices

        order = lambda s: (s.val, s.dim)
        simplices.sort(key=order)

        for i in range(len(simplices)):
            self.sid[simplices[i].vertices] = i

        for s in simplices:
            self.columns.append(Column(s, self.sid))

    def __str__(self):
        s = ""
        for c in self.columns:
            s += str(c) + "\n"
        return s

    def reduce(self):
        pivots = {}
        for j in range(len(self.columns)):
            lower = self.columns[j].lower()
            while lower in pivots and lower != None:
                self.columns[j] += self.columns[pivots[lower]]
                lower = self.columns[j].lower()
            if lower != None:
                pivots[lower] = j
        self.pivots = pivots

    def get_barcode(self):
        bc = []
        for j in range(len(self.columns)):
            lower = self.columns[j].lower()
            if lower == None and j not in self.pivots:
                dim = self.columns[j].dim
                val = self.columns[j].val
                bc.append((dim, val, "inf"))
            elif lower in self.pivots:
                dim = self.columns[j].dim - 1
                val_end = self.columns[j].val
                val_init = self.columns[lower].val
                bc.append((dim, val_init, val_end))
        return bc


def read():
    simplices = []
    with open("example.txt", "r") as f:
        for line in f:
            l = line.rstrip().split(" ")
            val = float(l[0])
            dim = int(l[1])
            vertices = [int(i) for i in l[2:]]
            simplices.append(Simplex(dim, val, vertices))

    return simplices


def boundary_matrix():
    simplices = read()

    B = BoundaryMatrix(simplices)
    print(B)
    B.reduce()
    print(B)
    print(B.sid)
    print(B.get_barcode())


if __name__ == "__main__":
    boundary_matrix()
