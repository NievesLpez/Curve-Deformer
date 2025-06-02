#Import from same folder
from . import main
from . import ui

def launch(): #Verifica si hay ventanas existentes y las cierra, abre una nueva
    try:
        ui.ui.close()
    except:
        pass
    
    ui.ui = ui.BaseWindow()
    ui.ui.show()



"""
Uso en maya
--------------------
import curveDeformer
curveDeformer.launch()
"""