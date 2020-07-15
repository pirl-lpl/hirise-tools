Queries
=======

Queries of varying degrees of usefulness for extracting information about HiRISE data from
the HiRISE catalog of the HiCat Database. See
https://hirise.lpl.arizona.edu/HiCat/Data_Dictionary/index.shtml for the database 
information. Note that to use these queries the user has to have the appropriate accounts
and permissions for that database. As such, these queries are intended for use by HiRISE
team members.

These queries are largely intended to be modified by the user to suit specific tasks, and
are distinctly USER BEWARE in most cases. Testing tends to be sharply limited to only the
specific use case that the query was built to serve.

`mode_query_PGH.sql` - Query intended to identify the imaging mode for all, or a subset
of, planned HiRISE images. "Imaging mode" refers to the configuration of each of the 13
(excluding RED9) CCDs - which ones are returning data, and the binning mode for each. See
the query itself for some additional detail.

`mode_query_PGH_results.txt` - Sample output of the similarly named query.