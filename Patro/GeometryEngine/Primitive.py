####################################################################################################
#
# Patro - A Python library to make patterns for fashion design
# Copyright (C) 2017 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

"""Module to implement base classes for primitives.

"""

# Fixme:
#  length, interpolate path
#  area

####################################################################################################

__all__ = [
    'Primitive',
    'Primitive2DMixin',
    'Primitive1P',
    'Primitive2P',
    'Primitive3P',
    'Primitive4P',
]

####################################################################################################

from collections import abc as collections

import numpy as np

from .BoundingBox import bounding_box_from_points
# Fixme: circular import
# from .Transformation import Transformation2D

####################################################################################################

class Primitive:

    """Base class for geometric primitive"""

    __vector_cls__ = None

    ##############################################

    @property
    def dimension(self):
        """Dimension in [2, 3] for 2D / 3D primitive"""
        raise NotImplementedError

    ##############################################

    @property
    def is_infinite(self):
        """True if the primitive has infinite extend like a line"""
        return False

    ##############################################

    @property
    def is_closed(self):
        """True if the primitive is a closed path."""
        return False

    ##############################################

    @property
    def number_of_points(self):
        """Number of points which define the primitive."""
        raise NotImplementedError

    def __len__(self):
        return self.number_of_points

    ##############################################

    @property
    def is_reversible(self):
        """True if the order of the points is reversible"""
        # Fixme: True if number_of_points > 1 ???
        return False

    ##############################################

    # Fixme: part of the API imply points
    #  it is not true for Path2D

    @property
    def points(self):
        raise NotImplementedError

    ##############################################

    # @points.setter
    # def points(self):
    #     raise NotImplementedError

    def _set_points(self, points):
        raise NotImplementedError

    ##############################################

    def __repr__(self):
        return self.__class__.__name__ + str([str(p) for p in self.points])

    ##############################################

    def clone(self):
        return self.__class__(*self.points)

    ##############################################

    @property
    def bounding_box(self):
        """Bounding box of the primitive.

        Return None if primitive is infinite.
        """
        # Fixme: cache
        if self.is_infinite:
            return None
        else:
            return bounding_box_from_points(self.points)

    ##############################################

    def reverse(self):
        return self

    ##############################################

    def transform(self, transformation, clone=False):
        """Apply a transformation to the primitive.

        If *clone* is set then the primitive is cloned.

        """
        obj = self.clone() if clone else self
        if not transformation.is_identity:
            obj.apply_transformation(transformation)
        return obj

    ##############################################

    def apply_transformation(self, transformation):
        """Apply a transformation to the primitive.

        If *clone* is set then the primitive is cloned.

        """
        # for point in self.points:
        #     point *= transformation # don't work
        self._set_points([transformation*p for p in self.points])

    ##############################################

    def mirror(self, clone=False):
        from .Transformation import Transformation2D
        return self.transform(Transformation2D.Parity(), clone)

    def x_mirror(self, clone=False):
        from .Transformation import Transformation2D
        return self.transform(Transformation2D.XReflection(), clone)

    def y_mirror(self, clone=False):
        from .Transformation import Transformation2D
        return self.transform(Transformation2D.YReflection(), clone)

    def rotate(self, angle, clone=False):
        from .Transformation import Transformation2D
        return self.transform(Transformation2D.Rotation(angle), clone)

    def scale(self, x_factor, y_factor=None, clone=False):
        from .Transformation import Transformation2D
        return self.transform(Transformation2D.Scale(x_factor, y_factor), clone)

    ##############################################

    @property
    def point_array(self):
        r"""Return the geometry matrix as a Numpy array.

        .. math::
           \mathrm{Geometry\ Matrix} =
           \begin{bmatrix}
           x_0  & x_1 & \ldots & x_{n-1} \\
           y_0  & y_1 & \ldots & y_{n-1}
           \end{bmatrix}

        """
        # Fixme: geometry_matrix vs point_array
        # Fixme: cache ??? but point set and init
        # if self._point_array is None:
        #     self._point_array = np.array(list(self.points)).transpose()
        # return self._point_array
        return np.array(list(self.points)).transpose()

    ##############################################

    def is_point_close(self, other):
        # Fixme: verus is_closed
        #  is_similar
        return np.allclose(self.point_array, other.point_array)

####################################################################################################

class Primitive2DMixin:

    __vector_cls__ = None # Fixme: due to import, done in module's __init__.py

    # __dimension__ = 2
    @property
    def dimension(self):
        return 2

####################################################################################################

class ClosedPrimitiveMixin:

    # Fixme: should be reversible

    ##############################################

    @property
    def is_closed(self):
        """True if the primitive is a closed path."""
        return True

    ##############################################

    @property
    def closed_points(self):
        points = list(self.points)
        points.append(self.start_point)
        return points

    ##############################################

    @property
    def closed_point_array(self):
        r"""Return the geometry matrix as a Numpy array for a closed primitive.

        .. math::
           \mathrm{Geometry\ Matrix} =
           \begin{bmatrix}
           x_0  & x_1 & \ldots & x_{n-1} & x_0 \\
           y_0  & y_1 & \ldots & y_{n-1} & y_0
           \end{bmatrix}

        """
        # Fixme: place, func for closed_point
        # Fixme: cache ???
        return np.array(self.closed_points).transpose()

####################################################################################################

class ReversiblePrimitiveMixin:

    ##############################################

    @property
    def is_reversible(self):
        True

    ##############################################

    @property
    def reversed_points(self):
        raise NotImplementedError
        # return reversed(list(self.points))

    ##############################################

    def reverse(self):
        return self.__class__(*self.reversed_points)

    ##############################################

    @property
    def start_point(self):
        raise NotImplementedError

    @property
    def end_point(self):
        raise NotImplementedError

####################################################################################################

class Primitive1P(Primitive):

    ##############################################

    def __init__(self, p0):
        self.p0 = p0

    ##############################################

    @property
    def number_of_points(self):
        return 1

    @property
    def p0(self):
        return self._p0

    @p0.setter
    def p0(self, value):
        self._p0 = self.__vector_cls__(value)

    ##############################################

    @property
    def points(self):
        return iter(self._p0) # Fixme: efficiency ???

    @property
    def reversed_points(self):
        return self.points

    ##############################################

    def _set_points(self, points):
        self._p0 = points

####################################################################################################

class Primitive2P(Primitive1P, ReversiblePrimitiveMixin):

    ##############################################

    def __init__(self, p0, p1):
        # We don't call super().__init__(p0) for speed
        self.p0 = p0
        self.p1 = p1

    ##############################################

    # Redundant code ... until we don't use self._points = []

    @property
    def number_of_points(self):
        return 2

    @property
    def p1(self):
        return self._p1

    @p1.setter
    def p1(self, value):
        self._p1 = self.__vector_cls__(value)

    ##############################################

    @property
    def start_point(self):
        return self._p0

    @property
    def end_point(self):
        return self._p1

    ##############################################

    @property
    def points(self):
        return iter((self._p0, self._p1))

    @property
    def reversed_points(self):
        return iter((self._p1, self._p0))

    ##############################################

    def _set_points(self, points):
        self._p0, self._p1 = points

    ##############################################

    def interpolate(self, t):
        """Return the linear interpolate of two points."""
        return self._p0 * (1 - t) + self._p1 * t

####################################################################################################

class Primitive3P(Primitive2P):

    ##############################################

    def __init__(self, p0, p1, p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

    ##############################################

    @property
    def number_of_points(self):
        return 3

    @property
    def p2(self):
        return self._p2

    @p2.setter
    def p2(self, value):
        self._p2 = self.__vector_cls__(value)

    ##############################################

    @property
    def end_point(self):
        return self._p2

    ##############################################

    @property
    def points(self):
        return iter((self._p0, self._p1, self._p2))

    @property
    def reversed_points(self):
        # Fixme: share code ???
        return iter((self._p2, self._p1, self._p0))

    def iter_from_second_point(self):
        # Fixme: share code ???
        return iter(self._p1, self._p2)

    ##############################################

    def _set_points(self, points):
        self._p0, self._p1, self._p2 = points

####################################################################################################

class Primitive4P(Primitive3P):

    ##############################################

    def __init__(self, p0, p1, p2, p3):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    ##############################################

    @property
    def number_of_points(self):
        return 4

    @property
    def p3(self):
        return self._p3

    @p3.setter
    def p3(self, value):
        self._p3 = self.__vector_cls__(value)

    ##############################################

    @property
    def end_point(self):
        return self._p3

    ##############################################

    @property
    def points(self):
        return iter((self._p0, self._p1, self._p2, self._p3))

    @property
    def reversed_points(self):
        return iter((self._p3, self._p2, self._p1, self._p0))

    def iter_from_second_point(self):
        return iter(self._p1, self._p2, self._p3)

    ##############################################

    def _set_points(self, points):
        self._p0, self._p1, self._p2, self._p3 = points

####################################################################################################

class PrimitiveNP(Primitive, ReversiblePrimitiveMixin):

    ##############################################

    @staticmethod
    def handle_points(points):
        if len(points) == 1 and isinstance(points[0], collections.Iterable):
            points = points[0]
        return points

    ##############################################

    def __init__(self, *points):

        points = self.handle_points(points)
        self._points = [self.__vector_cls__(p) for p in points]
        self._point_array = None

    ##############################################

    @property
    def number_of_points(self):
        return len(self._points)

    ##############################################

    @property
    def start_point(self):
        return self._points[0]

    @property
    def end_point(self):
        return self._points[-1]

    ##############################################

    @property
    def points(self):
        return iter(self._points)

    @property
    def reversed_points(self):
        return reversed(self._points)

    def iter_from_second_point(self):
        return iter(self._points[1:])

    ##############################################

    def _set_points(self, points):
        self._points = points
        self._point_array = None

    ##############################################

    def __getitem__(self, _slice):
        return self._points[_slice]

    ##############################################

    def iter_on_nuplets(self, size):

        if size > self.number_of_points:
            raise ValueError('size {} > number of points {}'.format(size, self.number_of_points))

        for i in range(self.number_of_points - size +1):
            yield self._points[i:i+size]

####################################################################################################

class PolygonMixin:

    ##############################################

    def to_polygon(self):
        from .Polygon import Polygon2D
        return Polygon2D(self.points)

####################################################################################################

class PathMixin:

    ##############################################

    def to_path(self):

        from .Path import Path2D

        path = Path2D(self.start_point)
        for point in self.iter_from_second_point():
            path.line_to(point, absolute=True)
        if self.is_closed:
            path.close()

        return path


