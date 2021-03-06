=========
CIPPtools
=========

*Convenience Tools for HiRISE CIPP work*

---------------------------------

These are a very loose collection of Python 3 programs for helping someone 
serving as a HiRISE CIPP perform various tasks.


* Free software: Apache Software License 2.0

Conversion
----------
The ``ptf2csv.py`` and ``csv2ptf.py`` function mostly like the Perl
equivalents that have been in use by HiRISE for a decade.

The difference is that ``ptf2csv.py`` has an option to add a
'HiReport Link' column to the end of the output CSV file.  This
column contains a formula that when read in by most spreadsheet
programs will result in a clickable link in that cell of your
spreadsheet to allow easy checking of HiReport.

And ``csv2ptf.py`` basically ignores any non-PTF columns in your
.csv file (like maybe that HiReport column that you had ``ptf2csv.py``
put in, or any other columns that you might have added).


Working with the HiTList
------------------------
``special_priorities.py`` will modify all of those 11000 priorities
and spread them out from 11000 to 11400, based on the priorities
from the Special Target Requests by Cycle page. People have diligently
entered in priorities from 1 to 10 for those Special Targets (WTHs,
HiKERs, CaSSIS coordination targets, etc.).  If you would like to
incorporate those priorities, you can use ``special_priorities.py``
on the delivered HiTList.ptf to create a new "special.ptf" where
those records have altered priorities.  This means that once you
sort by priority everyone's highest rated WTHs will be priority
11400, and maybe easier to pick between.  Similarly, with this
priority modification in place, you you can compare two of these
that might fall in the same orbit, just by looking at their (now modified)
priority value.

``prioritize_by_orbit.py`` can be used on the HiTList you get from
your HiTS (or the PTF you created with ``special_priorities.py``)
to clearly flag (by changing their existing priority from positive
to negative) which lower-priority observations in each orbit are
'excluded' by the latitude-exclusion zone (this latitude zone
exclusion is 40 degrees on either side of observation for the
highest priority observations, and decreases with decreasing
priority).

``priority_rewrite.py`` can be used near the end of your process when you
have a bunch of observations that all have the same priority that each need
a unique priority.  This program takes that block of entries, and assigns unique
priorities based on latitude.

``orbit_count.py`` again, a program of the same name as a Perl program that we have.
The difference here is that this one is 'aware' of the possible negative priorities
given by ``prioritize_by_orbit.py``, prints out an observation count histogram (how many 
orbits have 3 observations, etc.) Although it doesn't report data volume like
the Perl verison does (but it could).


TOS
---
What made it through TOS?  Did my WTH make it through TOS?  Did my WTH even make
it into the HiTLIST?  Did you elminiate my WTH from the HiTList, you monster?

Or replace 'WTH' with HiKERs or CaSSIS targets or really any list of suggestions
that you want to know are contained in a PTF.

All of these questions can be answered with a PTF, text copied from the WTH list
wiki page, and ``tos_success.py``.


WARNING
-------
**There are some tests, but user beware.**
