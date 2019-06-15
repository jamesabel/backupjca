del /S /Q venv
"C:\Program Files\Python37\python.exe" -m venv --clear venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip3 install -U setuptools
venv\Scripts\pip3 install -U -r requirements.txt
REM
REM the pypi pyinstaller didn't work so use the latest from its repo
pushd .
cd ..\pyinstaller
..\backupjca\venv\Scripts\python.exe setup.py install
popd
