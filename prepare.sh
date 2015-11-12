echo "## FETCH QUESTION CLASSIFIER TRAINING DATA ##"
cp -r /home/debjyotp/important/qcdata .
echo "## FETCH COMPLETE ##"
echo "## FETCH developset DATA ##"
cp -r /home/debjyotp/important/developset .
echo "## INSTALL scikit-learn IN pwd"
/usr/local/stow/python/amd64_linux26/python-2.7.3/bin/pip install -t . scikit-learn 
echo "## INSTALL COMPLETE "
echo "## DONE!! "
echo "Example to Run program : Note: by default output will also be printed in \"myresponse.txt\" \n And it takes around 1 hour to run on developset data \COMMAND: "
echo "/usr/local/stow/python/amd64_linux26/python-2.7.3/bin/python qa.py -i input.txt -o myresponse.txt"


