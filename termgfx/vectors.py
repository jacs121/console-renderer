import math

class Vector2:
    def __init__(self, x: float | int = 0.0, y: float | int = 0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float | int) -> 'Vector2':
        if isinstance(scalar, type(self)):
            return Vector2(self.x * scalar.x, self.y * scalar.y)
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector2':
        if isinstance(scalar, type(self)):
            return Vector2(self.x / scalar.x, self.y / scalar.y)
        else:
            return Vector2(self.x / scalar, self.y / scalar)
    
    def __div__(self, scalar: float) -> 'Vector2':
        if isinstance(scalar, type(self)):
            return Vector2(self.x / scalar.x, self.y / scalar.y)
        else:
            return Vector2(self.x / scalar, self.y / scalar)
    
    def __floordiv__(self, scalar: float) -> 'Vector2':
        if isinstance(scalar, type(self)):
            return Vector2(int(self.x // scalar.x), int(self.y // scalar.y))
        return Vector2(int(self.x // scalar), int(self.y // scalar))
    
    def __eq__(self, other: 'Vector2') -> bool:
        return self.x == other.x and self.y == other.y
    
    def __ne__(self, other: 'Vector2') -> bool:
        return not self.__eq__(other)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
    
    def magnitude(self) -> float:
        """Calculate the length of the vector"""
        return math.sqrt(self.x**2 + self.y**2)
    
    def magnitude_squared(self) -> float:
        """Calculate squared length (faster for comparisons)"""
        return self.x**2 + self.y**2
    
    def normalized(self) -> 'Vector2':
        """Return a normalized copy of the vector"""
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2()
    
    def normalize(self) -> None:
        """Normalize the vector in-place"""
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
    
    def dot(self, other: 'Vector2') -> float:
        """Calculate dot product with another vector"""
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vector2') -> float:
        """Calculate 2D cross product (returns scalar)"""
        return self.x * other.y - self.y * other.x
    
    def distance_to(self, other: 'Vector2') -> float:
        """Calculate distance to another vector"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def distance_squared_to(self, other: 'Vector2') -> float:
        """Calculate squared distance (faster for comparisons)"""
        return (self.x - other.x)**2 + (self.y - other.y)**2
    
    def angle(self) -> float:
        """Calculate angle in radians from positive x-axis"""
        return math.atan2(self.y, self.x)
    
    def rotate(self, angle: float) -> 'Vector2':
        """Rotate vector by angle (radians)"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def lerp(self, other: 'Vector2', t: float) -> 'Vector2':
        """Linear interpolation between two vectors"""
        t = max(0.0, min(1.0, t))
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def perpendicular(self) -> 'Vector2':
        """Return perpendicular vector (rotated 90 degrees counter-clockwise)"""
        return Vector2(-self.y, self.x)
    
    def to_tuple(self) -> tuple[float, float]:
        """Convert to tuple representation"""
        return (self.x, self.y)
    
    @classmethod
    def from_angle(cls, angle: float, magnitude: float = 1.0) -> 'Vector2':
        """Create vector from angle (radians) and magnitude"""
        return Vector2(
            math.cos(angle) * magnitude,
            math.sin(angle) * magnitude
        )
    
    @classmethod
    def zero(cls) -> 'Vector2':
        """Return zero vector"""
        return Vector2(0, 0)
    
    @classmethod
    def one(cls) -> 'Vector2':
        """Return vector (1, 1)"""
        return Vector2(1, 1)
    
    @classmethod
    def up(cls) -> 'Vector2':
        """Return vector (0, 1)"""
        return Vector2(0, 1)
    
    @classmethod
    def down(cls) -> 'Vector2':
        """Return vector (0, -1)"""
        return Vector2(0, -1)
    
    @classmethod
    def left(cls) -> 'Vector2':
        """Return vector (-1, 0)"""
        return Vector2(-1, 0)
    
    @classmethod
    def right(cls) -> 'Vector2':
        """Return vector (1, 0)"""
        return Vector2(1, 0)