from OpenGL.GL import *

class VAO:
    def __init__(self) -> None:  self.ID = glGenVertexArrays(1)

    def bind(self)   -> None:  glBindVertexArray(self.ID)
    def unbind(self) -> None:  glBindVertexArray(0)
    def delete(self) -> None:  glDeleteVertexArrays(1, [self.ID])
