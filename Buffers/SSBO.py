import numpy as np
from OpenGL.GL import *

from typing import Iterable

class SSBO:
    def __init__(self) -> None:
        self.ID = glGenBuffers(1)
        self.bindingPoint: int

    def bind(self)   -> None:  glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.ID)
    def unbind(self) -> None:  glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

    def bufferData(self, data: np.ndarray, usage=GL_STATIC_DRAW) -> None:
        if not issubclass(type(data), np.ndarray):  data = np.array(data)
        
        self.bind()
        glBufferData(GL_SHADER_STORAGE_BUFFER, data.nbytes, data, usage)

    def bindBase(self, bindingPoint: int) -> None:
        self.bindingPoint = bindingPoint
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self.bindingPoint, self.ID)

    def delete(self) -> None:  glDeleteBuffers(1, [self.ID])
    
    @staticmethod
    def sendData(data: Iterable, bindingPoint: int) -> "SSBO":
        newSSBO = SSBO()
        newSSBO.bind()
        newSSBO.bufferData(data)
        newSSBO.bindBase(bindingPoint)
        newSSBO.unbind()
        
        return newSSBO
