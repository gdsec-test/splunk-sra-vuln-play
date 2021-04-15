#!/bin/bash
echo "removing old files"
rm -rf splunk_sra_vuln_play

echo "copying"
rsync -r src/ splunk_sra_vuln_play

echo "removing bad files"
find ./splunk_sra_vuln_play -type d -name __pycache__\* -exec rm  -rf {} \; 2>/dev/null
find ./splunk_sra_vuln_play -type d -name .\* -exec rm  -rf {} \; 2>/dev/null
rm -rf ./splunk_sra_vuln_play/**/.env
rm -rf ./splunk_sra_vuln_play/bin/.venv
rm -rf ./splunk_sra_vuln_play/bin/.coverage
rm -rf ./splunk_sra_vuln_play/bin/.coveragerc
rm -rf ./splunk_sra_vuln_play/bin/Makefile
rm -rf ./splunk_sra_vuln_play/bin/requirements.txt
rm -rf ./splunk_sra_vuln_play/bin/test*

echo "fix permissions"
sudo chmod -R 644 ./splunk_sra_vuln_play && sudo find ./splunk_sra_vuln_play -type d -exec chmod 755 {} +

echo "tarring"
tar c ./splunk_sra_vuln_play > ./splunk_sra_vuln_play.tar
echo "zipping"
gzip ./splunk_sra_vuln_play.tar
echo "renaming"
mv ./splunk_sra_vuln_play.tar.gz ./splunk_sra_vuln_play.spl

# echo "removing old files"
rm -rf splunk_sra_vuln_play
