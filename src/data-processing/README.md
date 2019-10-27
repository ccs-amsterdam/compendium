This folder should contain the code that does the data processing before actual analysis.

More formally: after running all code in this folder, 
all files in data/intermediate that scripts in `src/analysis` depend on should be created. 

Generally, data processing code will depend either on files in `data/raw` or `data/raw-private`, 
or on other files in `data/intermediate` or `data/tmp` created by other data processing code.
