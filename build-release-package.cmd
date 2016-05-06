set app_title=Turrican II Editor
set app_description=A level editor for Turrican II CDTV.

set app_name=Turrican II Editor
set app_name_lower=turrican2editor

set app_version=1.0.0
set app_version_value=1.0.0
set app_version_title=1.0.0

set build_path=".\build\exe.win32-2.7"

set python_interpreter="c:\python27\python.exe"
set setup_compiler="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
set zip=7za


rmdir .\build /S /Q
%python_interpreter% setup.py build

del %app_name_lower%-setup-*.exe
%setup_compiler% %app_name_lower%.iss

del %app_name_lower%-*.7z
%zip% a %app_name_lower%-%app_version%.7z %build_path%\* -r -mx=9 -ms=on

pause
