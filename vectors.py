import math

class Vector2d:
    num_of_vectors = 0

    def __init__(self, x: int | float = 0, y: int | float = 0):
        self.x = x
        self.y = y

        Vector2d.num_of_vectors += 1

    def __add__(self, b):
        return Vector2d(self.x + b.x, self.y + b.y)

    def __sub__(self, b):
        return Vector2d(self.x - b.x, self.y - b.y)

    def __mul__(self, b):
        return Vector2d(b * self.x, b * self.y)

    def __rmul__(self, b):
        return Vector2d(b * self.x, b * self.y)

    def __truediv__(self, b):
        if b != 0:
            return Vector2d(self.x / b, self.y / b)
        else:
            return Vector2d(self.x / 0.001, self.y / 0.001)

    def dot(self, b):
        return self.x * b.x + self.y * b.y

    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def unit(self):
        return self / self.mag()

    def coords(self):
        coord = (self.x, self.y)
        return coord


class Vector3d:
    num_of_vectors = 0

    def __init__(self, x: int | float = 0, y: int | float = 0, z: int | float = 0):
        self.x = x
        self.y = y
        self.z = z

        Vector3d.num_of_vectors += 1

    def __add__(self, b):
        return Vector3d(self.x + b.x, self.y + b.y, self.z + b.z)

    def __sub__(self, b):
        return Vector3d(self.x - b.x, self.y - b.y, self.z - b.z)

    def __mul__(self, b):
        return Vector3d(b * self.x, b * self.y, self.z * b.z)

    def __rmul__(self, b):
        return Vector3d(b * self.x, b * self.y, self.z * b.z)

    def __truediv__(self, b):
        if b != 0:
            return Vector3d(self.x / b, self.y / b, self.z / b.z)
        else:
            return Vector3d(self.x / 0.001, self.y / 0.001, self.z / 0.001)

    def dot(self, b):
        return self.x * b.x + self.y * b.y + self.z * b.z

    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def unit(self):
        return self / self.mag()

    def coords(self):
        coord = (self.x, self.y, self.z)
        return coord