import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys


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

    __is_reduced = False

    def __init__(self, simplices):
        self.__is_reduced = False
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
        if not self.__is_reduced:
            pivots = {}

            for j in range(len(self.columns)):
                lower = self.columns[j].lower()
                while lower in pivots and lower != None:
                    self.columns[j] += self.columns[pivots[lower]]
                    lower = self.columns[j].lower()
                if lower != None:
                    pivots[lower] = j
            self.pivots = pivots


class BarCode:
    bc = []
    colors = ["blue", "green", "red", "cyan", "magenta", "yellow", "black"]

    def __init__(self, M: BoundaryMatrix):
        """Compute the Bar Code on a reduced matrix"""
        M.reduce()
        bc = []
        for j in range(len(M.columns)):
            lower = M.columns[j].lower()
            if lower == None and j not in M.pivots:
                dim = M.columns[j].dim
                val = M.columns[j].val
                bc.append((dim, val, "inf"))
            elif lower in M.pivots:
                dim = M.columns[j].dim - 1
                val_end = M.columns[j].val
                val_init = M.columns[lower].val
                bc.append((dim, val_init, val_end))
        self.bc = bc

    def __str__(self):
        s = ""
        for bar in self.bc:
            s += "{} {} {}\n".format(bar[0], bar[1], bar[2])
        return s

    def sort(self):
        order = lambda x: x[0]
        self.bc.sort(key=order)

    def remove(self, length):
        """Remove bar with a lenght less than the specified minimum length"""
        i = 0
        while i < len(self.bc):
            if self.bc[i][2] != "inf" and self.bc[i][2] - self.bc[i][1] <= length:
                self.bc.pop(i)
            else:
                i += 1

    def plot(self, logarithmic=False, title=""):
        min_x = self.bc[0][1] + 1e-3
        max_x = min_x * 1.1
        for bar in self.bc:
            min_x = min(min_x, bar[1])
            if bar[2] != "inf":
                max_x = max(max_x, bar[2])
            else:
                max_x = max(max_x, bar[1])
        max_x *= 1.1

        dims = set()
        plt.figure()
        for i in range(len(self.bc)):
            bar = self.bc[i]
            dim = bar[0]
            low = bar[1]
            high = bar[2]
            if high == "inf":
                high = max_x
            color = self.colors[dim % len(self.colors)]
            plt.plot([low, high], [i, i], color=color)
            dims.add(dim)
        plt.yticks([])
        plt.xlim(min_x, max_x)
        if logarithmic:
            plt.xscale("log")
        patches = []
        for d in dims:
            color = self.colors[d % len(self.colors)]
            patches.append(mpatches.Patch(color=color, label="H{}".format(d)))
            plt.legend(handles=patches)
        plt.title(title)
        plt.show()


def read(file_name):
    simplices = []
    with open(file_name, "r") as f:
        for line in f:
            l = line.rstrip().split(" ")
            val = float(l[0])
            dim = int(l[1])
            vertices = [int(i) for i in l[2:]]
            simplices.append(Simplex(dim, val, vertices))
    return simplices


def plot_bar_code(file="torus.txt", log=False):
    simplices = read(file)
    B = BoundaryMatrix(simplices)
    B.reduce()
    bc = BarCode(B)
    bc.sort()
    bc.plot(logarithmic=log, title=file.replace(".txt", ""))


def print_filtration(file="torus.txt"):
    simplices = read(file)
    B = BoundaryMatrix(simplices)
    bc = BarCode(B)
    print(bc)


if __name__ == "__main__":
    args = sys.argv
    log = False
    print_bc = False
    if len(args) >= 2:
        file = args[1]
    else:
        file = "torus.txt"
    if "--log" in args:
        log = True
    if "--print" in args:
        print_filtration(file)
    else :
        plot_bar_code(file, log)
