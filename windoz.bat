@echo off
echo %DATE% %TIME%
goto BUILD
echo.
echo Notes about how to run pyRig on Windoze 10
echo.
echo Already should have matplotlib, basemap installed from demos.
echo.
echo To run script directly:
echo.
        pyRig.py -rig DIRECT
:BUILD       
echo.
echo Compile with - works on both windoz and linux:
echo.
        pyinstaller --onefile pyRig.py
echo.
echo To run compiled binary - works on both windows and linux:
echo.
        dist\pyRig.exe -rig DIRECT
echo.
echo     Run Inno Setup Compiler end follow the prompts to create an installer
echo     This installer works on Windoz 10 end Bottles!
echo.
echo %DATE% %TIME%
echo.
