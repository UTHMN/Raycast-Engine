import numpy as np
import pygame
from OpenGL.GL import *

from Buffers.VAO import VAO
from Buffers.VBO import VBO
from Buffers.EBO import EBO
from Buffers.texture import Texture, TextureArray

class Chunk:
    def __init__(
            self,
            vertices: np.ndarray,
            indices:  np.ndarray,
            index:    int,
            length:   int,
            dataType,
            textures: str | list[str] | pygame.Surface | list[pygame.Surface] | None = None
        ):
        
        self.vertices = vertices
        self.indices  = indices
        
        self.index    = index
        self.length   = length
        self.dataType = dataType
        
        self.VAO = VAO()
        self.VBO = VBO()
        self.EBO = EBO()
        
        if     textures is None:  self.textureAmount = 0
        else:  self.textureAmount = 1
        
        self.textures = None
        textureType = type(textures)
        
        if issubclass(textureType, pygame.Surface):
            newTexture = Texture()
            newTexture.loadSurface(textures)
            self.textures = newTexture
            
        elif issubclass(textureType, str):
            self.textures = Texture()
            self.textures.loadSurface(pygame.image.load(textures))
        
        elif issubclass(textureType, list):
            self.textures = TextureArray()
            self.textureAmount = len(textures)
            
            if all(issubclass(item, pygame.Surface) for item in textures):
                self.textures.loadLayers(textures)
            elif all(issubclass(item, str) for item in textures):
                newTextures = []
                for path in textures:
                    newTextures.append(pygame.image.load(path))
                self.textures.loadLayers(newTextures)
            else:
                raise RuntimeError(f"Unknown Texture Type: {type(textures[0])}")
        
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
        
    def bindTextureData(self, program, textureUnit) -> None:
        if self.textures:

            if isinstance(type(self.textures), TextureArray):
                uniformName = "u_textureArray"
                
                uniformLocation = glGetUniformLocation(program, uniformName)
                if uniformLocation != -1:
                    self.textures.bind(textureUnit)
                    glUniform1i(uniformLocation, 0)
                else:
                    print(f"Warning: Shader Fniform '{uniformName}' not Found for TextureArray.")

            elif isinstance(type(self.textures), Texture):
                uniformName = "u_texture2D"
                uniformLocation = glGetUniformLocation(program, uniformName)
                if uniformLocation != -1:
                    self.textures.bind(textureUnit)
                    glUniform1i(uniformLocation, 0)
                else:
                    print(f"Warning: Shader Uniform '{uniformName}' not Found for 2D Texture.")
            else:
                raise RuntimeError(f"Unsupported Texture Type: {type(self.textures)}")
            
    def unbindTextureData(self, textureUnit) -> None:
        if self.textures is None:  return

        if isinstance(type(self.textures), TextureArray) or isinstance(type(self.textures), Texture):
            self.textures.unbind(textureUnit)
        else:
            raise RuntimeError(f"Unsupported Texture Type: {type(self.textures)}")
    
    def bind(self)   -> None:  self.VAO.bind()
    def unbind(self) -> None:  self.VAO.unbind()

    def delete(self) -> None:
        self.VAO.delete()
        self.VBO.delete()
        self.EBO.delete()
