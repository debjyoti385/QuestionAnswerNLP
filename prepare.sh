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
echo "## INSTALL scikit-learn IN pwd"
/usr/local/stow/python/amd64_linux26/python-2.7.3/bin/pip install -t . scikit-learn 
echo "## INSTALL COMPLETE "
echo "## DONE!! "
echo "###################################################################################################"
echo "Example to Run program : "
echo "NOTE: DEFAULT OUTPUT will also be printed in \"myresponse.txt\""
echo "And it takes around 1 HOUR to run on developset data "
echo "Please use "screen" command and run "
echo "###################################################################################################"
echo "COMMAND: "
echo "/usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o myresponse.txt"
echo "###################################################################################################"


