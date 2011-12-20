#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2010                       ##
##            Vincent Pottier <@.> 2010                                  ##
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
DROP TABLE IF EXISTS kw_tmp;
SELECT DISTINCT ON (nodes.geom)
    nodes.id,
    ST_AsText(nodes.geom) AS way,
    SUBSTRING(nodes.tags->'description' from '#"%#" -%' for '#') AS desc
FROM
    nodes
        JOIN (VALUES
            ('bâtiment'),
            ('blockhaus'),
            ('château'),
            ('chapelle'),
            ('cheminée'),
            ('clocher'),
            ('croix'),
            ('église'),
            ('mairie'),
            ('maison'),
            ('phare'),
            ('réservoir'),
            ('silo'),
            ('tour')
        ) AS k(kw) ON
            nodes.tags ? 'man_made' AND
            nodes.tags->'man_made' = 'survey_point' AND
            nodes.tags ? 'description' AND
            position(k.kw in lower(nodes.tags->'description')) > 0 AND
            position('point constaté détruit' in lower(nodes.tags->'description')) = 0
        LEFT OUTER JOIN ways ON
            ways.tags ? 'building' AND
            is_polygon AND
            ST_Within(nodes.geom, ways.linestring)
WHERE
    ways.id IS NULL
;
"""

class Analyser_Osmosis_Geodesie(Analyser_Osmosis):

    def __init__(self, config, logger = None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs[1] = {"item":"7010", "desc":{"fr":"Repère géodésique sans bâtiment", "en":"Geodesic mark without building"} }

    def analyser_osmosis(self):
        self.run(sql10, lambda res: {"class":1,
            "data":[self.node_full, self.positionAsText],
            "text":{"en":res[2]} } )
