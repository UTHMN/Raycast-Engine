import numpy as np
from OpenGL.GL import *
import pygame

from typing import Union

number = Union[int, float]

class Texture:
    def __init__(self) -> None:
        self.ID = glGenTextures(1) # Generate a single texture ID
        self.width = 0
        self.height = 0

    def bind(self, textureUnit=GL_TEXTURE0) -> None:
        glActiveTexture(textureUnit)
        glBindTexture(GL_TEXTURE_2D, self.ID)

    def unbind(self, textureUnit=GL_TEXTURE0) -> None:
        glActiveTexture(textureUnit)
        glBindTexture(GL_TEXTURE_2D, 0)

    def loadSurface(
            self,
            surface: pygame.Surface,
            internalFormat=GL_RGBA8,
            inputFormat=GL_RGBA,
            inputType=GL_UNSIGNED_BYTE,
            generateMipmaps: bool | None = True
        ) -> None:
        
        self.width = surface.get_width()
        self.height = surface.get_height()

        textureData = pygame.image.tostring(surface, "RGBA", True)

        self.bind()

        glTexImage2D(
            GL_TEXTURE_2D,
            0,               # Mipmap level
            internalFormat,
            self.width,
            self.height,
            0,
            inputFormat,
            inputType,
            textureData
        )

        if generateMipmaps:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # U
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  # V

        if generateMipmaps:  glGenerateMipmap(GL_TEXTURE_2D)  # Generate Mipmaps

        self.unbind()

    def setParam(self, paramName, param: number) -> None:
        self.bind()
        glTexParameteri(GL_TEXTURE_2D, paramName, param)
        self.unbind()

    def delete(self) -> None:  glDeleteTextures(1, [self.ID])

class TextureArray:
    def __init__(self):
        self.ID = glGenTextures(1)
        self.width  = 0
        self.height = 0
        self.depth  = 0

    def loadLayers(self, surfaces: list[pygame.Surface]):
        if len(surfaces) == 0:  raise ValueError("No surfaces provided for texture array.")

        self.depth = len(surfaces)
        for i in range(self.depth):
            newWidth  = surfaces[i].get_width()
            newHeight = surfaces[i].get_height()
            
            if newWidth  > self.width:   self.width = newWidth
            if newHeight > self.height:  self.height = newHeight

        glBindTexture(GL_TEXTURE_2D_ARRAY, self.ID)

        glTexImage3D(
            GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8, 
            self.width, self.height, self.depth, 
            0, GL_RGBA, GL_UNSIGNED_BYTE, None
        )

        for i, surface in enumerate(surfaces):
            newSurface = pygame.Surface((self.width, self.height))
            newSurface.set_colorkey((0, 0, 0))
            newSurface.blit(surface, (0, 0))
            
            layerData = pygame.image.tostring(newSurface, "RGBA", True)
            
            glTexSubImage3D(
                GL_TEXTURE_2D_ARRAY, 0, 
                0, 0, i,
                self.width, self.height, 1,
                GL_RGBA, GL_UNSIGNED_BYTE, layerData
            )
        
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

        glBindTexture(GL_TEXTURE_2D_ARRAY, 0)
    
    def bind(self, texture_unit=GL_TEXTURE0):
        glActiveTexture(texture_unit)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.ID)

    def unbind(self, texture_unit=GL_TEXTURE0):
        glActiveTexture(texture_unit)
        glBindTexture(GL_TEXTURE_2D_ARRAY, 0)

    def delete(self):
        glDeleteTextures(1, [self.ID])