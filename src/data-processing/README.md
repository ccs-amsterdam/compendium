This folder should contain the scripts (or other code) that does the data processing before actual analysis.

More formally: after running all code in this folder, 
all files in `data/intermediate` or `data/tmp` that scripts in `src/analysis` depend on should be created. 

Generally, data processing scripts will depend either on files in `data/raw` or `data/raw-private`, 
on external sources, or on other files in `data/intermediate` or `data/tmp` created by other data processing scripts.

When setting up your compendium, replace this readme file with a description of the different processing scripts. 

Note that if processing scripts start with the a header such as the following, 
the data processing and process documentation can be automated using `doit`:

```
#!/usr/bin/env python3
#DEPENDS: private/input.txt
#CREATES: intermediate/output.txt
#TITLE: Optional descriptive title
#PIPE: TRUE  # if process can be run as a pipeline, e.g. program < infile > outfile
```
