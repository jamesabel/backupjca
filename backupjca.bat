REM usage:
REM backupjca.bat source dest name
REM
REM example:
REM c:\Users\joe\Documents is the folder we want to back up
REM l: is our backup drive (e.g. an external USB drive - we make a backup folder to distinguish it from regular files)
REM Documents is our name for this session (used for naming log files)
REM backupjca.bat c:\Users\joe\Documents l:\backup\joe\Documents Documents
REM
REM you should create a .bat file that calls this .bat like:
REM call backupjca.bat c:\Users\joe\Documents l:\backup\joe\Documents Documents
REM call backupjca.bat c:\Users\joe\Favorites l:\backup\joe\Favorites Favorites
REM call backupjca.bat c:\Users\joe\Desktop   l:\backup\joe\Desktop   Desktop
REM etc
REM 
echo on
echo %1 %2 %3
mkdir %2
copy /Y c:\b\backupjca.bat %2_cmd.txt
echo "" >> %2_cmd.txt
echo %1 >> %2_cmd.txt
echo %2 >> %2_cmd.txt
echo %3 >> %2_cmd.txt
REM use /MIR for true backups, however we're using /e for now since we don't trust whats currently on the drive
robocopy %1 %2 *.* /e /DCOPY:T /COPYALL /R:2 /W:1 /B /LOG:%2\..\%3_log.log /TS /NP /TEE /XD $RECYCLE.BIN "System Volume Information" 

