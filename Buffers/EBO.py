import numpy as np
from OpenGL.GL import *

from typing import Iterable

class EBO:
    def __init__(self):  self.ID = glGenBuffers(1)

    def bind(self)   -> None:  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ID)
    def unbind(self) -> None:  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def bufferData(self, data: np.ndarray, usage=GL_STATIC_DRAW) -> None:
        if not issubclass(type(data), np.ndarray):  data = np.array(data)
        
        self.bind()
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, usage)

    def delete(self) -> None:  glDeleteBuffers(1, [self.ID])
