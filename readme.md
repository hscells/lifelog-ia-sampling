# Lifelog image sampling for use in annotations

This set of scripts and files will cluster images in a lifelog
collection which provides a suitable collection to sample from.

# Setup

The following requirements must be met (This is what I build with):

 - gcc (c++) `Apple LLVM version 7.3.0 (clang-703.0.31)`
 - opencv `version 2.4.12_2`
 - go `go1.5.3 darwin/amd64`
 - python `Python 2.7.10` with `scipy (0.16.1)`
 
To build the c++ and go files:

 - run `./build.sh`
 
# Running the files

There are a couple of handy shell files to glue everything together:

## Generating feature vectors

The feature vectors are a list of histograms which are used in the 
clustering process. This is a pre-processing step. The files for this
step are listed under the `feature-vectors` folder.

 - `generate-feature-vectors.sh path/to/images images.txt vectors.txt`
 
Where `path/to/images` is the directory or directories that contain the
lifelog images, and where `images.txt` and `vectors.txt` are output
file names that the script produces. The important file that is produced
in this process will be whatever `vectors.txt` is named by prepended 
with `processed-`.

## Clustering images

The clustering process is described [here](http://research.nii.ac.jp/ntcir/workshop/OnlineProceedings12/pdf/ntcir/LIFELOG/05-NTCIR12-LIFELOG-ScellsH.pdf).
To start the process, run:

 - `./tmpcluster processed-vectors.txt`
 
## Mapping

todo (I forgot what these files do but they are here for historical
reasons ¯\\\_(ツ)\_/¯)

## Importing the data

Once all the above steps are all done, you may wish to import the 
clustered image data into a database. For my own reasons, I'm using a 
Postgres database, so my script will only work for this type of 
database.

Before importing, you must set four environment variables:

```
export LIFELOG_DB_USER="username"
export LIFELOG_DB_PASS="secret"
export LIFELOG_DB_HOST="your.database.url"
export LIFELOG_DB_NAME="databasename"
```
 
To kick off this process, run:

 - `./import.sh path/to/cluster/folder output.json`
 
This will run two python scripts that will firstly convert the directory
that contains the clusters into a JSON blob, and secondly import that
blob into a database.

If you would like to _only_ create the JSON blob, you may run:

 - `python import/cluster_to_json.py path/to/cluster/folder output.json`
 
# License

Copyright © 2016 Harry Scells