import maya.cmds as cmds
import math

# Variables globales para almacenar info general reutilizable
stored_curve = None
stored_mesh = None
control_color = (0.2, 0.5, 1.0) 
stored_deformer = None


"""
Convierte el edge loop que seleccionas directamente en una nurbs
"""

def convertCurve(): 
    global stored_curve, stored_mesh, stored_deformer #Utiliza las variables globales para no crear nuevas
    
    stored_deformer = None #Limpia def para reutilizar herramienta
    
    selection = cmds.ls(selection=True, flatten=True)

    if not selection:
        cmds.warning("Selection is not valid, select edge loop to proceed")
        return None, None 
    
    # Verifica que lo seleccionado son ejes con codigo 32 (ejes)
    edges = cmds.filterExpand(selection, selectionMask=32, expand=True)

    if not edges:
        cmds.warning("Selection is not valid, select edge loop to proceed")
        return None, None 

    # Convertir en NURBS
    if edges:
        mesh = edges[0].split('.')[0] #Uso la primera parte del nombre de edges sin el _ para crear nombre diferente
        
        try:
            # Crear nombre curva, suma 1 si el anterior ya existe
            counter = 1
            while True:
                curve_name = f"{mesh}_CRV_{counter}"
                if not cmds.objExists(curve_name):
                    break
                counter += 1

            curve = cmds.polyToCurve(form=2, degree=3, name=curve_name) #Crea NURBS y asigna nombre
            curve = curve[0] #Asigna var al primer elemento de la lista

            cmds.delete(curve, constructionHistory=True) #Del history  para evitar cycles

            # Configurar apariencia de la curva
            cmds.setAttr(f"{curve}.lineWidth", 5)
            cmds.setAttr(f"{curve}.overrideEnabled", 1)
            cmds.setAttr(f"{curve}.overrideColor", 13)

            # Almacenar var globales
            stored_curve = curve
            stored_mesh = mesh

            return mesh, curve
            
        except Exception as e:
            cmds.warning(f"Could not create curve")
            return None, None

    else:
        cmds.warning("Error when converting to NURB")

    return None, None 


def createControls(curve_name):
    if not cmds.objExists(curve_name): #Verifica que la la curva exista
        cmds.warning("Curve does not exist")
        return []
    
    curve_shapes = cmds.listRelatives(curve_name, shapes=True) #Busca el nodo de shape de la curva
    if not curve_shapes:
        cmds.warning("Curve does not exist")
        return []
    
    curveToControl = curve_shapes[0]

    spans = cmds.getAttr(f"{curveToControl}.spans")
    degree = cmds.getAttr(f"{curveToControl}.degree")
        
    # Calcula numero de cvs basandose en spans y tipo de curva
    cvs = spans + degree

    controls = []

    for i in range(cvs):

        # Recoge posicion en el mundo de cada cv de la curva
        ctlPOS = cmds.pointPosition(f"{curve_name}.cv[{i}]", world=True)
        
        # Crear nombre  para cada control (suma 1)
        counter = 1
        while True:
            sphere_name = f"{curve_name}_CTL_{i}_{counter}"
            if not cmds.objExists(sphere_name):
                break
            counter += 1
            
        sphere = cmds.polySphere(name=sphere_name, radius=0.1, subdivisionsX=8, subdivisionsY=6)[0] #Crea esferas como controles
        
        # Colocar esferas en cada cv position (coordenadas xyz trans)
        cmds.move(ctlPOS[0], ctlPOS[1], ctlPOS[2], sphere, absolute=True)
        
        # Apariencia del control
        cmds.setAttr(f"{sphere}.overrideEnabled", 1)
        cmds.setAttr(f"{sphere}.overrideRGBColors", 1)
        cmds.setAttr(f"{sphere}.overrideColorRGB", *control_color) #Utilizo la var que saco del picker de la ui
        
        # shading transparente
        cmds.setAttr(f"{sphere}.overrideShading", 0)
        
        controls.append(sphere) #Uno controles a mi lista creada antes
        
    return controls


"""
Bindea NURBS a la mesh con deformadores
"""

def bindCurve():
    global stored_curve, stored_mesh, stored_deformer
    
    selection = cmds.ls(selection=True, flatten=True)
        
    if len(selection) < 2:
        cmds.warning("Select a mesh first and then a NURBS curve") #Necesita dos selecciones para funcionar correctamente
        return 

    mesh = selection[0]
    curve = selection[1]
    
    # Verificar que los objetos existen y son del tipo correcto
    if not cmds.objExists(mesh):
        cmds.warning("Mesh does not exist")
        return
        
    if not cmds.objExists(curve):
        cmds.warning("Curve does not exist")
        return
    
    # Verificar que el primer objeto es una mesh
    mesh_shapes = cmds.listRelatives(mesh, shapes=True) or []
    if not any(cmds.nodeType(shape) == 'mesh' for shape in mesh_shapes):
        cmds.warning(f"{mesh} is not a mesh")
        return
    
    # Verificar que el segundo objeto es una curva
    curve_shapes = cmds.listRelatives(curve, shapes=True) or []
    if not any(cmds.nodeType(shape) == 'nurbsCurve' for shape in curve_shapes):
        cmds.warning(f"{curve} is not a NURBS curve")
        return

    try:
        print(f"{mesh}, {curve} selected")
        
        # Crear nombre para el deformador
        counter = 1
        while True:
            deformer_name = f"{curve}_DEF_{counter}"
            if not cmds.objExists(deformer_name):
                break
            counter += 1
        
        # Crear wire deformer
        wire_result = cmds.wire(mesh, wire=curve, name=deformer_name)
        deformer = wire_result[0]  
        
        print("Wire deformer created")
        

        # Almacenar var
        stored_mesh = mesh
        stored_curve = curve
        stored_deformer = deformer

        return deformer
        
    except Exception as e:
        cmds.warning(f"Deformer could not be created")
        return None

"""
Modifica el valor del dropoff con el slider
"""
def influenceWeight(value):
    global stored_deformer
    if stored_deformer and cmds.objExists(stored_deformer):
            cmds.setAttr(f"{stored_deformer}.dropoffDistance[0]", value)
    else:
        cmds.warning("No active deformer found")

"""
 Colorear controladores
 """
def setControlColor(rgb_color):
    global control_color
    control_color = rgb_color


"""
Conecta los controles a los CVs de la curva usando clusters
"""
def connectControlsToCurve(controls, curve):
    for i, control in enumerate(controls):
        # Crear nombre para el cluster (+1)
        counter = 1
        while True:
            cluster_name = f"{curve}_CV{i}_CLS_{counter}"
            if not cmds.objExists(cluster_name):
                break
            counter += 1
        
        # Crea un cluster en cada cv
        cluster = cmds.cluster(f"{curve}.cv[{i}]", name=cluster_name)[1]
        
        # Constraint del ctl al cluster
        cmds.pointConstraint(control, cluster, maintainOffset=False)
        
        # Visibilidad
        cmds.setAttr(f"{cluster}.visibility", 0)
        
        # Parent cluster al grupo RIG
        if cmds.objExists("RIG_GRP"):
            cmds.parent(cluster, "RIG_GRP")


"""
Al inicializar la tool crea los grupos base para mantener organizado el rig
"""
def createBaseGroups():
    rootName = "character"

    # Solo crea grupos si no existen
    if not cmds.objExists("GEO_GRP"):
        cmds.group(em=True, name="GEO_GRP")
    if not cmds.objExists("CTRL_GRP"):
        cmds.group(em=True, name="CTRL_GRP")
    if not cmds.objExists("SKEL_GRP"):
        cmds.group(em=True, name="SKEL_GRP")
    if not cmds.objExists("RIG_GRP"):
        cmds.group(em=True, name="RIG_GRP")

    # Parent skel under rig 
    try:
        if cmds.listRelatives("SKEL_GRP", parent=True) != ["RIG_GRP"]:
            cmds.parent("SKEL_GRP", "RIG_GRP")
    except:
        pass

    # Parent resto de grupos bajo el main
    if not cmds.objExists(rootName):
        try:
            cmds.group("GEO_GRP", "CTRL_GRP", "RIG_GRP", name=rootName)
        except:
            pass

    # Color para organizacion
    try:
        cmds.setAttr("GEO_GRP.useOutlinerColor", 1)
        cmds.setAttr("GEO_GRP.outlinerColor", 0, 1, 0)

        cmds.setAttr("CTRL_GRP.useOutlinerColor", 1)
        cmds.setAttr("CTRL_GRP.outlinerColor", 1, 1, 0)

        cmds.setAttr("RIG_GRP.useOutlinerColor", 1)
        cmds.setAttr("RIG_GRP.outlinerColor", 0.74, 0, 0.75)
    except:
        pass


"""
Funcion que ejecuta el sistema final
"""                
def createDeformer():
    createBaseGroups()

    if not stored_curve:
        cmds.warning("No curve available")
        return
    
    # Crear controles para la curva
    if stored_curve and cmds.objExists(stored_curve):
        controls = createControls(stored_curve)
    
        # Organizar en grupos
        if cmds.objExists("CTRL_GRP"):
            for ctrl in controls:
                try:
                    if not cmds.listRelatives(ctrl, parent=True) or cmds.listRelatives(ctrl, parent=True)[0] != "CTRL_GRP":
                        cmds.parent(ctrl, "CTRL_GRP")
                except:
                    pass

        if cmds.objExists("RIG_GRP") and stored_curve:
            try:
                if not cmds.listRelatives(stored_curve, parent=True) or cmds.listRelatives(stored_curve, parent=True)[0] != "RIG_GRP":
                    cmds.parent(stored_curve, "RIG_GRP")
            except:
                pass    
                
        # Crear constraints entre controles y cvs de la curva
        connectControlsToCurve(controls, stored_curve)
        
    else:
        cmds.warning("No valid curve found")