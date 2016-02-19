import sys
if sys.platform == 'win32':
    from crea8s_nail.tzlocal.win32 import get_localzone, reload_localzone
elif 'darwin' in sys.platform:
    from crea8s_nail.tzlocal.darwin import get_localzone, reload_localzone
else:
    from crea8s_nail.tzlocal.unix import get_localzone, reload_localzone
    
