#Imports
from PySide import QtCore, QtGui, QtOpenGL
from PySide.QtGui import QMenu, QMessageBox
from PIL import Image
import numpy,math
from dds import *
from models_2k import Model2k
from StringIO import StringIO

#pyopengl checking
try:
    from OpenGL import *
    from OpenGL import GL, GLU
    
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL textures",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)

from OpenGL.constants import GLfloat
vec4 = GL.constants.GLfloat_4

#texture GL type dictionary
image_types={'DXT1':0x83F1,
             'DXT3':0x83F2,
             'DXT5':0x83F3,
             'ATI2':0x8DBD,
             70:0x83F1,
             71:0x83F1,
             72:0x83F1,
             76:0x83F2,
             77:0x83F2,
             78:0x83F2,
             82:0x83F3,
             83:0x8dbd,
             84:0x83F3,
             '\x00\x00\x00\x00':0,
             'q\x00\x00\x00':0,
             113:0,
             }

verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )
 
edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )
 
colors = (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (0,1,0),
    (1,1,1),
    (0,1,1),
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (1,0,0),
    (1,1,1),
    (0,1,1),
    ) 
 
surfaces = ((0,1,2,3),
            (3,2,7,6),
            (6,7,5,4),
            (4,5,1,0),
            (1,5,7,2),
            (4,0,3,6)) 
 
class GLWidget(QtOpenGL.QGLWidget):
    sharedObject = 0
    refCount = 0
    texture=None
    
    clicked = QtCore.Signal()

    def __init__(self, parent, shareWidget):
        QtOpenGL.QGLWidget.__init__(self, parent, shareWidget)
        self.clearColor = QtCore.Qt.black
        #self.clearColor = QtGui.QColor()
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        
        self.xMov = 0.0
        
        self.tex_width=512
        self.tex_height=512

        self.image=None
        self.win = self.window()
        self.lightPos=(0.0,0.0,-0.5)
        #self.initializeGL()
        
        
        #context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.ctx_menu)
        
        
    def changeObject(self):
        print('Changing Object')
        self.makeCurrent()
        self.sharedObject=self.cubeDraw()
        self.updateGL()
    
    def cubeDraw(self):
        print('drawingCube')
        #glRotatef(1.0, 3.0, 1.0, 1.0)
        #glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        dlist=glGenLists(1)
        self.qglColor(QtCore.Qt.red)
        glNewList(dlist,GL_COMPILE)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(verticies[vertex])
        glEnd()
        glEndList()
        return dlist
        
    
    
    
    def ctx_menu(self,position):
        menu=QMenu()
        menu.addAction(self.tr('Save Image'))
        menu.addAction(self.tr('Import Image'))
        res=menu.exec_(self.mapToGlobal(position))
        if not res:
            return
        
        if res.text()=='Save Image':
            print('Saving Image to DDS')
            location=QtGui.QFileDialog.getSaveFileName(caption="Save File",filter='*.dds')
            f=open(location[0],'wb')
            f.write(self.image.write_texture().read())
            f.close()
            #StatusBar notification
            self.window().statusBar.showMessage("Texture Saved to "+str(location[0]))
        
        elif res.text()=='Import Image':
            print('Importing Image')
            location=QtGui.QFileDialog.getOpenFileName(caption="Open Image File",filter='*.dds ;; *.jpg ;; *.png')
            
            #Loading New Image to Viewport
            im = Image.open(location[0], "r")
            self.tex_width, self.tex_height=im.size
            img_data = im.convert("RGBA").tostring("raw", "RGBA")
            
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
            glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
            
            glTexImage2D(GL_TEXTURE_2D,0,3,im.size[0],im.size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
            
            self.resizeGL(self.width(),self.height())
            self.update()
            
            
            #Add file to the scheduler
            
            #status=call(['./fifa_tools/nvidia_tools/nvdxt.exe','-file',location,comp,'-nmips',str(nmips),
            #             '-outdir','./fifa_tools','-quality_production','-output',tex[1].split(sep='\\')[-1].split(sep='.')[0]+'.dds'])
            
            self.win.scheduler_add(im,location[0])
            
        
        #msg=QMessageBox()
        #msg.setText('Done')
        #msg.exec_()
            
    
    def freeGLResources(self):
        GLWidget.refCount -= 1
        if GLWidget.refCount == 0:
            self.makeCurrent()
            glDeleteLists(self.__class__.sharedObject, 1)

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(200, 200)

    def setClearColor(self, color):
        self.clearColor = color
        self.updateGL()

    
    def initializeGL(self,*args):
        if not GLWidget.sharedObject:
            GLWidget.sharedObject = self.makeObject()
        GLWidget.refCount += 1
        
        
        glEnable(GL_DEPTH_TEST)
        glEnable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        try:
            self.texture_setup(args[0])
        except IndexError:
            pass
        
        glTranslatef(0.0,0.0, -5)
        #glEnable(GL_CULL_FACE)
        #glEnable(GL_TEXTURE_2D)

    def paintGL(self):
        self.qglClearColor(self.clearColor)
        self.qglColor(QtCore.Qt.white)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        #glMatrixMode(GL_MODELVIEW)
        glCallList(GLWidget.sharedObject)
        
        
        

    def resizeGL(self, width, height):
        side = min(width, height)
        glViewport((width - side) / 2, (height - side) / 2, side, side)
        #####ORIGINAL
        #tex_side=self.tex_width / self.tex_height
        
        #f_height=width/tex_side
        #if height>=f_height:
        #    f_width=width
        #else:
        #    f_height=height
        #    f_width=f_height*tex_side
        ######
        
        
        
        #print('Viewport Size: ',width,height, 'Sides: ' ,side,tex_side, 'Texture Sizes: ',self.tex_width,self.tex_height)
        #glViewport((width-f_width) /2, (height-f_height) /2, f_width, f_height) 
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        glMatrixMode(GL_MODELVIEW)
        #glOrtho(-0.1, +0.1, +0.5, -0.5, 4.0, 15.0)
        #lMatrixMode(GL_MODELVIEW)

    
    def makeObjectOriginal(self):
        dlist=glGenLists(1)
        glNewList(dlist,GL_COMPILE)
        
        glBegin(GL_QUADS)
        glTexCoord2f(1, 0);
        glVertex2f(1, 1);

        glTexCoord2f(0, 0);
        glVertex2f(-1, 1);

        glTexCoord2f(0, 1);
        glVertex2f(-1, -1);

        glTexCoord2f(1, 1);
        glVertex2f(1, -1);
        glEnd()
        glEndList()
        return dlist
    
    
    
    
    def texture_setup(self,image_data):
        self.image=image_data
        if not self.image:
            return
        typ=''.join(self.image.header.ddspf.dwFourCC)
        if typ=='DX10':
            typ=image_types[self.image.header.dwdx10header.dxgi_format]
        else:
            typ=image_types[typ]
        
        height=self.image.header.dwHeight
        width=self.image.header.dwWidth
        
        self.tex_width=width
        self.tex_height=height
        
        self.image.data.seek(0)
        
        #f=open('gl_data','wb')
        #f.write(self.image.data.read())
        #f.close()
        
        #set class texture size
        
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        
        
        if not typ: #normal uncompressed Texture
            buf_size=self.image.header.dwPitchOrLinearSize * height
            
            if self.image.header.ddspf.dwImageMode=='BGRA':
                typ=GL_BGRA
            else:
                typ=GL_RGBA
            
            glTexImage2D(GL_TEXTURE_2D,0,3,width,height,0,typ,GL_UNSIGNED_BYTE,image_data.data.read(buf_size))
        else:
            buf_size=self.image.header.dwPitchOrLinearSize
            self.image.unswizzle_2k()
            glCompressedTexImage2D(GL_TEXTURE_2D,0,typ,width,height,0,buf_size,self.image.data.read(buf_size))
        
        print(hex(typ),height,width,hex(buf_size))
        self.resizeGL(self.width(),self.height())
        self.update()
        
        
class GLWidgetQ(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.scale = 0.1
        self.xMov = 0.0
        self.yMov = 0.0
        self.lightPos=[0.,0.,2.5,1.0]
        self.sizeDiv=1.0
        self.lastPos = QtCore.QPoint()
        self.info = False

        #Model Data
        self.verts= []
        self.faces =[]

        self.trolltechGreen = QtGui.QColor.fromCmykF(0.0, 0.0, 0.0, 0.2)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.0, 0.0, 0.0, 0.7)
        
        #Image Props
        self.tex_width=512
        self.tex_height=512

        #Model Props
        self.vc=0
        self.fc=0
        
        self.image=None
        
        #Parent Window
        self.win = self.window()
        
        #Context Menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.ctx_menu)

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def setXMov(self,step):
        self.xMov+= step / 500.0
        self.updateGL()

    def setYMov(self,step):
        self.yMov+= step / 500.0
        self.updateGL()


    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.emit(QtCore.SIGNAL("xRotationChanged(int)"), angle)
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.emit(QtCore.SIGNAL("yRotationChanged(int)"), angle)
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.emit(QtCore.SIGNAL("zRotationChanged(int)"), angle)
            self.updateGL()

    def initializeGL(self):
        #setup model
        verts,norms,faces=self.loadOBJ('blogtext.obj')
        lightPos=[0.,0.,2.5,1.0]
        self.object = self.customModel(faces,verts,norms,lightPos)

        #lights
        pos = vec4(5.0, 5.0, 10.0, 0.0)
        red = vec4(0.8, 0.1, 0.0, 1.0)
        green = vec4(0.0, 0.8, 0.2, 1.0)
        blue = vec4(0.2, 0.2, 1.0, 1.0)

        self.qglClearColor(self.trolltechPurple.darker())

        #GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_DEPTH_TEST)

        
        
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        GL.glLoadIdentity()
        #GLU.gluPerspective(0,(self.width()/self.height()),0.1,15.0)
        
        GL.glTranslatef(self.xMov,self.yMov,-5.0)
        
        GL.glScalef(self.scale,self.scale,self.scale)
        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)

        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.lightPos)
        mult=5
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, (mult*self.scale,mult*self.scale,mult*self.scale,mult*self.scale))
        #GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (0.24725,0.1995,0.0745,1.0))
        #GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (0.1,0.1,0.1,1.0))

        
        GL.glCallList(self.object)
        
        
        GL.glLoadIdentity()
        GL.glDisable(GL.GL_DEPTH_TEST)
        self.qglColor(QtGui.QColor.fromCmykF(0.0,0.0,1.0,0.0))
        
        #Information
        if self.image and self.info:
            self.renderText(0.5, -self.sizeDiv + 0.1, 0.0, "Image Width: "+str(self.tex_width))
            self.renderText(0.5, -self.sizeDiv + 0.15, 0.0, "Image Height: "+str(self.tex_height))
            self.renderText(0.5, -self.sizeDiv + 0.2, 0.0, "Compression: "+''.join(self.image.header.ddspf.dwFourCC))
            self.renderText(0.5, -self.sizeDiv + 0.25, 0.0, "MipMaps: "+str(self.image.header.dwMipMapCount))
        elif self.info:
            self.renderText(0.5, -self.sizeDiv + 0.1, 0.0, "Vertex Count: "+str(self.vc))
            self.renderText(0.5, -self.sizeDiv + 0.15, 0.0, "Faces Count: "+str(self.fc))



        self.renderText(0.5, self.sizeDiv - 0.1 , 0.0, "3Dgamedevblog.com")
        
        self.qglColor(QtCore.Qt.white)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        side = min(width, height)
        #GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        tex_side=self.tex_width / self.tex_height
        
        f_height=width/tex_side
        if height>=f_height:
            f_width=width
        else:
            f_height=height
            f_width=f_height*tex_side
        
        #print('Viewport Size: ',width,height, 'Sides: ' ,side,tex_side, 'Texture Sizes: ',self.tex_width,self.tex_height)
        if self.image:
            GL.glViewport((width-f_width) /2, (height-f_height) /2, f_width, f_height)
            self.sizeDiv = 1.0
        else:
            GL.glViewport(0, 0, width, height)
            self.sizeDiv = float(height)/width

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        
        GL.glOrtho(-1.0, +1.0, self.sizeDiv, -self.sizeDiv,-0.1, 1000.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def wheelEvent(self, event):
        self.scale += event.delta()/(20*4*120.0)
        self.scale=max(0.005,self.scale)
        #print(event.delta(),self.scale)
        self.updateGL()
        
        
    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        
        if (event.buttons() & QtCore.Qt.LeftButton) and (event.modifiers() & QtCore.Qt.AltModifier):
            self.setXRotation(self.xRot + 8 * dy / 0.1 * 2.0 * self.scale)
            self.setZRotation(self.zRot + 8 * dx / 0.1 * 2.0 * self.scale)
        elif (event.buttons() & QtCore.Qt.LeftButton):
            self.setXRotation(self.xRot + 8 * dy / 0.1 * 2.0 * self.scale)
            self.setYRotation(self.yRot + 8 * dx / 0.1 * 2.0 * self.scale)
        elif event.buttons() & QtCore.Qt.MiddleButton:
            self.setXMov(dx)
            self.setYMov(dy)

            

        self.lastPos = QtCore.QPoint(event.pos())


    def keyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key_I:
            self.info = not self.info
            self.update()
        elif event.key() == QtCore.Qt.Key_1:
            self.lightPos[2]+=1.0
            self.update()
        elif event.key() == QtCore.Qt.Key_3:
            self.lightPos[2]-=1.0
            self.update()
        elif event.key() == QtCore.Qt.Key_4:
            self.lightPos[1]+=1.0
            self.update()
        elif event.key() == QtCore.Qt.Key_6:
            self.lightPos[1]-=1.0
            self.update()
        elif event.key() == QtCore.Qt.Key_7:
            self.lightPos[0]+=1.0
            self.update()
        elif event.key() == QtCore.Qt.Key_9:
            self.lightPos[0]-=1.0
            self.update()
        elif event.key() == QtCore.Qt.Key_R:
            print(self.lightPos,self.scale)

        
    def cubeDraw(self):
        print('drawingCube')
        #glRotatef(1.0, 3.0, 1.0, 1.0)
        #glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        


        #GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_EMISSION) ;
        #GL.glColorMaterial ( GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE ) 
        GL.glMaterialfv( GL.GL_FRONT, GL.GL_DIFFUSE, (0.0,0.8,0.8,1.0))
        #GL.glMaterialfv( GL.GL_FRONT, GL.GL_SPECULAR, (1.0,1.0,1.0,1.0))
        #GL.glMaterialf(GL.GL_FRONT, GL.GL_SHININESS, 100.0 );

        dlist=GL.glGenLists(1)
        self.qglColor(QtCore.Qt.red)
        GL.glNewList(dlist,GL.GL_COMPILE)
        GL.glBegin(GL.GL_QUADS)
        self.qglColor(self.trolltechGreen)
        for surface in surfaces:
            for vertex in surface:
                GL.glVertex3fv([v/3.0 for v in verticies[vertex]])
        GL.glEnd()
        GL.glEndList()
        return dlist

    def customModel(self,faces,verts,norms,lightPos):
        #Get vc and fc
        self.vc=len(verts)
        self.verts = verts
        self.fc=len(faces)
        self.faces=faces

        self.image=None
        self.scale=0.1
        self.xRot =0.0
        self.yRot =0.0
        self.zRot =0.0
        self.xMov =0.0
        self.yMov =0.0

        self.lightPos=lightPos

        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_CULL_FACE);
        GL.glDisable(GL.GL_CULL_FACE);
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glCullFace(GL.GL_FRONT_AND_BACK)
        #GL.glLightModeli(GL.GL_LIGHT_MODEL_TWO_SIDE, GL.GL_TRUE);
        #GL.glEnable( GL.GL_COLOR_MATERIAL )
        #GL.glEnable( GL.GL_LIGHT0 )

        #GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, (0.0, 1.0, 3.0, 0.0));
        #GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (1.0,1.0,1.0,0.6));
        #GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, (1.0,1.0,1.0,3.0));

        GL.glMaterialfv( GL.GL_FRONT, GL.GL_DIFFUSE, (0.7,0.7,0.7,1.0))
        #GL.glMaterialfv( GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT, (0.7,0.7,0.7,1.0))

        
        dlist=GL.glGenLists(1)
        
        GL.glNewList(dlist,GL.GL_COMPILE)
        
        #GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE);
        GL.glBegin(GL.GL_TRIANGLES)


        for face in faces:
            for vert in face:
                try:
                    GL.glNormal3fv(list(norms[vert]))
                except:
                    GL.glNormal3fv([0.0,0.0,1.0])
                GL.glVertex3fv(list(verts[vert]))
                
        GL.glEnd()
        GL.glEndList()
        #Update the Viewport
        self.resizeGL(self.width(),self.height())
        self.update()
        return dlist


    def makeTextureQuad(self):
        dlist=GL.glGenLists(1)
        GL.glNewList(dlist,GL.GL_COMPILE)
        
        GL.glBegin(GL.GL_QUADS)
        
        GL.glTexCoord2f(1, 0);
        GL.glVertex2f(1, 1);

        GL.glTexCoord2f(0, 0);
        GL.glVertex2f(-1, 1);

        GL.glTexCoord2f(0, 1);
        GL.glVertex2f(-1, -1);

        GL.glTexCoord2f(1, 1);
        GL.glVertex2f(1, -1);
        GL.glEnd()
        GL.glEndList()
        return dlist
    
    def makeObject(self):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)

        GL.glBegin(GL.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        Pi = 3.14159265358979323846
        NumSectors = 200

        for i in range(NumSectors):
            angle1 = (i * 2 * Pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)

            angle2 = ((i + 1) * 2 * Pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        GL.glEnd()
        GL.glEndList()

        return genList

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.qglColor(self.trolltechGreen)

        GL.glVertex3d(x1, y1, -0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x3, y3, -0.05)
        GL.glVertex3d(x4, y4, -0.05)

        GL.glVertex3d(x4, y4, +0.05)
        GL.glVertex3d(x3, y3, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x1, y1, +0.05)

    def extrude(self, x1, y1, x2, y2):
        self.qglColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        GL.glVertex3d(x1, y1, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
    
    def texture_setup(self,image_data):
        self.image=image_data
        if not self.image:
            return
        typ=''.join(self.image.header.ddspf.dwFourCC)
        if typ=='DX10':
            typ=image_types[self.image.header.dwdx10header.dxgi_format]
        else:
            typ=image_types[typ]
        
        height=self.image.header.dwHeight
        width=self.image.header.dwWidth
        
        #Changing Object
        self.object=self.makeTextureQuad()
        #Checking Rotation
        self.xRot=180*16.0
        self.yRot=0
        self.zRot=0
        self.xMov=0.0
        self.yMov=0.0
        self.scale=1.0
        
        GL.glDisable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        
        
        self.tex_width=width
        self.tex_height=height
        
        self.image.data.seek(0)
        
        #f=open('gl_data','wb')
        #f.write(self.image.data.read())
        #f.close()
        
        #set class texture size
        
        GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT )
        GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT )
        GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR )
        GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR )
        
        
        if not typ: #normal uncompressed Texture
            buf_size=self.image.header.dwPitchOrLinearSize * height
            
            if self.image.header.ddspf.dwImageMode=='BGRA':
                typ=GL.GL_BGRA
            else:
                typ=GL.GL_RGBA
            
            GL.glTexImage2D(GL.GL_TEXTURE_2D,0,3,width,height,0,typ,GL.GL_UNSIGNED_BYTE,image_data.data.read(buf_size))
        else:
            buf_size=self.image.header.dwPitchOrLinearSize
            #print(hex(self.image.header.dwFlags),(self.image.header.dwFlags & 0xff000000)>>24)
            if ((self.image.header.dwFlags & 0xff000000)>>24) == 0x80:
                self.image.unswizzle_2k()
            GL.glCompressedTexImage2D(GL.GL_TEXTURE_2D,0,typ,width,height,0,buf_size,self.image.data.read(buf_size))
            
        
        print(hex(typ),height,width,hex(buf_size))
        self.resizeGL(self.width(),self.height())
        self.update()
    
        
    def ctx_menu(self,position):
        menu=QMenu()
        menu.addAction(self.tr('Save Image'))
        menu.addAction(self.tr('Import Image'))
        menu.addAction(self.tr('Import Model'))
        menu.addAction(self.tr('Export Model'))
        menu.addAction(self.tr('Make Coffee'))

        res=menu.exec_(self.mapToGlobal(position))
        if not res:
            return
        
        if res.text()=='Save Image':
            print('Saving Image to DDS')
            location=QtGui.QFileDialog.getSaveFileName(caption="Save File",filter='*.dds')
            f=open(location[0],'wb')
            f.write(self.image.write_texture().read())
            f.close()
            #StatusBar notification
            self.window().statusBar.showMessage("Texture Saved to "+str(location[0]))
        elif res.text()=='Make Coffee':
            print('Making Coffee for buddaking')
            verts,norms,faces=self.loadOBJ('coffee.obj')
            self.object = self.customModel(faces,verts,norms)

        elif res.text()=='Import Image':
            print('Importing Image')
            location=QtGui.QFileDialog.getOpenFileName(caption="Open Image File",filter='*.dds ;; *.jpg ;; *.png')
            #Reseting Color
            self.qglColor(QtCore.Qt.white)
            
                       
            #Changing Object
            self.object=self.makeTextureQuad()
            #Checking Rotation
            self.xRot=180*16.0
            self.yRot=0
            self.zRot=0
            self.scale=1.0
            #print(self.xRot,self.yRot,self.zRot)
            
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glEnable (GL.GL_BLEND)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glDisable( GL.GL_LIGHTING )

            GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT )
            GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT )
            GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR )
            GL.glTexParameterf( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR )

            #Loading New Image to Viewport
            if not location[0].split('.')[-1]=='dds': #load normal textures
                print('Normal Image')
                im = Image.open(location[0], "r")
                self.tex_width, self.tex_height=im.size
                img_data = im.convert("RGBA").tostring("raw", "RGBA")
                GL.glTexImage2D(GL.GL_TEXTURE_2D,0,3,im.size[0],im.size[1],0,GL.GL_RGBA,GL.GL_UNSIGNED_BYTE,img_data)
            else: #load dds
                print('DDS Image')
                f=open(location[0],'rb')
                im = dds_file(True,f)
                self.tex_width=im.header.dwWidth
                self.tex_height=im.header.dwHeight
                self.MipMaps=im.header.dwMipMapCount

                typ=''.join(im.header.ddspf.dwFourCC)
                
                self.image=im
                self.loadDDS(typ,self.tex_width,self.tex_height,im)
                
                f.close()

            self.resizeGL(self.width(),self.height())
            self.update()
            self.win.scheduler_add_texture(im,location[0])
        
        elif res.text()=='Import Model':
            print('Importing Mesh to Viewport')
            location=QtGui.QFileDialog.getOpenFileName(caption="Open Model File",filter='*')
            #parse Model
            t=open(location[0],'rb')
            t.seek(0x4) #  Skip Header
            first = Model2k(t)
            first.data = first.read_strips(t)
            first.data = first.strips_to_faces()
            
            #vertices
            second = Model2k(t)
            second.data = second.get_verts(t,100.0)
            print(len(second.data))
            #normals
            third = Model2k(t)
            third.data = third.get_normals(t)
            k=StringIO()
            t.seek(0)
            k.write(t.read())
            k.seek(0)
            t.close()
            print('Mesh Vertex Count: ', len(second.data))
            
            self.object=self.customModel(first.data,second.data,third.data)
            self.win.scheduler_add_model(k)

        elif res.text()=='Export Model':
            print('Saving Model to Wavefront OBJ')
            location=QtGui.QFileDialog.getSaveFileName(caption="Save File",filter='*.obj')
            f=open(location[0],'w')

            #writing data
            f.write('o custom_mesh \n')
            for v in self.verts:
                f.write('v ' + ' '.join([str(vi) for vi in v]) + '\n')
            f.write('usemtl None \n')
            f.write('s off \n')
            for face in self.faces:
                f.write('f '+ ' '.join([str(fi+1) for fi in face]) + '\n')

            f.close()
            #StatusBar notification
            self.window().statusBar.showMessage("Obj Saved to "+str(location[0]))

    def loadOBJ(self,filename):
        numVerts = 0
        verts = []
        faces=[]
        norms = []
        vertsOut = []
        normsOut = []
        for line in open(filename, "r"):
            vals = line.split()
            if vals[0] == "v":
                v = map(float, vals[1:4])
                verts.append(v)
            if vals[0] == "vn":
                n = map(float, vals[1:4])
                norms.append(n)
            if vals[0] == "f":
                vals = [val.split("/")[0] for val in vals[1:4]]
                fa=map(int,vals)
                faces.append([f-1 for f in fa])
        return verts,norms,faces


    def loadDDS(self,typ,width,height,image):
        
        if typ=='DX10':
            typ=image_types[image.header.dwdx10header.dxgi_format]
        else:
            typ=image_types[typ]

        image.data.seek(0)
        if not typ: #normal uncompressed Texture
            print('Uncompressed Image')
            buf_size=image.header.dwPitchOrLinearSize * height
            
            if image.header.ddspf.dwImageMode=='BGRA':
                typ=GL.GL_BGRA
            else:
                typ=GL.GL_RGBA
            
            GL.glTexImage2D(GL.GL_TEXTURE_2D,0,3,width,height,0,typ,GL.GL_UNSIGNED_BYTE,image.data.read(buf_size))
        else:
            print('Compressed Image')
            buf_size=image.header.dwPitchOrLinearSize
            #print(hex(self.image.header.dwFlags),(self.image.header.dwFlags & 0xff000000)>>24)
            #if ((image.header.dwFlags & 0xff000000)>>24) == 0x80:
            #    image.unswizzle_2k()

            image.data.seek(0)
            GL.glCompressedTexImage2D(GL.GL_TEXTURE_2D,0,typ,width,height,0,buf_size,image.data.read(buf_size))



            
        
        #msg=QMessageBox()
        #msg.setText('Done')
        #msg.exec_()
            
       

        