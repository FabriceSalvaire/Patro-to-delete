####################################################################################################
#
# PyValentina - A Python implementation of Valentina Pattern Drafting Software
# Copyright (C) 2017 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

def bounding_box_from_points(points):

    bounding_box = points[0].bounding_box()
    for point in points[1:]:
        bounding_box |= points.bounding_box()
    return bounding_box

####################################################################################################

class Primitive:

    __dimension__ = None

    ##############################################

    def bounding_box(self):

        raise NotImplementedError

####################################################################################################

class Primitive2D:

    __dimension__ = 2
