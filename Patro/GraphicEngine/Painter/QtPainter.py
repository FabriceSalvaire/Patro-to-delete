####################################################################################################
#
# Patro - A Python library to make patterns for fashion design
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

import logging

import numpy as np

from IntervalArithmetic import Interval2D

from QtShim.QtCore import (
    Property, Signal, Slot, QObject,
    QRectF, QSizeF, QPointF, Qt,
)
from QtShim.QtGui import QColor, QFont, QFontMetrics, QImage, QPainter, QPainterPath, QBrush, QPen
# from QtShim.QtQml import qmlRegisterType
from QtShim.QtQuick import QQuickPaintedItem

from .Painter import Painter
from Patro.GeometryEngine.Vector import Vector2D
from Patro.GraphicEngine.GraphicScene.Scene import GraphicScene
from Patro.GraphicStyle import StrokeStyle

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class QtScene(QObject, GraphicScene):

    _logger = _module_logger.getChild('QtScene')

    ##############################################

    def __init__(self):

        QObject.__init__(self)
        GraphicScene.__init__(self)

####################################################################################################

class QtPainter(Painter):

    __STROKE_STYLE__ = {
        None: None, # Fixme: ???
        StrokeStyle.NoPen: Qt.NoPen,
        StrokeStyle.SolidLine: Qt.SolidLine,
        StrokeStyle.DashLine: Qt.DashLine,
        StrokeStyle.DotLine: Qt.DotLine,
        StrokeStyle.DashDotLine: Qt.DashDotLine,
        StrokeStyle.DashDotDotLine: Qt.DashDotDotLine,
    }

    _logger = _module_logger.getChild('QtPainter')

    ##############################################

    def __init__(self, scene=None):

        super().__init__(scene)

        self._show_grid = True

        # self._paper = paper

        # self._translation = QPointF(0, 0)
        # self._scale = 1

    ##############################################

    # @property
    # def translation(self):
    #     return self._translation

    # @translation.setter
    # def translation(self, value):
    #     self._translation = value

    # @property
    # def scale(self):
    #     return self._scale

    # @scale.setter
    # def scale(self, value):
    #     print('set scale', value)
    #     self._scale = value

    ##############################################

    def paint(self, painter):

        self._logger.info('paint')

        self._painter = painter
        if self._show_grid:
            self._paint_grid()
        super().paint()

    ##############################################

    def length_scene_to_viewport(self, length):
        raise NotImplementedError

    @property
    def scene_area(self):
        raise NotImplementedError

    def scene_to_viewport(self, position):
        # Note: painter.scale apply to text as well
        raise NotImplementedError

        # point = QPointF(position.x, position.y)
        # point += self._translation
        # point *= self._scale
        # point = QPointF(point.x(), -point.y())
        # return point

    ##############################################

    def cast_position(self, position):
        """Cast coordinate, apply scope transformation and convert scene to viewport, *position* can be a
        coordinate name string of a:class:`Vector2D`.

        """
        position = super().cast_position(position)
        return self.scene_to_viewport(position)

    ##############################################

    def _set_pen(self, item):

        path_syle = item.path_style
        print('_set_pen', item, path_syle)
        if item.selected:
            color = QColor('red') # Fixme: style
        else:
            color = path_syle.stroke_color
            if color is not None:
                color = QColor(str(color))
            else:
                color = None
        line_style = self.__STROKE_STYLE__[path_syle.stroke_style]
        line_width = path_syle.line_width_as_float

        # Fixme: selection style
        if item.selected:
            line_width *= 4

        print(item, color, line_style)
        if color is None or line_style is StrokeStyle.NoPen:
            # invisible item
            pen = QPen(Qt.NoPen)
            # print('Warning Pen:', item, item.user_data, color, line_style)
        else:
            pen = QPen(
                QBrush(color),
                line_width,
                line_style,
            )
            self._painter.setPen(pen)
            return pen

        fill_color = path_syle.fill_color
        if fill_color is not None:
            color = QColor(str(fill_color))
            self._painter.setBrush(color)
        else:
            self._painter.setBrush(Qt.NoBrush)

        return None

    ##############################################

    def _paint_grid(self):

        area = self.scene_area
        xinf, xsup = area.x.inf, area.x.sup
        yinf, ysup = area.y.inf, area.y.sup

        color = QColor('black')
        brush = QBrush(color)
        pen = QPen(brush, .75)
        self._painter.setPen(pen)
        self._painter.setBrush(Qt.NoBrush)

        step = 10
        self._paint_axis_grid(xinf, xsup, yinf, ysup, True, step)
        self._paint_axis_grid(yinf, ysup, xinf, xsup, False, step)

        color = QColor('black')
        brush = QBrush(color)
        pen = QPen(brush, .25)
        self._painter.setPen(pen)
        self._painter.setBrush(Qt.NoBrush)

        step = 1
        self._paint_axis_grid(xinf, xsup, yinf, ysup, True, step)
        self._paint_axis_grid(yinf, ysup, xinf, xsup, False, step)

    ##############################################

    def _paint_axis_grid(self, xinf, xsup, yinf, ysup, is_x, step):

        for i in range(int(xinf // step), int(xsup // step) +1):
            x = i*step
            if xinf <= x <= xsup:
                if is_x:
                    p0 = Vector2D(x, yinf)
                    p1 = Vector2D(x, ysup)
                else:
                    p0 = Vector2D(yinf, x)
                    p1 = Vector2D(ysup, x)
                p0 = self.cast_position(p0)
                p1 = self.cast_position(p1)
                self._painter.drawLine(p0, p1)

    ##############################################

    def paint_CoordinateItem(self, item):
        self._coordinates[item.name] = self.scene_to_viewport(item.position)

    ##############################################

    def paint_CircleItem(self, item):

        center = self.cast_position(item.position)
        radius = self.length_scene_to_viewport(item.radius)

        pen = self._set_pen(item)

        # self._painter.drawEllipse(center, radius, radius)
        rectangle = QRectF(
            center + QPointF(-radius, radius),
            center + QPointF(radius, -radius),
        )
        self._painter.drawArc(rectangle, 0, 360*16)
        ## self._painter.drawArc(center.x, center.y, radius, radius, 0, 360)

    ##############################################

    def paint_CubicBezierItem(self, item):

        vertices = self.cast_item_positions(item)

        pen = self._set_pen(item)
        path = QPainterPath()
        path.moveTo(vertices[0])
        path.cubicTo(*vertices[1:])
        self._painter.drawPath(path)

        path_style = item.path_style
        # if path_style.show_control:
        if getattr(path_style, 'show_control', False):
            color = QColor(str(path_style.control_color))
            brush = QBrush(color)
            pen = QPen(brush, 1) # Fixme
            self._painter.setPen(pen)
            self._painter.setBrush(Qt.NoBrush)
            path = QPainterPath()
            path.moveTo(vertices[0])
            for vertex in vertices[1:]:
                path.lineTo(vertex)
            self._painter.drawPath(path)

            # Fixme:
            radius = 3
            self._painter.setBrush(brush)
            for vertex in vertices:
                self._painter.drawEllipse(vertex, radius, radius)
            self._painter.setBrush(Qt.NoBrush) # Fixme:

    ##############################################

    def paint_ImageItem(self, item):

        vertices = self.cast_item_positions(item)
        rec = QRectF(vertices[0], vertices[1])

        image = item.image
        height, width, bytes_per_line = image.shape
        bytes_per_line *= width
        qimage = QImage(image, width, height, bytes_per_line, QImage.Format_RGB888)

        self._painter.drawImage(rec, qimage)

    ##############################################

    def paint_SegmentItem(self, item):

        self._set_pen(item)
        vertices = self.cast_item_positions(item)
        self._painter.drawLine(*vertices)

    ##############################################

    def paint_PolylineItem(self, item):

        self._set_pen(item)
        vertices = self.cast_item_positions(item)
        path = QPainterPath()
        path.moveTo(vertices[0])
        for vertex in vertices[1:]:
            path.lineTo(vertex)
        self._painter.drawPath(path)

    ##############################################

    def paint_TextItem(self, item):

        position = self.cast_position(item.position)

        font = item.font
        qfont = QFont(font.family, font.point_size) # weight, italic = False

        # Fixme: anchor position
        # font_metrics = QFontMetrics(qfont)
        # height = font_metrics.height()
        # width = font_metrics.width(item.text)

        self._painter.setFont(qfont)
        self._painter.drawText(position, item.text)

####################################################################################################

class ViewportArea:

    ##############################################

    def __init__(self):

        self._scene = None

        # self._width = None
        # self._height = None
        self._viewport_size = None

        self._scale = 1
        self._center = None
        self._area = None

    ##############################################

    def __bool__(self):

        return self._scene is not None

    ##############################################

    @property
    def viewport_size(self):
        return self._viewport_size
        # return (self._width, self._height)

    @viewport_size.setter
    def viewport_size(self, geometry):
        # self._width = geometry.width()
        # self._height = geometry.height()
        self._viewport_size = np.array((geometry.width(), geometry.height()), dtype=np.float)
        if self:
            self._update_viewport_area()

    ##############################################

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, value):
        self._scene = value

    @property
    def scene_area(self):
        if self:
            return self._scene.bounding_box
        else:
            return None

    ##############################################

    # @property
    # def scale(self):
    #     return self._scale # px / mm

    @property
    def scale_px_by_mm(self):
        return self._scale

    @property
    def scale_mm_by_px(self):
        return 1 / self._scale

    @property
    def center(self):
        return self._center

    # @property
    # def center_as_point(self):
    #     return QPointF(self._center[0], self._center[1])

    @property
    def area(self):
        return self._area

    ##############################################

    def _update_viewport_area(self):

        offset = self._viewport_size / 2 * self.scale_mm_by_px
        x, y = list(self._center)
        dx, dy = list(offset)

        self._area = Interval2D(
            (x - dx, x + dx),
            (y - dy, y + dy),
        )
        # Fixme: QPointF ???
        self._translation = - QPointF(self._area.x.inf, self._area.y.sup)

        print('_update_viewport_area', self._center, self.scale_mm_by_px, self._area)

    ##############################################

    def _compute_scale_to_fit_scene(self, margin=None):

        # width_scale = self._width / scene_area.x.length
        # height_scale = self._height / scene_area.y.length
        # scale = min(width_scale, height_scale)

        # scale [px/mm]
        axis_scale = self._viewport_size / np.array(self.scene_area.size, dtype=np.float)
        axis = axis_scale.argmin()
        scale = axis_scale[axis]

        return scale, axis

    ##############################################

    def zoom_at(self, center, scale):

        self._center = center
        self._scale = scale
        self._update_viewport_area()

    ##############################################

    def fit_scene(self):

        if self:
            center = np.array(self.scene_area.center, dtype=np.float)
            scale, axis = self._compute_scale_to_fit_scene()
            self.zoom_at(center, scale)

    ##############################################

    def scene_to_viewport(self, position):

        point = QPointF(position.x, position.y)
        point += self._translation
        point *= self._scale
        point = QPointF(point.x(), -point.y())
        return point

    ##############################################

    def length_scene_to_viewport(self, length):
        return length * self._scale

    ##############################################

    def viewport_to_scene(self, position):

        point = QPointF(position.x(), -position.y())
        point /= self._scale
        point -= self._translation
        return np.array((point.x(), point.y()), dtype=np.float)

    ##############################################

    def pan_delta_to_scene(self, position):

        # Fixme:
        point = QPointF(position.x(), position.y())
        # point /= self._scale
        return np.array((point.x(), point.y()), dtype=np.float)

####################################################################################################

class QtQuickPaintedSceneItem(QQuickPaintedItem, QtPainter):

    _logger = _module_logger.getChild('QtQuickPaintedSceneItem')

    ##############################################

    def __init__(self, parent=None):

        QQuickPaintedItem.__init__(self, parent)
        QtPainter.__init__(self)

        self.setAntialiasing(True)
        # self.setRenderTarget(QQuickPaintedItem.Image) # high quality antialiasing
        self.setRenderTarget(QQuickPaintedItem.FramebufferObject) # use OpenGL

        self._viewport_area = ViewportArea()

    ##############################################

    def geometryChanged(self, new_geometry, old_geometry):

        print('geometryChanged', new_geometry, old_geometry)
        self._viewport_area.viewport_size = new_geometry
        # if self._scene:
        #     self._update_transformation()
        QQuickPaintedItem.geometryChanged(self, new_geometry, old_geometry)

    ##############################################

    # def _update_transformation(self):

    #     area = self._viewport_area.area
    #     self.translation = - QPointF(area.x.inf, area.y.sup)
    #     self.scale = self._viewport_area.scale_px_by_mm # QtPainter

    ##############################################

    @property
    def scene_area(self):
        return self._viewport_area.area

    ##############################################

    def scene_to_viewport(self, position):
        return self._viewport_area.scene_to_viewport(position)

    ##############################################

    def length_scene_to_viewport(self, length):
        return self._viewport_area.length_scene_to_viewport(length)

    ##############################################

    sceneChanged = Signal()

    @Property(QtScene, notify=sceneChanged)
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, scene):
        if self._scene is not scene:
            print('QtQuickPaintedSceneItem set scene', scene)
            self._logger.info('set scene') # Fixme: don't print ???
            self._scene = scene
            self._viewport_area.scene = scene
            self._viewport_area.fit_scene()
            # self._update_transformation()
            self.update()
            self.sceneChanged.emit()

    ##############################################

    # zoomChanged = Signal()

    # @Property(float, notify=zoomChanged)
    # def zoom(self):
    #     return self._zoom

    # @zoom.setter
    # def zoom(self, zoom):
    #     if self._zoom != zoom:
    #         print('QtQuickPaintedSceneItem zoom', zoom, self.width(), self.height())
    #         self._zoom = zoom
    #         self.set_transformation(zoom)
    #         self.update()
    #         self.zoomChanged.emit()

    ##############################################

    @Property(float)
    def zoom(self):
        return self._viewport_area.scale_px_by_mm

    ##############################################

    @Slot(QPointF, result=str)
    def format_coordinate(self, position):
        scene_position = self._viewport_area.viewport_to_scene(position)
        return '{:.3f}, {:.3f}'.format(scene_position[0], scene_position[1])

    ##############################################

    @Slot(float)
    def zoom_at_center(self, zoom):
        self._viewport_area.zoom_at(self._viewport_area.center, zoom)
        self.update()

    ##############################################

    @Slot(QPointF, float)
    def zoom_at(self, position, zoom):
        print('zoom_at', position, zoom)
        scene_position = self._viewport_area.viewport_to_scene(position)
        self._viewport_area.zoom_at(scene_position, zoom)
        self.update()

    ##############################################

    @Slot()
    def fit_scene(self):
        self._viewport_area.fit_scene()
        self.update()

    ##############################################

    @Slot(QPointF)
    def pan(self, dxy):
        position = self._viewport_area.center + self._viewport_area.pan_delta_to_scene(dxy)
        self._viewport_area.zoom_at(position, self._viewport_area.scale_px_by_mm)
        self.update()

    ##############################################

    @Slot(QPointF)
    def item_at(self, position):

        # Fixme: 1 = 1 cm
        #   as f of zoom ?
        radius = 0.3

        self._scene.update_rtree()
        self._scene.unselect_items()
        scene_position = Vector2D(self._viewport_area.viewport_to_scene(position))
        items = self._scene.item_at(scene_position, radius)
        if items:
            distance, nearest_item = items[0]
            print('nearest item at {} #{:6.2f} {} {}'.format(scene_position, len(items), distance, nearest_item.user_data))
            nearest_item.selected = True
            # Fixme: z_value ???
            for pair in items[1:]:
                distance, item = pair
                print('  {:6.2f} {}'.format(distance, item.user_data))
        self.update()

####################################################################################################

# qmlRegisterType(QtQuickPaintedSceneItem, 'Patro', 1, 0, 'PaintedSceneItem')
