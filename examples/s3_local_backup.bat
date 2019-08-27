pushd .
cd ..
call venv\Scripts\activate.bat
python -m backupjca temp\s3 -s
deactivate
popd
