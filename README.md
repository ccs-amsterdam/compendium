# Research Compendium Template CCS Amsterdam

This repo contains a template for structuring projects used within the [Computational Communication Science Lab Amsterdam](http://ccs.amsterdam/). You can just clone or download this repo to get started.

## Introduction and Rationale
Computational research often involves a number of data sets, tools/scripts, analyses, and papers. It is beneficial to use a standardized default project structure so it is easier to read each other’s code, and because it stimulates setting up analysis projects in such a way as to make they easily publishable. 
This document describes a structure for repositories that contain data analyses, including all necessary preprocessing and data wrangling steps that link the raw data to the final outcome. They are sometimes called ‘compendiums’ because they function as an appendix for a published paper. 
See also https://github.com/benmarwick/rrtools and Marwick (2017).

For pure software or package repositories, strict guidelines are available, and computational social scientists developing such packages should follow the normal package structure for python (https://python-packaging.readthedocs.io/en/latest/minimal.html) / R (LINK), etc... This document, in contrast, gives guidance on structuring projects that are focused on data analysis and academic papers that rely on these data.  

## Goal
Our goal is to create a project structure that::
- I[a]s published on (e.g.) github;
- Contains (ideally) all data and code needed for a certain analysis and/or to create a cleaned/annotated data set;
- If relevant and possible, automatically checks whether files can be generated (e.g. Rmd files) and runs other tests;
- If relevant and possible, automatically builds a docker with all dependencies and data for version management.
Open questions
- Should we rename report to results and include end-product data as well? If so, can we rename the data folder to prevent confusion (e.g. src/code, src/data; data-src; data-raw)
- Can we make it so the source files are installable as (r, python) package (possibly even including the data). That would make it easier to handle requirements, pythonpath etc.


## Folder structure and files

All files/folders in bold are archived publicly. 

- **src**
   + **draft** - contains work-in-progress to be moved to other folders (or deleted)
   + **data-processing** - contains data cleaning / processing scripts that generate any intermediate or temporary data files needed by the analyses
   + **lib** - contains functions used by other scripts in src/data-processing or src/analysis
   + **analysis** - scripts or notebooks that contain the actual analyses; should produce the files in /report
- **data**
   + **raw** - contains raw ‘public’ data. Files should never be manually edited or cleaned. 
   + raw-private - contains raw data that cannot be shared for any reason (copyright, privacy, etc.). 
   + **raw-private-encrypted** - contains an encrypted version of the data in raw-private. 
   + **intermediate** - contains ‘public’ data derived from raw data or downloaded from an external source automatically. Any files here can be recreated using the scripts in src/data-processing provided any needed external sources and private data are available. Files are archived publicly. 
   + tmp - contains temporarily generated data to help speed up or simplify processing, but that does not need to be stored. All files in this folder can be recreated using the scripts in scripts/data that do not depend on external sources or private data. Files are not archived. 
   + *Files directly in data/ are seen as final / published data sets.*
- **report**
   + **figures** - optional folder for embedded figures
   + *Files directly in report/ are final / published reports*


Required top-level files:
- Readme.Rmd / md
- LICENSE


Optional/recommended top-level files:

- Makefile or other executable script to run data processing and analyses
- .travis or other CI-file
- Dockerfile or other Container install script
- Requirements.txt or R-equivalent


# Example repository

This repository contains a trivial example setup that showcases some of the features. You can run it with the following command:

```{sh}
doit passphrase=geheim
```

This will install python and the doit package (from [requirements.txt](requirements.txt) , decrypt the 'private' data and process it with the example scripts (that run upper/lowercase on it). 
