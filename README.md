# auto-photo-geo-tagger
Automaticly geotag your photos (local or in the cloud) by supplying gpx track file(s)

Status: pre-alpha, WIP (You just have to wait a bit :) )


# Warnings and caveats

* Be aware apgt needs to load every image to check for exif data. If you are running apgt on large image libraries keep the apgt process as close to your file sources as possible.  
For example if you have your photos on cloud storage that you pay by bandwith and run apgt every hour on your home server, all your image will be transmitted every hour. You cloud cost could skyrocket in such a setup.  
In such a setup is makes more sense to run apgt not as a service but selective on certain dirs once.
* We assume you always setup your camera to local time ("Daylight saving time" aware), otherwise matching between photo time and GPX Trackpoint time will fail
