import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from os import path as ospath

class Shader:
    def __init__(self, vertexPath: str, fragmentPath: str) -> None:
        vertexSource = self.loadShaderSource(vertexPath)
        fragmentSource = self.loadShaderSource(fragmentPath)

        self.program = Shader.compileProgramWithLog(vertexSource, fragmentSource)

    @staticmethod
    def createUniform(shaderProgram, name, value, warnings=False):
        location = glGetUniformLocation(shaderProgram, name)
        if location == -1 and warnings:
            print(f"Warning: uniform '{name}' not found in shader.")
            return

        if isinstance(value, int):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, (tuple, list, np.ndarray)):
            length = len(value)
            if length == 2:
                glUniform2f(location, *value)
            elif length == 3:
                glUniform3f(location, *value)
            elif length == 4:
                glUniform4f(location, *value)
            elif length == 16:
                glUniformMatrix4fv(location, 1, GL_FALSE, np.array(value, dtype=np.float32))
            else:
                print(f"Unsupported uniform tuple/list size for '{name}'")
        else:
            print(f"Unsupported uniform type for '{name}': {type(value)}")

    @staticmethod
    def loadShaderSource(path):
        dirPath = ospath.dirname(path)
        with open(path, 'r') as file:
            lines = file.readlines()

        processedSource = ""
        for line in lines:
            if line.strip().startswith("#include"):
                includeFile = line.strip().split()[1].replace('"', '')
                includeFilePath = ospath.join(dirPath, includeFile)
                processedSource += Shader.loadShaderSource(includeFilePath) + '\n'
            else:
                processedSource += line

        return processedSource

    @staticmethod
    def compileShaderWithLog(source, shaderType):
        try:
            shader = compileShader(source, shaderType)
        except RuntimeError as e:
            print(f"Shader compile failed:\n{e}")
            raise
        
        return shader

    @staticmethod
    def compileProgramWithLog(vertexSource, fragmentSource):
        vertexShader = Shader.compileShaderWithLog(vertexSource, GL_VERTEX_SHADER)
        fragmentShader = Shader.compileShaderWithLog(fragmentSource, GL_FRAGMENT_SHADER)
        try:
            program = compileProgram(vertexShader, fragmentShader)
            
            linkStatus = glGetProgramiv(program, GL_LINK_STATUS)
            if not linkStatus:
                print("Program link failed:\n" + glGetProgramInfoLog(program).decode())
                raise RuntimeError("Shader link failed")

            glValidateProgram(program)
            validateStatus = glGetProgramiv(program, GL_VALIDATE_STATUS)
            if not validateStatus:
                print("Program validation failed:\n" + glGetProgramInfoLog(program).decode())
                raise RuntimeError("Shader validation failed")

            return program
        
        except Exception as e:
            raise RuntimeError(f"Error compiling/linking shader program: {e}")
