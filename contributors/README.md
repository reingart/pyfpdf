# Contributors map

The `build_contributors_html_page.py` script queries the GitHub v3 API
in order to generate the web page `contributors.html` with all the locations
of `fpdf2` contributors that included such information on their profile page.

Then the `contributors.html` page uses [LeafletJS](https://leafletjs.com)
and [Leaflet Control Geocoder](https://github.com/perliedman/leaflet-control-geocoder)
in order to place all contributors on a world map.

As of june 2021, the map looks like this (click on it to access the up-to-date online version):

[![Contributors map](contributors-map-small.png)](https://pyfpdf.github.io/fpdf2/contributors.html)
