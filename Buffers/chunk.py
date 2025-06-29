import numpy as np

from OpenGL.GL import *

from Buffers.VAO import VAO
from Buffers.VBO import VBO
from Buffers.EBO import EBO

class Chunk:
    def __init__(
            self,
            vertices: np.ndarray,
            indices:  np.ndarray,
            index:    int,
            length:   int,
            dataType,
        ):
        
        self.vertices = vertices
        self.indices  = indices
        
        self.index    = index
        self.length   = length
        self.dataType = dataType
        
        self.VAO = VAO()
        self.VBO = VBO()
        self.EBO = EBO()
        
    def sendData(self) -> None:
        self.VAO.bind()  # VAO
        
        self.VBO.bind()  # VBO
        self.VBO.bufferData(self.vertices)
        
        self.EBO.bind()  # EBO
        self.EBO.bufferData(self.indices)
        
        # Vertex Attrib Pointer
        glEnableVertexAttribArray(self.index)
        glVertexAttribPointer(self.index, self.length, self.dataType, GL_FALSE, 0, None)
        
        self.VAO.unbind()
        self.VBO.unbind()
        self.EBO.unbind()
    
    def bind(self)   -> None:  self.VAO.bind()
    def unbind(self) -> None:  self.VAO.unbind()

    def delete(self) -> None:
        self.VAO.delete()
        self.VBO.delete()
        self.EBO.delete()
