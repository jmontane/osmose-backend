#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights                        ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from Analyser_Osmosis import Analyser_Osmosis

sql10 = """
SELECT
    ways3.id,
    ST_AsText(ST_Centroid(ways3.linestring))
FROM
    {0}ways AS buildings,
    {1}ways AS ways3
WHERE
    ST_NPoints(ways3.linestring)=4 AND
    ways3.id != buildings.id AND
    ways3.tags ? 'building' AND ways3.tags->'building' != 'no' AND
    buildings.tags ? 'building' AND buildings.tags->'building' != 'no' AND 
    (buildings.tags ? 'wall' = ways3.tags ? 'wall') AND
    (ST_Intersects(buildings.linestring, ways3.linestring) OR ST_Touches(buildings.linestring, ways3.linestring))
group by ways3.id,ways3.linestring
;
"""


class Analyser_Osmosis_Building_3nodes(Analyser_Osmosis):

    def __init__(self, config, logger = None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs_change[1] = {"item":"0", "level": 3, "tag": ["building", "fix:imagery"], "desc": T_(u"Merge building (triangle)") }      
        self.callback70 = lambda res: {"class":1, "data":[self.way_full, self.positionAsText]}

    def analyser_osmosis_all(self):
        self.run(sql10.format("", ""), self.callback70)

