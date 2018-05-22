# GeoTaggedPhotos
Turning Geotagging photos into photo points for Google Earth and ArcGIS Using Python

If your phone has location turned on  the picture will contain latitude and longitude values in the metadata

The script will take pictures from a user input folder and correctly locate the photo spatially on the map if the mobile phone had location services enabled when the photo was taken. The user is then asked if they want the output to be a Google Earth KMZ file for general viewing or if they want to save their file in a shapefile for use in GIS. For each photo, the script reads the location coordinates and adds the photo to the KMZ or shapefile. The user can input specific project names for organization purposes.
