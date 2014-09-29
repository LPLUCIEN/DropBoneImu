from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from socket import *
import select

name = 'BeaglePotBlack'

num_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

port = 4774 # port of the data broadcast
buff = 1024 # maximum size of the data from the BBB
sock = 0; #useful to initialise it here

######
# THESE COME FROM UDP USING MAGIC AND CODE... hopefully
pitch = 0.0
roll = 0.0
yaw = 0.0
######

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400,400)
    glutCreateWindow(name)

    glClearColor(0.,0.,1.,1.)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    lightZeroPosition = [-20.,2.,-2.,1.]
    lightZeroColor = [1.8,1.0,0.8,1.0] #green tinged
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(40.,1.,1.,40.)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0,0,10,
              0,0,0,
              0,1,0)
    glPushMatrix()
    glutMainLoop()
    return

def display():

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    color = [1.0,0.,0.,1.]
    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
    glRotatef(180,1,0,0) # The teapot is upside down by default
    glRotatef(90,0,1,0) # Make it face spout forward
    ####
    # These next three should now be in the correct order
    global yaw, roll, pitch
    glRotatef(yaw,1,0,0)
    glRotatef(roll,0,1,0)
    glRotatef(pitch,0,0,1)
    ####
    glutSolidTeapot(-2,20,-20)
    
    glPopMatrix()
    glutSwapBuffers()
    
    return

def animate():
    ####
    #Get data gets the values that are being broadcast over udp.
    global roll, pitch, yaw
    [yaw, roll, pitch] = get_data()
    glutPostRedisplay()

#makes the socket
def make_sock():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('<broadcast>', port))
    sock.setblocking(0)

#returns an array of floats or 0 if fail
#it should return the values from udp...
def get_data():
    if not sock:
        make_sock()
    result = select.select([sock],[],[])
    msg = result[0][0].recv(buff)
    current_float_string = "" #hold the current float in string while it is constructed
    float_array = [] #array to be returned
    for char in msg:
        if char == ',':
            float_array.append(float(current_float_string))
            current_float_string = ""
        elif char == '\0': #assuming that packet contains '\0' on the end, may be wrong
            float_array.append(float(current_float_string))
            return float_array
        elif char in num_chars:
            current_float_string.append(char)
    return [0, 0, 0]

if __name__ == '__main__': main()
