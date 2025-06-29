import glm
from typing import Union

from MeshLoaders.glb import GLB

number = Union[int, float]

class Mesh:
    def __init__(
            self,
            vertices: list[tuple[number, number, number]],
            indices:  list[tuple[int, int, int]],
            normals:  list[tuple[number, number, number]] | None = None,
            uvs:      list[tuple[number, number]]         | None = None,
            textures: list[str]                           | None = None
        ) -> None:
        
        self.vertices = list(vertices)
        self.indices  = list(indices)
        self.normals  = list(normals)  if normals  is not None else None
        self.uvs      = list(uvs)      if uvs      is not None else None
        self.textures = list(textures) if textures is not None else None
        
        self.scale = 1
        
    def update(self) -> None:
        self.vertices = [(x * self.scale, y * self.scale, z * self.scale) for x, y, z in self.vertices]
        
    @staticmethod
    def create(filename: str) -> "Mesh":
        if filename.endswith(".glb"):
            return Mesh(*GLB.load(filename))
        else:
            raise NotImplementedError(f"Unsupported Mesh Format: {filename.split('.')[-1]}")
