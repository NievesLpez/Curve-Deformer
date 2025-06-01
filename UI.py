import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QDialog, QLabel, QPushButton, QSlider, QVBoxLayout, QHBoxLayout, QColorDialog, QCheckBox
import main 


#Clase para implementar el color dialog
class CustomColorButton(QtWidgets.QPushButton):
    colorChanged = QtCore.Signal(tuple)

    #Ajustar nombre, tamaño, y permitir selección del color
    def __init__(self, label="Pick control color", parent=None):
        super(CustomColorButton, self).__init__(label, parent)
        self.clicked.connect(self.choose_color) #Conectar en click
        self.color = QtGui.QColor(100, 100, 255) #Color predeterminado
        self.update_color()

    def choose_color(self): #Abre el dialog y almacena el color que se elija
        color = QtWidgets.QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self.update_color()

            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
            self.colorChanged.emit((r, g, b))

    def update_color(self): #Hace que el color del hover sea el que se ha elegido, queda más elegante que todo el botón del color elegido siempre.
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #4a4a4a;  
                color: white;
            }}
            QPushButton:hover {{
                background-color: {self.color.name()};  
            }}
        """)



class SliderWithLabel(QtWidgets.QWidget): #Funcion slider que actualiza su valor con valueChanged, compound widget de label y slider

    valueChanged = QtCore.Signal(int)

    def __init__(self, text="Slider", parent=None):
        super(SliderWithLabel, self).__init__(parent)

        self.label = QtWidgets.QLabel(text)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 3)
        self.slider.setValue(1)

        layout = QtWidgets.QHBoxLayout(self) #Crea su propio layout para que la etiqueta y el slider queden bien alineados
        layout.addWidget(self.label)
        layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self.valueChanged.emit)




class BaseWindow(QtWidgets.QDialog):

    def __init__(self): #Crea la ventana principal

        super(BaseWindow, self).__init__()

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowTitle("Curve Deformer")
        self.setFixedSize (400, 200)
        #Style sheet general que se aplica a toda la UI, también especifico el botón create button con un nombre para que sea azul en vez dxe gris
        self.setStyleSheet(""" 
            QDialog {
                background-color: #2e2e2e;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton#createButton {
            background-color: #4682B4;
            }
            QPushButton#createButton:hover {
            background-color: #5A9BD5;
            }
            QLabel {
                color: white;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #777;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #5c5c5c;
                width: 14px;
                margin: -5px 0;
            }
            
        """)

        self.populate() #Crea la ventana 



    def populate(self): #Crea todos los widgets que quiero añadir con sus tooltips individuales

        #Buttons
        self.convert_button = QtWidgets.QPushButton("Convert")
        self.convert_button.setToolTip("Select geometry edge loop to create NURB")

        self.bind_button = QtWidgets.QPushButton("Bind")
        self.bind_button.setToolTip("Select mesh first and NURB to bind them")

        #Influence slider
        self.influence_slider = SliderWithLabel("Influence") #Llamo funcion que cree antes con el widget
        self.influence_slider.setToolTip("Adjust deformer influence")

        #Color checkbox
        self.color_button = CustomColorButton() #Llamo funcion que cree antes con el widget
        self.color_button.setToolTip("Select a color for the controllers")
        
        #Create button
        self.create_button = QtWidgets.QPushButton("Create")
        self.create_button.setToolTip("Create controllers for the deformer")
        self.create_button.setObjectName("createButton")

        """Layout"""

        main_layout = QtWidgets.QVBoxLayout(self) #Layout principal
        
        top_layout = QtWidgets.QHBoxLayout() #Layout para separar los botones de la partye superior

        top_layout.addWidget(self.convert_button)
        top_layout.addWidget(self.bind_button)

        main_layout.addLayout(top_layout) #Lo añado al principal

        main_layout.addWidget(self.influence_slider) 
        main_layout.addWidget(self.color_button) #El resto de elementos van directamente en el principal para que vayan centrados
        main_layout.addWidget(self.create_button)

        self.create_connections() #Llamo funcion para conectar botones con funciones

    #Conectar botones con funciones cuando haces click
    def create_connections(self):
        self.convert_button.clicked.connect(self.on_convert_clicked)
        self.bind_button.clicked.connect(self.on_bind_clicked)
        self.color_button.colorChanged.connect(self.on_color_changed)
        self.influence_slider.valueChanged.connect(self.on_influence_changed)
        self.create_button.clicked.connect(self.on_create_clicked)


    def on_convert_clicked(self):
        
        try:
            result = main.convertCurve()

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")


if __name__ == "Curve Deformer": #Creacion de la ventana, cierra la anterior para evitar duplicados
       
    try:
        ui.close()

    except:
        pass
#Soy consciente de que esto debe estar indentado, pero si lo indento maya deja de ejecutarlo...
ui= BaseWindow()
ui.show()

