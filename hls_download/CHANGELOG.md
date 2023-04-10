01-27-2023
- Added SZA, SAA, VZA, and VAA to bands that can be download

07-18-2022
- Updated the output .tif to include the V2.0 
- Updated the date format to include month as %mm 

02-08-2022
- update the limit parameter because of time out issue reported by a user.
11-26-2021
- Updated HLS_SuPER.py and README to use HLS V2.0 data.

06-02-2021
- Updated README to reflect public release of HLS L30 v1.5.   

03-15-2021
- Updated `collections` to product `shortnames` (in place of `concept_id`) to align with latest release of CMR-STAC.   
- Updated logic for search responses with no data found (now returns valid response with `numberReturned` = 0).   
- Changed all queries to CMR-STAC LPCLOUD Search endpoint from **GET** requests to **POST** requests.   
- Updated README with link to CHANGELOG.md  

02-12-2021
- Replaced `bounding_box` with `bbox` and `concept_id` with `collections` to fix breaking change in CMR-STAC search parameter spec and added CHANGELOG.md to repo and updated `while` loop logic in `hls_su.py` to fix breaking change in CMR-STAC response for a search query with no granules returned

01-29-2021
- Added second retry for files that fail to download and/or process

01-27-2021
- Merge branch 'master' of ssh://git.earthdata.nasa.gov:7999/lpdur/hls-super-script into develop
- Added logic to determine OS for netrc generation and pagination for queries with 200+ granules
- updated HLS_PER.py to latest version

01-26-2021
- adjusted netrc file name to accomodate Windows

01-25-2021
- updated HLS_PER.py so that Windows will read the netrc

01-20-2021
- Pull request #4: Updated code and readme per peer review suggestions

01-19-2021
- Added printout notifying users if data for a product were found
- Updated code and readme per peer review suggestions

12-30-2020
- Pull request #3: Added user prompt to continue downloading/processing and cleaned up in-line comments

12-29-2020
- fixed quality filtering bug
- Fixed Scale = False bug, updated print outs to reflect # granules/files, and updated nc4 output name convention
- Updated Readme
- Reconciled README conflicts
- Reconciled README conflicts
- Updated Readme
- Added user prompt to continue downloading/processing and cleaned up in-line comments

12-23-2020
- Pull request #1: Amf review

12-21-2020
- Readme edits

12-18-2020
- updated readme file

12-17-2020
- Updated README

12-16-2020
- Initial Commit
