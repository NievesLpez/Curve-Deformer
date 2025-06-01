import maya.cmds as cmds
import math
    


"""
Convierte el edge loop que seleccionas en una nurbs
"""

def convertCurve(self): 
    
    selection = cmds.ls(selection=True, flatten=True) #seleccion

    if not selection:
        cmds.warning("Selection is not valid, select faces to proceed")
        return None, None 
    
    faces = cmds.filterExpand(selectionMask=34, expand = True) #filtra caras de la seleccion

    if not faces:
        cmds.warning("Selection is not valid, select faces to proceed")
        return None, None 

    # Filtrar la seleccion a solo caras cada dos (selecciona edges en los que el resto es 0 o 1)
    edgesToConvert = [face for i, face in enumerate(faces) if i % 4 in [0, 1]]

    #Convertir caras en edges 

    mainEdges = []

    for face in edgesToConvert:
        edges = cmds.polyListComponentConversion(face, fromFace=True, toEdge=True)
        edges = cmds.ls(edges, flatten=True)

        #Selecciono edges y obtengo edge loop
        cmds.select(edges)
        mainEdgeLoop = cmds.polySelect(edgeLoop=True)
        edgeLoopSelection = cmds.ls(selection=True, flatten=True)
        
        if edgeLoopSelection:
            mainEdges.extend(edgeLoopSelection)

    #Convertit en NURBS
    if mainEdges:
        mesh = mainEdges[0].split('.')[0] #Get name de la mesh con numeracion para que los nombres no se solapen
        cmds.select(mainEdges)  # Seleccionar TODOS los edges juntos
        curve = cmds.polyToCurve(form=2, degree=3, name=f"{mesh}_CRV")

        #Usa el primer elemento de la lista en caso de que la cree 
        if isinstance(curve, list):
            curve = curve[0]

        print("Curve created")

        cmds.setAttr(f"{curve}.lineWidth", 5)
        cmds.setAttr(f"{curve}.overrideEnabled", 1)
        cmds.setAttr(f"{curve}.overrideColor", 13)

        return mesh, curve

    else:
        cmds.warning("Cannot convert to NURB")

    return None, None 


def createControls (self, curve_name):


    if not cmds.objExists(curve_name):
        cmds.warning("Curve does not exist")
        return None, None
    
    curve_shapes = cmds.listRelatives(curve_name, shapes=True)
    if not curve_shapes:
        cmds.warning("Curve does not exist")
        return None, None
    

    curveToControl = curve_shapes[0]

    spans = cmds.getAttr(f"{curveToControl}.spans")
    degree = cmds.getAttr(f"{curveToControl}.degree")
        
    # El número de CVs es spans + degree
    cvs = spans + degree

    controls = []

    for i in range(cvs):

        # Obtener posición del CV
        ctlPOS = cmds.pointPosition(f"{curve_name}.cv[{i}]", world=True)
        
        # Crear esfera
        sphere_name = f"{curve_name[0].split('.')[0]}_CTL"
        sphere = cmds.polySphere(name=sphere_name, radius= 0.5, subdivisionsX=8, subdivisionsY=6)[0]
        
        # Posicionar esfera en el CV
        cmds.move(ctlPOS[0], ctlPOS[1], ctlPOS[2], sphere, absolute=True)
        
        # Configurar apariencia del control
        cmds.setAttr(f"{sphere}.overrideEnabled", 1)
        cmds.setAttr(f"{sphere}.overrideColor", 17)  # Amarillo
        
        # Opcional: Hacer la esfera un poco transparente
        cmds.setAttr(f"{sphere}.overrideShading", 0)
        
        controls.append(sphere)
        
     return controls




"""
Bindea esta estructura a la mesh con deformadores
"""

def bindCurve(self): #funcion que bindea la curva con la mesh, crea un wire deformer, funciona más o menos, por ahora también hace un print
    
    selection = cmds.ls(selection=True, flatten=True)
        
    if len(selection) < 2:
            cmds.warning("Select a mesh first and then a NURBS curve")
            return 

    mesh = selection[0]
    curve = selection[1]
    try:
        deformer = cmds.wire(mesh, curve, name=f"{curve}_DEF")[0] #crea el wire con la seleccion, da warning si no puede crearlo
        cmds.select(deformer)  

        print("Deformer was created")
    except:
        cmds.warning("Deformer could not be created")

    """funcion en proceso"""





def influenceWeight(self, value): #funcion para cambiar la dropoff distance a tiempo real del deformador, es decir, la "influencia" que tiene
    print(f"Influence changed to: {value}")
    

def colorControl(self): #funciona para manejar el color de los controladores que crea
    print(f"Your controls will have the color {self.color_button.color.name()}") #print del color elegido




    """
    Ejecuta la tool con los parametros establecidos
    """

def createDeformer(self): #crea los controles que manejan los vertex del wire

    """
    Al inicializar la tool crea los grupos base para ,antener organizado el rig
    """
    rootName = "character"

    cmds.group(em=True, name="GEO_GRP")
    cmds.group(em=True, name="CTRL_GRP")
    cmds.group(em=True, name="SKEL_GRP")
    cmds.group(em=True, name="RIG_GRP")

    # Parent skel under rig 

    cmds.parent("SKEL_GRP", "RIG_GRP")

    # Parent rresto de grupos bajo el main

    cmds.group("GEO_GRP", "CTRL_GRP", "RIG_GRP", name=rootName)

    # Color para organizacion

    cmds.setAttr("GEO_GRP.useOutlinerColor", 1)
    cmds.setAttr("GEO_GRP.outlinerColor", 0, 1, 0)

    cmds.setAttr("CTRL_GRP.useOutlinerColor", 1)
    cmds.setAttr("CTRL_GRP.outlinerColor", 1, 1, 0)

    cmds.setAttr("RIG_GRP.useOutlinerColor", 1)
    cmds.setAttr("RIG_GRP.outlinerColor", 0.74, 0, 0.75)