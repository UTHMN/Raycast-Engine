import glfw
import numpy as np

from OpenGL.GL import *

from Buffers.chunk import Chunk
from Buffers.SSBO  import SSBO

from camera import Camera
from mesh   import Mesh
from shader import Shader
from settings import Settings

def main() -> None:
    if not glfw.init():  return
    
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(Settings.Screen.WIDTH, Settings.Screen.HEIGHT, "Raycasting", None, None)
    
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glViewport(0, 0, Settings.Screen.WIDTH, Settings.Screen.HEIGHT)

    shader = Shader("Shaders\\default.vsh", "Shaders\\default.fsh")

    screenVertices = np.array([
         1.0,  1.0,  0.0,
        -1.0,  1.0,  0.0,
         1.0, -1.0,  0.0,
        -1.0, -1.0,  0.0
    ], dtype=np.float32)

    screenIndices = np.array([
        0, 1, 2,
        1, 3, 2
    ], dtype=np.uint32)
    
    # Initialize Camera and Meshes
    camera = Camera(window, (0, 0, 0), (0, -90, 0), Settings.Camera.FOV, Settings.Camera.SPEED, Settings.Camera.SENSITIVITY)
    meshes: set[Mesh] = set()
    
    meshes.add(Mesh.create("Meshes\\monkey.glb"))
    
    meshVertices = []
    meshIndices  = []
    indicesOffset = 0
    for obj in meshes:
        for x, y, z in obj.vertices:
            meshVertices.append((x, y, z, 1))  # Add Padding
                
        for index in obj.indices:
            meshIndices.append(index + indicesOffset)
        
        indicesOffset += len(obj.vertices)
    
    meshVertices = np.array(meshVertices, dtype=np.float32)
    meshIndices  = np.array(meshIndices,  dtype=np.uint32)

    # Screen Buffer
    screenChunk = Chunk(screenVertices, screenIndices, 0, 3, GL_FLOAT)
    screenChunk.sendData()
    
    # Upload Mesh Data
    vertSSBO  = SSBO.sendData(meshVertices, 0)
    indexSSBO = SSBO.sendData(meshIndices,  1)

    # Constant Uniforms
    glUseProgram(shader.program)
    Shader.createUniform(shader.program, "CAM_PROJ_MAT", tuple(np.array(camera.PM   ).flatten('F')))
    Shader.createUniform(shader.program, "CAM_INV_PROJ", tuple(np.array(camera.invPM).flatten('F')))
            
    Shader.createUniform(shader.program, "CAM_FOV",  camera.FOV)
    Shader.createUniform(shader.program, "CAM_NEAR", camera.NEAR)
    Shader.createUniform(shader.program, "CAM_FAR",  camera.FAR)
    
    Shader.createUniform(shader.program, "numTriangles", len(meshIndices) // 3)
    
    lastTime = 0
    elapsedTime = 0
    inverseFPS = 1 / Settings.Screen.FPS

    while not glfw.window_should_close(window):
        
        if glfw.get_key(window, glfw.KEY_ESCAPE): glfw.set_window_should_close(window, True)
        
        glfw.poll_events()
        time = glfw.get_time()
        
        if elapsedTime >= inverseFPS:
            camera.update()
            
            glClearColor(0, 0, 0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT)
            
            glUseProgram(shader.program)
            
            # Uniforms
            Shader.createUniform(shader.program, "CAM_POS", tuple(camera.position))
            Shader.createUniform(shader.program, "CAM_ROT", tuple(camera.rotation))
            
            Shader.createUniform(shader.program, "CAM_VIEW_MAT", tuple(np.array(camera.getVM()       ).flatten('F')))
            Shader.createUniform(shader.program, "CAM_INV_VIEW", tuple(np.array(camera.getInverseVM()).flatten('F')))
            
            Shader.createUniform(shader.program, "iResolution", (Settings.Screen.WIDTH, Settings.Screen.HEIGHT))
            Shader.createUniform(shader.program, "iTime", time)
            
            screenChunk.bind()
            glDrawElements(GL_TRIANGLES, len(screenIndices), GL_UNSIGNED_INT, None)
            screenChunk.unbind()

            glfw.swap_buffers(window)
            elapsedTime = 0
        else:
            elapsedTime += time - lastTime
            
        lastTime = time

    screenChunk.delete()
    
    vertSSBO.delete()
    indexSSBO.delete()
    
    glDeleteProgram(shader.program)

    glfw.terminate()

if __name__ == "__main__":
    main()
