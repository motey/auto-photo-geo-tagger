# auto-photo-geo-tagger
Automaticly geotag your personal photos (local or in the cloud) by supplying gpx track file(s)

Status: pre-alpha, WIP (You just have to wait a bit :) )

- [auto-photo-geo-tagger](#auto-photo-geo-tagger)
- [tl;tr](#tltr)
  - [Is this applicable to my photos?](#is-this-applicable-to-my-photos)
  - [Which photos will not be tagged (without userinput)](#which-photos-will-not-be-tagged-without-userinput)
- [In detail](#in-detail)
  - [Whats different compared to other existing solutions?](#whats-different-compared-to-other-existing-solutions)
- [Warnings and caveats](#warnings-and-caveats)

# tl;tr

## Is this applicable to my photos? 

If you want to geotag **personal** photos with **personal** GPX tracks: Yes!

* Your GPX Tracks are single party only. No sharing of GPX Tracks with friends
* Your photos are single party only. e.g. No group sharing folder of photos with no GPS tags from your holidays at this end of the world and your friends holidays at the other end of the world at the same time.
* Your photos are always timestamped in the local time (With correct [daylight saving time shift](https://en.wikipedia.org/wiki/Daylight_saving_time)). Meaning: Set your camera **always** to the local time before starting shooting photos.

## Which photos will not be tagged (without userinput)

* Photos of days you crossed a timezone
* Photos too far away from any GPX Trackpoint (in terms of distance in time and or travel)

# In detail

## Whats different compared to other existing solutions?

Compared to solutions i found, this software tries to geotag your photos in the background without your input.

**The Timezone problem**

The problem with autogeotagging photos is that your photos timestamp is usually timezone unaware. This means `2022.05.28 12:00:00` could express `2022.05.28 10:00:00-UTC` in [Berlin, DE](https://de.wikipedia.org/wiki/Berlin) or `2022.05.28 00:00:00-UTC` in [Tuvalu](https://de.wikipedia.org/wiki/Tuvalu). Your GPX Track time is timezone aware and usaly saved as UTC time. So we can not easily match the *naive* date `2022.05.28 12:00:00` to `2022.05.28 10:00:00-UTC` (assuming you hang around in Berlin)

**But let us make some assumptions**

As long as you are not traveling very fast above our earth all the time we can make some assumptions:

* As long as you did not cross any timezone in the last 24hours according to the GPX track
  * Any photo shoot at this day is in the local timezone according to the GPX track

Now we can match, the photo the GPS coordinates

# Warnings and caveats

* Be aware apgt needs to load every image to check for exif data. If you are running apgt on large image libraries keep the apgt process as close to your file sources as possible.  
For example if you have your photos on cloud storage that you pay by bandwith and run apgt every hour on your home server, all your image will be transmitted every hour. You cloud cost could skyrocket in such a setup.  
In such a setup is makes more sense to run apgt not as a service but selective on certain dirs once.
* APGT assumes you always set your camera to local time ("Daylight saving time" aware), otherwise matching between photo time and GPX Trackpoint time will not be possible
