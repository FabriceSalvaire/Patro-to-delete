####################################################################################################
#
# Patro - A Python library to make patterns for fashion design
# Copyright (C) 2018 Fabrice Salvaire
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

from pathlib import Path

import yaml

####################################################################################################

class Measurement:

    ##############################################

    def __init__(self, name, full_name, description, default_value=0):

        self._name = name
        self._full_name = full_name
        self._description = description
        self._default_value = default_value

    ##############################################

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    ##############################################

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, value):
        self._full_name = value

    ##############################################

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    ##############################################

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value

####################################################################################################

class ValentinaMeasurement(Measurement):

    ##############################################

    def __init__(self, code, name, full_name, description, default_value):

        super().__init__(name, full_name, description, default_value)

        self._code = code

    ##############################################

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

####################################################################################################

class StandardMeasurement:

    ##############################################

    def __init__(self):

        self._names = {}

    ##############################################

    def __len__(self):
        return len(self._names)

    ##############################################

    def __iter__(self):
        return iter(self._names.values())

    ##############################################

    def __getitem__(self, name):
        return self._names[name]

    ##############################################

    def __contains__(self, name):
        return name in self._names

    ##############################################

    def add(self, measurement):

        if measurement.name not in self._names:
            self._names[measurement.name] = measurement
        else:
            raise NameError('{} is already registered'.format(measurement.name))

    ##############################################

    def dump(self):

        template = '''{0.name}
- {0.full_name}
- {0.description}
- {0.default_value}
'''

        for measurement in self:
            print(template.format(measurement))

####################################################################################################

class ValentinaStandardMeasurement(StandardMeasurement):

    ##############################################

    def __init__(self):

        super().__init__()

        yaml_path = Path(__file__).parent.joinpath('data', 'valentina-standard-measurements.yaml')
        with open(yaml_path, 'r') as fh:
            data = yaml.load(fh.read())
            for topic in data.values():
                for code, measurement_data in topic['measurements'].items():
                    measurement = ValentinaMeasurement(code, *measurement_data)
                    self.add(measurement)