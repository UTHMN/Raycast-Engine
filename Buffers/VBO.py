import numpy as np
from OpenGL.GL import *

class VBO:
    def __init__(self) -> None:  self.ID = glGenBuffers(1)

    def bind(self)   -> None:  glBindBuffer(GL_ARRAY_BUFFER, self.ID)
    def unbind(self) -> None:  glBindBuffer(GL_ARRAY_BUFFER, 0)

    def bufferData(self, data: np.ndarray, usage=GL_STATIC_DRAW) -> None:
        if not issubclass(type(data), np.ndarray):  data = np.array(data)
        
        self.bind()
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, usage)

    def delete(self) -> None:  glDeleteBuffers(1, [self.ID])
