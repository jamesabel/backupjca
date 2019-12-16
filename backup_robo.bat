REM usage:
REM backup_robo.bat source dest name
REM
REM example:
REM c:\Users\joe\Documents is the folder we want to back up
REM l: is our backup drive (e.g. an external USB drive - we make a backup folder to distinguish it from regular files)
REM Documents is our name for this session (used for naming log files)
REM backup_robo.bat c:\Users\joe\Documents l:\backup\joe\Documents Documents
REM
REM you should create a .bat file that calls this .bat like:
REM call backup_robo.bat c:\Users\joe\Documents l:\backup\joe\Documents Documents
REM call backup_robo.bat c:\Users\joe\Favorites l:\backup\joe\Favorites Favorites
REM call backup_robo.bat c:\Users\joe\Desktop   l:\backup\joe\Desktop   Desktop
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
REM use /MIR for true backups, however we're using /e for now since we want to keep everything (even what's been deleted from the source)
robocopy %1 %2 *.* /e /DCOPY:T /COPYALL /R:2 /W:1 /B /LOG:%2\..\%3_log.log /TS /NP /TEE /XD $RECYCLE.BIN "System Volume Information" 
