# assignment02

# phenomenon type
Honestly, I had trouble deciding on what phenomenon to do so I kind of sort of just yanked all of em at once. Got the data (in csv format) of specifically all the 2026 records of the locations and types of extreme weather sighted in the US. Took it from The National Centers for Environmental Information (NCEI).

# source link
https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/

# How does one run it?
you just run fetch.py followed by plot.py via uv and it'll generate the gif of a map of the US and spots that represents extreme weather, color coded by the EVENT_TYPE of the entry and featuring the tallied number of incidents that have showed up so far (in the intervals of a singular month for each frame)

# how does it work?
We can see the spread of the entries across the geographical locations, calculated and plotted via the coordinates within the .csv files, and to reduce clutter there is a function within fetch.py that's called download_boundary() where it grabs the required stats from the csv file and stuffs it into a new json file, then uses draw_states() in plot.py to generate the gif of the map of the US and plots the points.