echo "## FETCH QUESTION CLASSIFIER TRAINING DATA ##"
cp -r /home/debjyotp/important/qcdata .
echo "## FETCH COMPLETE ##"
echo "## FETCH developset DATA ##"
cp -r /home/debjyotp/important/developset .
echo "## PREPARING input.txt  ##"
cd developset
pwd > ../input.txt
ls   | grep story | sed 's/.story//' >> ../input.txt
cd ..
echo "## input.txt READY "
echo "###################################################################################################"
echo "## INSTALL scikit-learn IN pwd"
/usr/local/stow/python/amd64_linux26/python-2.7.3/bin/pip install -t . scikit-learn 
echo "## scikit-learn INSTALLATION COMPLETE"
echo "###################################################################################################"
echo "## INSTALL BART - a Beautiful Anaphora Resolution Toolkit IN pwd"
echo "FETCH BART snapshot from http://www.sfs.uni-tuebingen.de/~versley/BART/BART-snapshot.tgz "
echo "Normally takes 7 minutes though depends on network connection "
wget http://www.sfs.uni-tuebingen.de/~versley/BART/BART-snapshot.tgz
tar -xvf BART-snapshot.tgz
echo "Extraction complete"
cd BART/
/bin/bash
source setup.sh
echo "KILL any previously invoked process using 8125 port"
kill -9 `lsof -i :8125 | tail -1 | awk '{print $2}'`
echo "READY TO LAUNCH BART SERVER "
java -Xmx1024m elkfed.webdemo.BARTServer & > /dev/null 2>&1
exit
echo "## BART SERVER LAUNCHED "
echo "###################################################################################################"
echo "## ALL INSTALLATION COMPLETE "
echo "## DONE!! "
echo "###################################################################################################"
echo "Example to Run program : "
echo "NOTE: DEFAULT OUTPUT will also be printed in \"myresponse.txt\""
echo "And it takes around 1 HOUR to run on developset data "
echo "Please use "screen" command and run "
echo "###################################################################################################"
echo "COMMAND: "
echo "Run WITHOUT Coreference Resolution "
echo "/usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o myresponse.txt -c 0"
echo "Run WITH Coreference Resolution "
echo "/usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o myresponse.txt -c 1"
echo "###################################################################################################"
echo "For further queries please contact me: "
echo "Email: deb@cs.utah.edu"
echo "Phone: 385-313-7219"
echo "###################################################################################################"


