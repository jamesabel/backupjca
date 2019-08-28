pushd .
cd ..
call venv\Scripts\activate.bat
python -m backupjca temp\github -g
deactivate
popd
