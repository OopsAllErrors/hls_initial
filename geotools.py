import geopandas as gp
from shapely import geometry
import simplekml

#A simple datatype-flexible kml creator. Defaults to an object that gets added into on each call.
def qkml(geo,name='', color='00ffff', kml=simplekml.Kml()):
    if isinstance(geo,list):                           #If given a list,
        doc = kml.newdocument(name=name)
        for item in geo:                               #Step through the list.
            doc = ckml(item,name=name,color=color,kml=doc)
    elif isinstance(geo,gp.GeoDataFrame):             #If given a geodataframe,
        doc = kml.newdocument(name=name)
        if 'Name' in geo.columns:
            for row in geo.iterrows():                 #Step through the database.
                doc2 = doc.newdocument(name=row[1]['Name'])
                doc2 = ckml(row[1]['geometry'],name=row[1]['Name'],color=color,kml=doc2)
        else:
            count = 1
            for row in geo.iterrows():                 #Step through the database.
                doc = ckml(row[1]['geometry'],name=name+'_'+str(count),color=color,kml=doc)
                count += 1
    elif is_geom(geo):                                 #If given a geometry,
        if isinstance(geo,geometry.Point):             #For Points,
            pnt = kml.newpoint(name=name)
            pnt.coords = geo.coords[:]
        elif isinstance(geo,geometry.MultiPoint):      #For MultiPoints
            point_count = 1
            for point in geo:
                pnt = kml.newpoint(name=name+'_'+str(point_count))
                pnt.coords = point.coords[:]
                point_count += 1
        elif isinstance(geo,geometry.Polygon):         #For Polygons,
            plg = kml.newpolygon(name=name, altitudemode=simplekml.AltitudeMode.clamptoground)
            plg.outerboundaryis.coords = geo.exterior.coords[:]
            plg.style.polystyle.color = '44'+color
            plg.linestyle = simplekml.LineStyle(width=3, color='ff'+color)
        elif isinstance(geo,geometry.MultiPolygon):    #For Multipolygons,
            poly_count = 1
            for poly in geo:
                plg = kml.newpolygon(name=name+'_'+str(poly_count), altitudemode=simplekml.AltitudeMode.clamptoground)
                plg.outerboundaryis.coords = poly.exterior.coords[:]
                plg.style.polystyle.color = '44'+color
                plg.linestyle = simplekml.LineStyle(width=3, color='ff'+color)
                poly_count += 1
        elif isinstance(geo,geometry.LineString):      #For LineStrings/PolyLines
            nl = kml.newlinestring(name=name, altitudemode=simplekml.AltitudeMode.clamptoground)
            nl.linestyle = simplekml.LineStyle(width=3, color='ff'+color)
            nl.coords = geo.coords[:]
    return kml