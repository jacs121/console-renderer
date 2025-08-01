import math
import colorsys
from vectors import Vector2
from typing import Tuple, List, Union, Optional

class Color:
    def __init__(self, 
                 r: float = 0.0, 
                 g: float = 0.0, 
                 b: float = 0.0, 
                 a: float = 1.0, 
                 h: Optional[float] = None, 
                 s: Optional[float] = None, 
                 l: Optional[float] = None):
        """
        Represents a color in RGB, RGBA, or HSLA format.
        Defaults to RGBA if RGB values are provided, otherwise uses HSLA.
        """
        if h is not None and s is not None and l is not None:
            self._h = max(0.0, min(1.0, h))
            self._s = max(0.0, min(1.0, s))
            self._l = max(0.0, min(1.0, l))
            self._a = max(0.0, min(1.0, a))
            self._convert_hsla_to_rgba()
        else:
            self._r = max(0.0, min(1.0, r))
            self._g = max(0.0, min(1.0, g))
            self._b = max(0.0, min(1.0, b))
            self._a = max(0.0, min(1.0, a))

    def _convert_rgba_to_hsla(self):
        """Convert internal RGBA representation to HSLA"""
        r, g, b = self._r, self._g, self._b
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        self._h = h
        self._s = s
        self._l = l

    def _convert_hsla_to_rgba(self):
        """Convert internal HSLA representation to RGBA"""
        r, g, b = colorsys.hls_to_rgb(self._h, self._l, self._s)
        self._r = r
        self._g = g
        self._b = b

    @property
    def rgba(self) -> Tuple[float, float, float, float]:
        """Get RGBA values (0.0-1.0 range)"""
        return (self._r, self._g, self._b, self._a)
    
    @property
    def rgb(self) -> Tuple[float, float, float]:
        """Get RGB values (0.0-1.0 range)"""
        return (self._r, self._g, self._b)
    
    @property
    def hsla(self) -> Tuple[float, float, float, float]:
        """Get HSLA values (0.0-1.0 range)"""
        self._convert_rgba_to_hsla()
        return (self._h, self._s, self._l, self._a)
    
    @property
    def rgba255(self) -> Tuple[int, int, int, int]:
        """Get RGBA values in 0-255 range"""
        return (
            int(self._r * 255),
            int(self._g * 255),
            int(self._b * 255),
            int(self._a * 255)
        )
    
    @property
    def rgb255(self) -> Tuple[int, int, int]:
        """Get RGB values in 0-255 range"""
        return (
            int(self._r * 255),
            int(self._g * 255),
            int(self._b * 255)
        )
    
    def as_tuple(self, include_alpha: bool = False) -> Union[Tuple[int, int, int], Tuple[int, int, int, int]]:
        """Get color as tuple suitable for renderer"""
        if include_alpha:
            return self.rgba255
        return self.rgb255
    
    def blend(self, other: 'Color', alpha: float) -> 'Color':
        """Blend with another color using specified alpha"""
        alpha = min(max(alpha, 0.0), 1.0)
        inv_alpha = 1.0 - alpha
        return Color(
            r=self._r * inv_alpha + other._r * alpha,
            g=self._g * inv_alpha + other._g * alpha,
            b=self._b * inv_alpha + other._b * alpha,
            a=self._a * inv_alpha + other._a * alpha
        )
    
    def __eq__(self, other: 'Color') -> bool:
        return (self._r == other._r and 
                self._g == other._g and 
                self._b == other._b and 
                self._a == other._a)

class Texture:
    def __init__(self, source: Union[Color, List[List[Color]]], width: Optional[int] = None, height: Optional[int] = None):
        """
        Represents a texture that can be either:
        - A solid color
        - An image (2D grid of Color objects)
        """
        if isinstance(source, Color):
            self.is_solid = True
            self.color = source
            self.image = None
        else:
            self.is_solid = False
            self.image = source
            self.width = width if width else len(source[0])
            self.height = height if height else len(source)
    
    def sample(self, u: float = 0.0, v: float = 0.0) -> Color:
        """Get color at normalized coordinates (u, v) or pixel position"""
        if self.is_solid:
            return self.color
        
        # Convert normalized coordinates to pixel coordinates
        x = int(u * (self.width - 1))
        y = int(v * (self.height - 1))
        
        # Clamp coordinates to valid range
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        return self.image[y][x]
    
    def get_pixel(self, x: int, y: int) -> Color:
        """Get color at specific pixel coordinates"""
        if self.is_solid:
            return self.color
        return self.image[y][x]

class Rect:
    def __init__(self, 
                 position: Vector2, 
                 size: Vector2, 
                 rotation: float = 0.0):
        """
        Represents a rectangle with position, size, and rotation
        """
        self.__position__ = position
        self.__size__ = size
        self.__rotation__ = rotation  # Rotation in radians
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get the position of rectangle"""
        return (self.__position__.x, self.__position__.y)
    
    @property
    def size(self) -> Tuple[float, float]:
        """Get dimensions of rectangle"""
        return (self.__size__.x, self.__size__.y)

    @property
    def corners(self) -> List[Vector2]:
        """Get corner points of rectangle with rotation applied"""
        half_w = self.__size__.x / 2
        half_h = self.__size__.y / 2
        
        # Define corners relative to center
        corners = [
            Vector2(-half_w, -half_h),  # Top-left
            Vector2(half_w, -half_h),   # Top-right
            Vector2(half_w, half_h),    # Bottom-right
            Vector2(-half_w, half_h)    # Bottom-left
        ]
        
        # Apply rotation
        cos_angle = math.cos(self.__rotation__)
        sin_angle = math.sin(self.__rotation__)
        
        rotated_corners = []
        for corner in corners:
            # Rotate point around center
            rx = corner.x * cos_angle - corner.y * sin_angle
            ry = corner.x * sin_angle + corner.y * cos_angle
            # Translate to world position
            rotated_corners.append(self.position + Vector2(rx, ry))
        
        return rotated_corners

    def contains_point(self, point: Vector2) -> bool:
        """Check if a point is inside the rectangle"""
        # Transform point to local coordinates
        cos_angle = math.cos(-self.__rotation__)
        sin_angle = math.sin(-self.__rotation__)
        
        # Translate point to rectangle-local coordinates
        translated = point - self.position
        
        # Rotate point to align with rectangle axes
        rx = translated.x * cos_angle - translated.y * sin_angle
        ry = translated.x * sin_angle + translated.y * cos_angle
        
        # Check if within local bounds
        half_w = self.size.x / 2
        half_h = self.size.y / 2
        return (-half_w <= rx <= half_w) and (-half_h <= ry <= half_h)

class Collision:
    def __init__(self, rect1: Rect, rect2: Rect):
        """Represents a collision between two rectangles"""
        self.rect1 = rect1
        self.rect2 = rect2
        self._normal = (0.0, 0.0)
        self._depth = 0.0
        self._calculate_collision()
    
    def _calculate_collision(self):
        """Calculate collision details using Separating Axis Theorem"""
        # Get all corners
        corners1 = self.rect1.corners
        corners2 = self.rect2.corners
        
        # Check for separating axis
        min_overlap = float('inf')
        smallest_axis = None
        
        # Check edges of first rectangle
        for i in range(4):
            j = (i + 1) % 4
            edge = (corners1[j][0] - corners1[i][0], 
                    corners1[j][1] - corners1[i][1])
            axis = (-edge[1], edge[0])  # Perpendicular axis
            axis = self._normalize(axis)

            # Project both shapes onto axis
            min1, max1 = self._project(corners1, axis)
            min2, max2 = self._project(corners2, axis)
            
            # Check for overlap
            overlap = min(max1, max2) - max(min1, min2)
            if overlap <= 0:
                self._normal = (0.0, 0.0)
                self._depth = 0.0
                return
            elif overlap < min_overlap:
                min_overlap = overlap
                smallest_axis = axis
        
        # Check edges of second rectangle
        for i in range(4):
            j = (i + 1) % 4
            edge = (corners2[j][0] - corners2[i][0], 
                    corners2[j][1] - corners2[i][1])
            axis = (-edge[1], edge[0])  # Perpendicular axis
            axis = self._normalize(axis)
            
            # Project both shapes onto axis
            min1, max1 = self._project(corners1, axis)
            min2, max2 = self._project(corners2, axis)
            
            # Check for overlap
            overlap = min(max1, max2) - max(min1, min2)
            if overlap <= 0:
                self._normal = (0.0, 0.0)
                self._depth = 0.0
                return
            elif overlap < min_overlap:
                min_overlap = overlap
                smallest_axis = axis
        
        # Determine collision normal direction
        center1 = self.rect1.position
        center2 = self.rect2.position
        direction = (center2[0] - center1[0], center2[1] - center1[1])
        
        # Flip normal if pointing away from direction
        if self._dot(direction, smallest_axis) < 0:
            smallest_axis = (-smallest_axis[0], -smallest_axis[1])
        
        self._normal = smallest_axis
        self._depth = min_overlap
    
    def _normalize(self, vector: Tuple[float, float]) -> Tuple[float, float]:
        """Normalize a vector to unit length"""
        length = math.sqrt(vector[0]**2 + vector[1]**2)
        if length == 0:
            return (0, 0)
        return (vector[0]/length, vector[1]/length)
    
    def _dot(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Calculate dot product of two vectors"""
        return a[0]*b[0] + a[1]*b[1]
    
    def _project(self, 
                points: List[Tuple[float, float]], 
                axis: Tuple[float, float]) -> Tuple[float, float]:
        """Project points onto an axis and return min/max values"""
        min_val = float('inf')
        max_val = float('-inf')
        for (x, y) in points:
            projection = self._dot((x, y), axis)
            min_val = min(min_val, projection)
            max_val = max(max_val, projection)
        return (min_val, max_val)
    
    @property
    def colliding(self) -> bool:
        """Check if rectangles are colliding"""
        return self._depth > 0
    
    @property
    def normal(self) -> Tuple[float, float]:
        """Get collision normal vector (points from rect1 to rect2)"""
        return self._normal
    
    @property
    def depth(self) -> float:
        """Get penetration depth of collision"""
        return self._depth