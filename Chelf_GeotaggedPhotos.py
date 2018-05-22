# Christina Chelf
# Final Project
# Ask user for location of geotagged photos, ask if they want their photos in GIS or in Google earth. Output a file in choosen program.
# This has only been tested with Android photos on a Windows Machine.
import arcpy				
from arcpy import env
import simplekml
from simplekml import Kml
import PIL
from PIL import Image 
from PIL.ExifTags import TAGS, GPSTAGS
import os
env.overwriteOutput = True

print "This script takes all the photos in a folder and geocodes them into Google Earth (KMZ) or GIS (Feature Class)."
print "Photos must be jpg format."
print ""

################################
## Extract geotagged photo XYs##
################################

# Functions that take geotagged photos and extract XYs
# Credit to: https://gist.github.com/erans/983821

# Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags
def get_exif_data(image):
	exif_data = {}
	info = image._getexif() 
	if info:
		for tag, value in info.items():
			decoded = TAGS.get(tag, tag)
			if decoded == "GPSInfo":
				gps_data = {}
				for t in value:
					sub_decoded = GPSTAGS.get(t, t)
					gps_data[sub_decoded] = value[t]
				exif_data[decoded] = gps_data
			else:
				exif_data[decoded] = value
	return exif_data
# Checks if geotags exists
def _get_if_exist(data, key):
	if key in data:
		return data[key]
	return None
# Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
def _convert_to_degress(value):
	d0 = value[0][0]
	d1 = value[0][1]
	d = float(d0) / float(d1)

	m0 = value[1][0]
	m1 = value[1][1]
	m = float(m0) / float(m1)

	s0 = value[2][0]
	s1 = value[2][1]
	s = float(s0) / float(s1)

	return d + (m / 60.0) + (s / 3600.0)
# Returns the latitude and longitude, if available, from the provided exif_data
def get_lat_lon(exif_data):
	lat = None
	lon = None

	if "GPSInfo" in exif_data:		
		gps_info = exif_data["GPSInfo"]
		gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
		gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
		gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
		gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

		if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
			lat = _convert_to_degress(gps_latitude)
			if gps_latitude_ref != "N":                     
				lat = 0 - lat

			lon = _convert_to_degress(gps_longitude)
			if gps_longitude_ref != "E":
				lon = 0 - lon
	return lat, lon

########################
## Get input variables##
########################

# User folder input variables
inputfolder = raw_input("Please input the folder where your images are saved: ")
# Validates users input is a folder that exists.
while arcpy.Exists(inputfolder) == False:
	print "That is not an existing folder, try again."
	inputfolder = raw_input("Please input the full path to your photos, Example: C:\Users\cchelf\Desktop\Photos:")
print " "

# User format input variables
outputformat = raw_input("Do you want to see these locations with GIS or GoogleEarth?: ")
# Validate user choose KMZ or FC 
while str.lower(outputformat) != "gis" and str.lower(outputformat) != "g i s" and str.lower(outputformat) != "g.i.s" and str.lower(outputformat) != "googleearth" and str.lower(outputformat) != "google earth" and str.lower(outputformat) != "ge":
	print "Invalid option: Please choose 'GoogleEarth' or 'GIS'"
	outputformat = raw_input("Do you want to see these locations with GIS or GoogleEarth?: ")
print " "

# Create project name variable
projectname = raw_input("What is your project name? This will be used to name output file, no numbers, spaces or special characters in name: ")
# Validate for naming purposes
while projectname.isalpha() == False:
	print "Invalid option: no numbers, spaces or special characters in name."
	projectname = raw_input("What is your project name? This will be used to name output file.: ")
print " "
	
# Checking to see if folder path ends with final / (needed for later in script)
if inputfolder[-1] == "/" or inputfolder[-1] == "\\":
	folder = inputfolder
else:
	folder = inputfolder + "\\"

###########################################################
## Depending on user input creates a feature class or KMZ##
###########################################################


# Creates shapefile and populates based on photo points
if str.lower(outputformat) == "gis" or str.lower(outputformat) =="g i s" or str.lower(outputformat) =="g.i.s":
	print "Alrighty, making a feature class..."
	print " "
	
	# Adds XYs to feature class
	if __name__ == "__main__":
		
		# Create GDB, feature class, set spatial reference
		spatialref = arcpy.SpatialReference(4326)
		myGDB = arcpy.CreateFileGDB_management(folder, projectname)
		myfc = arcpy.CreateFeatureclass_management(myGDB, projectname, "POINT", "","","", spatialref)
		
		# Add fields
		arcpy.AddField_management(myfc, "Name", "TEXT", "", "", 100)	# Add field to store photo name
		arcpy.AddField_management(myfc, "Path", "TEXT", "", "", 300)	# Add field to store photo path
		arcpy.AddField_management(myfc, "Notes", "TEXT", "", "", 200)	# Add field for user to input notes later

		# Itterates through photos in folder
		for photo in os.listdir(folder):                                                                                                    
			if photo.lower().endswith("jpg"): 
				photopath = "<img src=" + "'" + folder + photo +"'" + " width='250' />"
				image = Image.open(folder + photo)                		# Gives variable of photo file 
				exif_data = get_exif_data(image)                        # Get the exif data from the image  
				my_point_lat, my_point_lng = get_lat_lon(exif_data)     # Create lat lng  variables
				xy = arcpy.Point(my_point_lng, my_point_lat)            # Adds coordinates to point list
				with arcpy.da.InsertCursor(myfc, ["Name", "Path","SHAPE@XY"] ) as cursor:  # Iterates through rows in shapefile
					cursor.insertRow([photo, photopath, xy])                # Adds XYs to rows in shapefile                                                                                                 
	print "Success! Check your input folder to find your feature class. It will be called " +"'"+ projectname + "' in " + projectname + ".gdb"

# Creates Google Earth KMZ file and populates based on photo points
elif str.lower(outputformat) == "googleearth" or str.lower(outputformat) == "google earth" or str.lower(outputformat) == "ge":
	print "Alrighty, making a KMZ..."
	print " "
	
	# Create empty KML
	kml = simplekml.Kml()												

	# Adds XYs to KMZ
	if __name__ == "__main__":												
		for photo in os.listdir(folder): 								# Directs to photo files
			if photo.lower().endswith("jpg"): 
				image = Image.open(folder + "/" + photo) 				# Gives variable of photo file to include all files within file
				exif_data = get_exif_data(image)                        # Get the exif data from the image 
				my_point_lat, my_point_lng = get_lat_lon(exif_data)     # Create lat lng  variables
				pnt = kml.newpoint(name=photo)                          # Create new points within KMZ based on original photo name
				pnt.coords = [(my_point_lng, my_point_lat)]             # Adds extracted coordinates to KMZ
				picpath = kml.addfile(folder + photo)
				pnt.description = '<img src="' + picpath +'" alt="picture" width="400" align="left" />'
				kml.savekmz(folder +projectname+".kmz")                       	# Saves KMZ
	print "Success! Check your input folder to find your KMZ. It will be called " +"'"+ projectname+".kmz'"
else:
	print "Oops something went terribly wrong."