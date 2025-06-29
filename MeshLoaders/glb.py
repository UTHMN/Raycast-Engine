import base64
import json
import pygame
import struct

from io     import BytesIO
from typing import Union
from os     import path

number = Union[int, float]

class GLB:
    @staticmethod
    def load(filename: str):
        with open(filename, "rb") as f:
            data = f.read()

        # Parse GLB header
        magic, version, length = struct.unpack_from("<4sII", data, 0)
        assert magic == b'glTF', "Invalid GLB file"

        # JSON chunk
        jsonChunkLength, jsonChunkType = struct.unpack_from("<I4s", data, 12)
        assert jsonChunkType == b'JSON', "Expected JSON chunk"

        jsonStart = 20
        jsonEnd  = jsonStart + jsonChunkLength
        jsonData = json.loads(data[jsonStart:jsonEnd].decode("utf-8"))

        # BIN chunk
        binChunkLength, binChunkType = struct.unpack_from("<I4s", data, jsonEnd)
        assert binChunkType[:3] == b'BIN', "Expected BIN chunk"

        binStart = jsonEnd + 8
        binEnd  = binStart + binChunkLength
        binBlob = data[binStart:binEnd]

        mesh = jsonData["meshes"][0]
        primitive = mesh["primitives"][0]

        positions = GLB.unpackAttr(jsonData, binBlob, primitive, "POSITION")
        normals   = GLB.unpackAttr(jsonData, binBlob, primitive, "NORMAL")
        uvs       = GLB.unpackAttr(jsonData, binBlob, primitive, "TEXCOORD_0")
        
        indices = GLB.unpackIndices(jsonData, binBlob, primitive)
        texture = GLB.loadTextureSurface(jsonData, filename, primitive, binBlob)

        return positions, indices, normals, uvs, texture
    
    @staticmethod
    def unpackAttr(jsonData, binBlob, primitive, attrName):
        if attrName not in primitive["attributes"]:  return None

        accessorIndex = primitive["attributes"][attrName]
        accessor   = jsonData["accessors"][accessorIndex]
        bufferView = jsonData["bufferViews"][accessor["bufferView"]]

        byteOffset = bufferView.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        compType   = accessor["componentType"]
        count      = accessor["count"]
        typeString = accessor["type"]

        # Supported Component Types
        if compType == 5126:
            fmtChar = "f"
            bytesPerComp = 4
        elif compType == 5123:
            fmtChar = "H"
            bytesPerComp = 2
        elif compType == 5125:
            fmtChar = "I"
            bytesPerComp = 4
        else:
            raise NotImplementedError(f"Unsupported component type: {compType}")

        compCount = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[typeString]

        values = []
        for i in range(count):
            start = byteOffset + i * compCount * bytesPerComp
            comps = tuple(struct.unpack_from("<" + fmtChar * compCount, binBlob, start))

            values.append(comps)

        return values

    @staticmethod
    def unpackIndices(jsonData, binBlob, primitive):
        if "indices" not in primitive:  return None

        accessorIndex = primitive["indices"]
        accessor   = jsonData["accessors"][accessorIndex]
        bufferView = jsonData["bufferViews"][accessor["bufferView"]]

        byteOffset = bufferView.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        count = accessor["count"]
        componentType = accessor["componentType"]

        if componentType == 5123:
            fmtChar = "H"
            bytesPerComp = 2
        elif componentType == 5125:
            fmtChar = "I"
            bytesPerComp = 4
        else:
            raise NotImplementedError(f"Unsupported index component type: {componentType}")

        indices = []
        for i in range(count):
            start = byteOffset + i * bytesPerComp
            index = struct.unpack_from("<" + fmtChar, binBlob, start)[0]
            indices.append(index)

        return indices

    @staticmethod
    def loadTextureSurface(jsonData, filename, primitive, binBlob=None):
        materialIndex = primitive.get("material")
        if materialIndex is None:  return None

        material = jsonData["materials"][materialIndex]
        baseColorTextureInfo = material.get("pbrMetallicRoughness", {}).get("baseColorTexture")
        if baseColorTextureInfo is None:  return None

        textureIndex = baseColorTextureInfo["index"]
        texture = jsonData["textures"][textureIndex]
        imageIndex = texture["source"]
        imageInfo = jsonData["images"][imageIndex]

        if "uri" in imageInfo:
            imageUri = imageInfo["uri"]

            if imageUri.startswith("data:"):
                header, encoded = imageUri.split(",", 1)
                imageBytes = base64.b64decode(encoded)
                imageStream = BytesIO(imageBytes)
                surface = pygame.image.load(imageStream)
            else:
                imagePath = path.join(path.dirname(filename), imageUri)
                surface = pygame.image.load(imagePath)

            return surface

        elif "bufferView" in imageInfo:
            bufferViewIndex = imageInfo["bufferView"]
            bufferView = jsonData["bufferViews"][bufferViewIndex]
            byteOffset = bufferView.get("byteOffset", 0)
            byteLength = bufferView["byteLength"]

            imageBytes = binBlob[byteOffset:byteOffset + byteLength]
            imageStream = BytesIO(imageBytes)
            surface = pygame.image.load(imageStream)

            return surface
