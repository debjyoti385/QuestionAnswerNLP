## QUESTION ANSWER NLP PROJECT
#### Author/ Contributor: Debjyoti Paul, deb@cs.utah.edu, uNID: u0992708
###NOTE: In CADE machines use following python path: /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python
`PLEASE RUN FIRST
$ chmod +x prepare.sh
$ ./prepare.sh`

- PREPARE MODULE
    - Modules require:
        - numpy
        - scipy
        - scikit-learn
    - to install them locally and run use following command
    - $ sh prepare.sh

- EXECUTION
    -  Help 
		- /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -h
	- Execution WITHOUT Coreference Resolution 
		- /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o response.txt -c 0
    - Execution WITH Coreference Resolution
		- /usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o response.txt -c 1
- INFORMATION
	- It usually takes some 30 seconds to initialize Question classifier.
    - In this project we are using bart server and that runs on port 8125.	
