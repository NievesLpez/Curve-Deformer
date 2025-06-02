import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QDialog, QLabel, QPushButton, QSlider, QVBoxLayout, QHBoxLayout, QColorDialog, QCheckBox
from . import main


#Clase para implementar el color dialog
class CustomColorButton(QtWidgets.QPushButton):
    colorChanged = QtCore.Signal(tuple)

    def __init__(self, label="Pick control color", parent=None):
        super(CustomColorButton, self).__init__(label, parent)

        self.clicked.connect(self.choose_color) #Conexion
        self.color = QtGui.QColor(100, 100, 255)  #Default
        self.update_color()

    def choose_color(self): #
        color = QtWidgets.QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self.update_color()

            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
            self.colorChanged.emit((r, g, b)) #Conversion de valores de color para adapptar los de Qt con maya nativo rgb (ratio 255 a 1)

    def update_color(self): #Hace que el color del hover sea el que se ha elegido
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #4a4a4a;  
                color: white;
            }}
            QPushButton:hover {{
                background-color: {self.color.name()};  
            }}
        """)



class SliderWithLabel(QtWidgets.QWidget): #Funcion slider que modifica el falloff del wire deformer

    valueChanged = QtCore.Signal(int)

    def __init__(self, text="Slider", parent=None):
        super(SliderWithLabel, self).__init__(parent)

        self.label = QtWidgets.QLabel(text)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 10)
        self.slider.setValue(3)

        layout = QtWidgets.QHBoxLayout(self) #Layout
        layout.addWidget(self.label)
        layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self.valueChanged.emit) #Emite senal para actualizar slider




class BaseWindow(QtWidgets.QDialog): #Ventana principal

    def __init__(self): 

        super(BaseWindow, self).__init__()

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Curve Deformer")
        self.setFixedSize (400, 200)

        #Style sheet general 
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

        self.populate() #Crea widgets



    def populate(self): #Crea todos los widgets 

        #Buttons
        self.convert_button = QtWidgets.QPushButton("Convert")
        self.convert_button.setToolTip("Select geometry edge loop to create NURB")

        self.bind_button = QtWidgets.QPushButton("Bind")
        self.bind_button.setToolTip("Select mesh first and NURB to bind them")

        #Influence slider
        self.influence_slider = SliderWithLabel("Influence") 
        self.influence_slider.setToolTip("Adjust deformer influence")

        #Color checkbox
        self.color_button = CustomColorButton()
        self.color_button.setToolTip("Select a color for the controllers")
        
        #Create button
        self.create_button = QtWidgets.QPushButton("Create")
        self.create_button.setToolTip("Create controllers for the deformer")
        self.create_button.setObjectName("createButton")

        """Layout"""

        main_layout = QtWidgets.QVBoxLayout(self) #Layout principal
        
        top_layout = QtWidgets.QHBoxLayout() #Layout para separar los botones

        top_layout.addWidget(self.convert_button)
        top_layout.addWidget(self.bind_button)

        main_layout.addLayout(top_layout) 

        main_layout.addWidget(self.influence_slider) 
        main_layout.addWidget(self.color_button) 
        main_layout.addWidget(self.create_button)

        self.create_connections() 


    #Conectar acciones
    def create_connections(self):
        self.convert_button.clicked.connect(self.on_convert_clicked)
        self.bind_button.clicked.connect(self.on_bind_clicked)
        self.color_button.colorChanged.connect(self.on_color_changed)
        self.influence_slider.valueChanged.connect(self.on_influence_changed)
        self.create_button.clicked.connect(self.on_create_clicked)

    #Funciones separadas que llaman al main


    def on_convert_clicked(self):
        try:
            result = main.convertCurve()
        except Exception as e:
            pass


    def on_bind_clicked(self):
        try:
            result = main.bindCurve()
        except Exception as e:
            pass


    def on_color_changed(self, rgb_color):
        main.setControlColor(rgb_color)

    def on_influence_changed(self, value):
        main.influenceWeight(value)


    def on_create_clicked(self):
        try:
            main.createDeformer()
        except Exception as e:
            pass

#Var global (creo laui desde innit)
ui = None