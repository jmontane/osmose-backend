#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2010                       ##
##            Frédéric Rodrigo <****@free.fr> 2010                       ##
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
    id,
    ST_AsText(geom)
FROM
(
    SELECT
        ways.id,
        geom
    FROM
    (
        SELECT
            ways.id,
            ST_Centroid(linestring) AS geom
        FROM
            ways
        WHERE
            -- tags
            ways.tags?'highway' AND
            ways.tags->'highway' IN ('primary','secondary','tertiary','residential') AND -- c'est une route pour voiture
            (NOT ways.tags?'junction' OR ways.tags->'junction' != 'roundabout') AND
            NOT ways.tags?'area' AND
            (NOT ways.tags?'name' OR ways.tags->'name' LIKE 'Rond%') AND -- pas de nom ou commence par 'Rond'
            -- geometry
            ways.is_polygon AND -- C'est un polygone
            ST_NPoints(linestring) < 24 AND
            ST_MaxDistance(ST_Transform(linestring,2154),ST_Transform(linestring,2154)) < 70 AND -- Le way fait moins de 80m de diametre
            ST_Area(linestring)/ST_Area(ST_MinimumBoundingCircle(linestring)) > 0.6 -- 90% de rp recouvrent plus 60% du cercle englobant
    ) AS ways
        JOIN way_nodes ON
            way_nodes.way_id = ways.id
        JOIN way_nodes AS o ON
            way_nodes.node_id = o.node_id AND
            o.way_id != way_nodes.way_id
    GROUP BY
        ways.id,
        way_nodes.node_id,
        geom
    HAVING
        COUNT(*) >= 2 -- selection des noueds avec ou moins deux voies
) AS t0
GROUP BY
    id,
    geom
HAVING
    COUNT(*) >= 2 -- selection des rond-points connecté a au moins deux voies
ORDER BY
    id
;
"""

class Analyser_Osmosis_Roundabout(Analyser_Osmosis):

    def __init__(self, config, logger = None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs[1] = {"item":"2010", "desc":{"fr":"Manque junction=roundabout", "en":"Missing junction=roundabout"} }

    def analyser_osmosis(self):
        self.run(sql10, lambda res: {"class":1, "data":[self.way_full, self.positionAsText]} )
