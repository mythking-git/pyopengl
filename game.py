###### Reference Tutorial ######

# https://www.youtube.com/playlist?list=PLn3eTxaOtL2PDnEVNwOgZFm5xYPr4dUoR
# by GetIntoGameDev

######      Packages      ######

import pygame as pg

import numpy as np
import ctypes

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# https://pyrr.readthedocs.io/en/latest/
import pyrr

######      Classes       ######

class Cube:

    def __init__(self,position,eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class App:
    def __init__(self):
        # pygame init
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)  # doublebuf is display style for opengl, one frame 2 draws.
        self.clock = pg.time.Clock()  # control framerate

        # init opengl
        glClearColor(0.2, 0.2, 0.2, 1)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # import shaders
        self.shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)

        # Loads texture to point 0
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        self.cube = Cube(
            position = [0,0,-3],
            eulers = [0,0,0]
        )

        self.cube_mesh = CubeMesh()

        self.uv_check_texture = Material("gfx/cat.jpg")

        # https://pyrr.readthedocs.io/en/latest/api_matrix.html?highlight=projection#module-pyrr.matrix44
        # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480,
            # near and far used to cull for performance + mathmatical errors
            near = 0.1, far = 10, dtype=np.float32
        )

        # https://registry.khronos.org/OpenGL-Refpages/gl4/html/glUniform.xhtml
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            # GL_FALSE as transpose not needed for column matrix
            1, GL_FALSE, projection_transform
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")

        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):
        with open(vertexFilepath, "r") as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath, "r") as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader

    def mainLoop(self):
        running = True
        while running:
            # check events
            for event in pg.event.get():
                if event.type == pg.QUIT:  # QUIT as pygame method
                    running = False

            # update cube

            # roll = 0  [z] side to side
            # pitch = 1 [x] forward to back
            # yaw = 2   [y] left to right
            
            self.cube.eulers[2] += 1
            if (self.cube.eulers[2] > 360):
                self.cube.eulers[2] -= 360



            # refreshes screen

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader)

            self.uv_check_texture.use()

            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers),
                    dtype=np.float32
                )
            )

            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=self.cube.position,
                    dtype=np.float32
                )
            )

            # upload
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)

            # pulls mesh  data
            glBindVertexArray(self.cube_mesh.vao)

            # draws the pulled data
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            pg.display.flip()

            # timing
            self.clock.tick(60)

            pg.display.set_caption(str(self.clock))
        self.quit() 

    def quit(self):

        # used to free memory
        self.cube_mesh.destroy()

        self.uv_check_texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class CubeMesh:
    def __init__(self):
        # a vertex in openGL is data that is
        # stored within each point not just a location

        # x, y, z, s, t

        # x = left to right
        # y = up to down
        # z = forward to back

        self.vertices = (
            -0.5, -0.5, -0.5, 0, 0,
             0.5, -0.5, -0.5, 1, 0,
             0.5,  0.5, -0.5, 1, 1,

             0.5,  0.5, -0.5, 1, 1,
            -0.5,  0.5, -0.5, 0, 1,
            -0.5, -0.5, -0.5, 0, 0,

            -0.5, -0.5,  0.5, 0, 0,
             0.5, -0.5,  0.5, 1, 0,
             0.5,  0.5,  0.5, 1, 1,

             0.5,  0.5,  0.5, 1, 1,
            -0.5,  0.5,  0.5, 0, 1,
            -0.5, -0.5,  0.5, 0, 0,

            -0.5,  0.5,  0.5, 1, 0,
            -0.5,  0.5, -0.5, 1, 1,
            -0.5, -0.5, -0.5, 0, 1,

            -0.5, -0.5, -0.5, 0, 1,
            -0.5, -0.5,  0.5, 0, 0,
            -0.5,  0.5,  0.5, 1, 0,

             0.5,  0.5,  0.5, 1, 0,
             0.5,  0.5, -0.5, 1, 1,
             0.5, -0.5, -0.5, 0, 1,

             0.5, -0.5, -0.5, 0, 1,
             0.5, -0.5,  0.5, 0, 0,
             0.5,  0.5,  0.5, 1, 0,

            -0.5, -0.5, -0.5, 0, 1,
             0.5, -0.5, -0.5, 1, 1,
             0.5, -0.5,  0.5, 1, 0,

             0.5, -0.5,  0.5, 1, 0,
            -0.5, -0.5,  0.5, 0, 0,
            -0.5, -0.5, -0.5, 0, 1,

            -0.5,  0.5, -0.5, 0, 1,
             0.5,  0.5, -0.5, 1, 1,
             0.5,  0.5,  0.5, 1, 0,

             0.5,  0.5,  0.5, 1, 0,
            -0.5,  0.5,  0.5, 0, 0,
            -0.5,  0.5, -0.5, 0, 1
        )

        # Each vertex is calculated by intdiv to account for each points' data
        self.vertex_count = len(self.vertices) // 5

        # numpy allows the GPU to read the data structure
        # default python is unreadable by the GPU
        # unsigned 32b is required for this action


        self.vertices = np.array(self.vertices, dtype=np.float32)

        # vao = vertex array object
        # declares the numpy array as a vertex array
        # https://youtu.be/Rin5Cp-Hhj8

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vbo = vertex buffer object
        # buffers sends data to the GPU to tell where, how much bytes, what to do
        # static draw as it's not rewriten often, just read

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(
            GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW
        )

        # enables attributes and describes which attribute, it's length, how to normalise,
        # and then how many to "stride" to get to the next set of attributes
        # ctypes are used to make python understand what i'm doing as it requires pointers

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))

    def destroy(self):
        # must be a list so tuple has extra comma

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Material:

    def __init__(self, filepath):

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        # address in s/t coord pairs from 0 to 1.
        # s=0 = left    s=1 = right
        # t=0 = top     t=1 = bottom

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Min & Mag to shrink or scale to the size of the object
        # Nearest to roughly shrink
        # Linear to linearly scale
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pg.image.load(filepath).convert_alpha()
        image_width, image_height = image.get_rect().size
        image_data = pg.image.tostring(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

        # Mipmaps are scaled down usually 50% to make distance textures more performant
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):

        glDeleteTextures(1, (self.texture,))

#####      Main Loop       ######

if __name__ == "__main__":
    myApp = App()