import glfw
import glm
from typing import Union

from settings import Settings

number = Union[int, float]

class Camera:
    def __init__(
            self,
            window,
            position: tuple[number, number, number] | None = (0.0,  0.0,  0.0),
            rotation: tuple[number, number, number] | None = (0.0, -90.0, 0.0),
            FOV:         number | None = 60,
            NEAR:        number | None = 0.1,
            FAR:         number | None = 100.0,
            speed:       number | None = 0.05,
            sensitivity: number | None = 50.0
        ) -> None:
        
        self.position = glm.vec3(position)
        self.rotation = glm.vec3(rotation)
        
        self.FOV  = FOV
        self.NEAR = NEAR
        self.FAR  = FAR
        
        self.speed       = speed
        self.sensitivity = sensitivity
        
        self.mousePosition    = glm.vec2(glfw.get_cursor_pos(window))
        self.oldMousePosition = self.mousePosition
        
        self.window = window
        self.updateVectors()
        
        self.PM = self.getPM()
        self.invPM = glm.inverse(self.PM)

    def updateVectors(self):
        yaw   = glm.radians(self.rotation.y)
        pitch = glm.radians(self.rotation.x)

        front = glm.vec3(
            glm.cos(yaw) * glm.cos(pitch),
            glm.sin(pitch),
            glm.sin(yaw) * glm.cos(pitch)
        )
        self.frontVector = glm.normalize(front)

        # Recalculate Right and Up Vectors
        self.rightVector = glm.normalize(glm.cross(self.frontVector, glm.vec3(0.0, 1.0, 0.0)))
        self.upVector    = glm.normalize(glm.cross(self.rightVector, self.frontVector))

        # Rotate Around Front
        if self.rotation.z != 0.0:
            rollMat = glm.rotate(glm.mat4(1.0), glm.radians(self.rotation.z), self.frontVector)
            self.rightVector = glm.vec3(rollMat * glm.vec4(self.rightVector, 0.0))
            self.upVector    = glm.vec3(rollMat * glm.vec4(self.upVector, 0.0))

    def updatePosition(self):
        moveX = (glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS) - (glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS)
        moveY = (glfw.get_key(self.window, glfw.KEY_Q) == glfw.PRESS) - (glfw.get_key(self.window, glfw.KEY_E) == glfw.PRESS)
        moveZ = (glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS) - (glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS)

        # Relative Movement Vector
        moveVector = (
            moveX * self.rightVector +
            moveY * self.upVector    +
            moveZ * self.frontVector
        )

        if glm.length(moveVector) > 0:
            moveVector = glm.normalize(moveVector)
            self.position += moveVector * self.speed

    def updateRotation(self, constrainPitch=True):
        self.mousePosition = glm.vec2(glfw.get_cursor_pos(self.window))

        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

            dx, dy = self.mousePosition - self.oldMousePosition
            dz = (glfw.get_key(self.window, glfw.KEY_Z) == glfw.PRESS) - (glfw.get_key(self.window, glfw.KEY_X) == glfw.PRESS)
            
            width, height = glfw.get_window_size(self.window)

            dx *= self.sensitivity / width
            dy *= self.sensitivity / height
            dz *= self.sensitivity / height
            
            self.rotation.z += dz
            
            rollRadians = glm.radians(-self.rotation.z)
            cosRoll = glm.cos(rollRadians)
            sinRoll = glm.sin(rollRadians)

            self.rotation.x += dx * sinRoll - dy * cosRoll
            self.rotation.y += dx * cosRoll + dy * sinRoll

            if constrainPitch:  self.rotation.x = glm.clamp(self.rotation.x, -89.9, 89.9)

            self.updateVectors()
        else:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)

        self.oldMousePosition = self.mousePosition

    def update(self):
        self.updateRotation()
        self.updatePosition()

    def getVM(self):
        return glm.lookAt(self.position, self.position + self.frontVector, self.upVector)

    def getInverseVM(self):
        return glm.inverse(self.getVM())
    
    def getPM(self):
        return glm.perspective(glm.radians(self.FOV), Settings.Screen.ASPECT_RATIO, Settings.Camera.NEAR, Settings.Camera.FAR)
    
    def getInversePM(self):
        return glm.inverse(self.getPM())
