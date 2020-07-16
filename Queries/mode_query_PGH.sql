/* Quick (ish) and dirty (very) query to display the mode and number of lines 
for a set of observation IDs. Only works for imaging modes that are, in fact, 
defined, based on enabled CCDs and binning for those CCDs. Assumes the user has 
read access to the database being queried.

USER BEWARE!! Observations that don't match one of these modes are simply not 
reported in the output. FURTHER BEWARE!! If you add anything else from 
Planned_CCD_Parameters in the select clause and the values for that field aren't 
the same for each CCD, that observation will be omitted from the output. 

INTENDED FOR INFORMATION ONLY. DON'T RELY ON THIS FOR VERIFICATION OF CRUCIAL 
PLANNING DETAILS!

To use: 

First make sure you are either working from a PIRL system or with a PIRL VPN up and 
running. On the command line, type the following:

% mysql < mode_query.sql > mode_query_PGH_results.txt

If you so choose, rename mode_query_PGH_results.txt to whatever works for you. Also, you 
can replace ">" with ">!" to overwrite existing files (in cshell. It's something 
else in bash). Also also, YMMV depending on how you've set up your .my.cnf file. 
Remember, USER BEWARE (and user contact PIRL managers if you have access issues).

To do this over just a subset of observations, rather than all of them, obtain a list of 
observation IDs. Remove the comment markers and replace <list> in EACH SECTION BELOW 
(currently 4 active (and 1 commented) sections) with your list of observation 
IDs.

To add new modes, copy and paste one entire section, from the opening "select" 
to the closing "having count(*) = x". Go to the end of the file. Delete the 
semicolon, add the word union, then paste your selection. Change the name of the 
mode, the binning as required for each ccd, the value for the count (it should 
match the number of CCDs in the mode - 13 if all CCDs are used, however many are 
active if fewer than that are used), and add a semicolon at the end of the new 
section just added. 

*/
use HiRISE;
#Bin 1A
select 
    "Bin 1A" as "Mode",
    PO.OBSERVATION_ID, 
    PO.CENTER_LONGITUDE,
    PO.CENTER_PLANETOCENTRIC_LATITUDE,
    PO.LSUBS,
    PCCD.IMAGE_LINES*PCCD.BINNING as BIN1_Equivalent_Lines
from 
    Planned_Observations as PO 
join 
    Planned_CCD_Parameters as PCCD 
on 
    PO.ID = PCCD.PLANNED_OBSERVATIONS_ID 
where 
/*    PO.OBSERVATION_ID in (<list>)
and
*/
    ((PCCD.CCD_NAME = "RED0" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED1" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED2" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED3" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED4" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED5" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED6" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED7" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED8" and PCCD.BINNING = 1)
or 
    (PCCD.CCD_NAME = "IR10" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "IR11" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "BG12" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "BG13" and PCCD.BINNING = 2)) 
group by 
    PLANNED_OBSERVATIONS_ID, BIN1_Equivalent_Lines having count(*) = 13
union
#Bin 1
select 
    "Bin 1" as "Mode",
    PO.OBSERVATION_ID, 
    PO.CENTER_LONGITUDE,
    PO.CENTER_PLANETOCENTRIC_LATITUDE,
    PO.LSUBS,
    PCCD.IMAGE_LINES*PCCD.BINNING as BIN1_Equivalent_Lines
from 
    Planned_Observations as PO 
join 
    Planned_CCD_Parameters as PCCD 
on 
    PO.ID = PCCD.PLANNED_OBSERVATIONS_ID 
where 
/*    PO.OBSERVATION_ID in (<list>)
and
*/
    ((PCCD.CCD_NAME = "RED0" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED1" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED2" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED3" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED4" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED5" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED6" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED7" and PCCD.BINNING = 1) 
or 
    (PCCD.CCD_NAME = "RED8" and PCCD.BINNING = 1)
or 
    (PCCD.CCD_NAME = "IR10" and PCCD.BINNING = 4) 
or 
    (PCCD.CCD_NAME = "IR11" and PCCD.BINNING = 4) 
or 
    (PCCD.CCD_NAME = "BG12" and PCCD.BINNING = 4) 
or 
    (PCCD.CCD_NAME = "BG13" and PCCD.BINNING = 4)) 
group by 
    PLANNED_OBSERVATIONS_ID, BIN1_Equivalent_Lines having count(*) = 13

union
#Bin 2A
select 
    "Bin 2A" as "Mode",
    PO.OBSERVATION_ID, 
    PO.CENTER_LONGITUDE,
    PO.CENTER_PLANETOCENTRIC_LATITUDE,
    PO.LSUBS,
    PCCD.IMAGE_LINES*PCCD.BINNING as BIN1_Equivalent_Lines
from 
    Planned_Observations as PO 
join 
    Planned_CCD_Parameters as PCCD 
on 
    PO.ID = PCCD.PLANNED_OBSERVATIONS_ID 
where 
/*    PO.OBSERVATION_ID in (<list>)
and
*/
    ((PCCD.CCD_NAME = "RED0" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED1" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED2" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED3" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED4" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED5" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED6" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED7" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED8" and PCCD.BINNING = 2)
or 
    (PCCD.CCD_NAME = "IR10" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "IR11" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "BG12" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "BG13" and PCCD.BINNING = 2)) 
group by 
    PLANNED_OBSERVATIONS_ID, BIN1_Equivalent_Lines having count(*) = 13

union
#Bin 2
select 
    "Bin 2" as "Mode",
    PO.OBSERVATION_ID, 
    PO.CENTER_LONGITUDE,
    PO.CENTER_PLANETOCENTRIC_LATITUDE,
    PO.LSUBS,
    PCCD.IMAGE_LINES*PCCD.BINNING as BIN1_Equivalent_Lines
from 
    Planned_Observations as PO 
join 
    Planned_CCD_Parameters as PCCD 
on 
    PO.ID = PCCD.PLANNED_OBSERVATIONS_ID 
where 
/*    PO.OBSERVATION_ID in (<list>)
and
*/
    ((PCCD.CCD_NAME = "RED0" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED1" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED2" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED3" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED4" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED5" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED6" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED7" and PCCD.BINNING = 2) 
or 
    (PCCD.CCD_NAME = "RED8" and PCCD.BINNING = 2)
or 
    (PCCD.CCD_NAME = "IR10" and PCCD.BINNING = 4) 
or 
    (PCCD.CCD_NAME = "IR11" and PCCD.BINNING = 4) 
or 
    (PCCD.CCD_NAME = "BG12" and PCCD.BINNING = 4) 
or 
    (PCCD.CCD_NAME = "BG13" and PCCD.BINNING = 4)) 
group by 
    PLANNED_OBSERVATIONS_ID, BIN1_Equivalent_Lines having count(*) = 13;
/* 
This identifies warmups. To use, delete the semicolon after the previous 
section, the "/*" on the previous line, all of this text, and the trailing star 
and slash on the final line of this document.

union

select 
    "Warmup NIO" as "Mode",
    PO.OBSERVATION_ID, 
    PO.CENTER_LONGITUDE,
    PO.CENTER_PLANETOCENTRIC_LATITUDE,
    PO.LSUBS,
    PCCD.IMAGE_LINES*PCCD.BINNING as BIN1_Equivalent_Lines
from 
    Planned_Observations as PO 
join 
    Planned_CCD_Parameters as PCCD 
on 
    PO.ID = PCCD.PLANNED_OBSERVATIONS_ID 
where 
    PO.OBSERVATION_ID in (<list>)
and
    ((PCCD.CCD_NAME = "RED0" and PCCD.BINNING = 16) 
or 
    (PCCD.CCD_NAME = "RED1" and PCCD.BINNING = 16) 
or 
    (PCCD.CCD_NAME = "RED3" and PCCD.BINNING = 16) 
or 
    (PCCD.CCD_NAME = "IR10" and PCCD.BINNING = 16)) 
group by 
    PLANNED_OBSERVATIONS_ID, BIN1_Equivalent_Lines having count(*) = 4;

*/