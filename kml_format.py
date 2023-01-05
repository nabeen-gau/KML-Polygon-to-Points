TEXT_1 = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
\t<name>"""

TEXT_2 = """</name>
\t<StyleMap id="m_ylw-pushpin">
\t\t<Pair>
\t\t\t<key>normal</key>
\t\t\t<styleUrl>#s_ylw-pushpin</styleUrl>
\t</Pair>
\t\t<Pair>
\t\t\t<key>highlight</key>
\t\t\t<styleUrl>#s_ylw-pushpin_hl</styleUrl>
\t\t</Pair>
\t</StyleMap>
\t<Style id="s_ylw-pushpin">
\t\t<IconStyle>
\t\t\t<scale>1.1</scale>
\t\t\t<Icon>
\t\t\t\t<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
\t\t\t</Icon>
\t\t\t<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
\t\t</IconStyle>
\t</Style>
\t<Style id="s_ylw-pushpin_hl">
\t\t<IconStyle>
\t\t\t<scale>1.3</scale>
\t\t\t<Icon>
\t\t\t\t<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
\t\t\t</Icon>
\t\t\t<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
\t\t</IconStyle>
\t</Style>
\t<Placemark>
\t\t<name>"""

TEXT_3 = """</name>
\t\t<styleUrl>#m_ylw-pushpin</styleUrl>
\t\t<LineString>
\t\t\t<tessellate>1</tessellate>
\t\t\t<coordinates>
"""

TEXT_4 = """\t\t\t</coordinates>
\t\t</LineString>
\t</Placemark>
</Document>
</kml>"""
