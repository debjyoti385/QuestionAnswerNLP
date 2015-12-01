## QUESTION ANSWER NLP PROJECT
#### Author/ Contributor: Debjyoti Paul, deb@cs.utah.edu, uNID: u0992708
###NOTE: In CADE machines use following python path: /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python
`PLEASE RUN FIRST
$ chmod +x prepare.sh
$ ./prepare.sh
`

- PREPARE MODULE
    - Modules require:
        - numpy
        - scipy
        - scikit-learn
        - beautifulSoup4
        - requests
    - to install them locally and run use following command
    - $ ./prepare.sh
    
- EXECUTION
    -  Help 
		- /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -h
	- Execution WITHOUT Coreference Resolution 
		- /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o response.txt -c 0
    - Execution WITH Coreference Resolution
		- /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o response.txt -c 1
    - NOTE: 
        - The final F-score obtained for developset is 32.68% (without coref resolution)
        - The final F-score obtained for testset1 is 38.64% (without coref resolution)
    
- INFORMATION
	- It usually takes some 30 seconds to initialize Question classifier.
    - This script also installs BART anaphora resolution kit and runs a web server with port 8125
    - TESTED on lab1-13.eng.utah.edu 
    - In OSX/ Macbook developset execution completes in 12-15 minutes while in CADE machine it takes more than an hour. 
      This is very weird and I presume it may be due to NFS disk access for NLTK_data.
