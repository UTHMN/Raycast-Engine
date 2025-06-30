#version 430

#include "common.glsl"

layout(std430, binding = 0) buffer VertexBuffer { vec3 vertices[]; };
layout(std430, binding = 1) buffer UVBuffer     { vec2 UVs[];      };
layout(std430, binding = 1) buffer IndexBuffer  { uint indices[];  };

uniform vec3 CAM_POS;
uniform mat4 CAM_INV_VIEW;
uniform mat4 CAM_INV_PROJ;

uniform float CAM_NEAR;
uniform float CAM_FAR;

uniform vec2 iResolution;
uniform float iTime;

uniform int numTriangles;

out vec4 FragColor;

void main()
{
    vec2 uv = (gl_FragCoord.xy / iResolution.xy) * 2.0 - 1.0;

    vec3 lightPosition = vec3(0.0, 10.0, 5.0);
    vec3 backgroundColor = vec3(0.0);

    float ambient = 0.2;
    float diffuse = 1.0;

    vec3 color = backgroundColor;

    vec4 clipPosition = vec4(uv.x, uv.y, -1.0, 1.0);
    vec4 viewPosition = CAM_INV_PROJ * clipPosition;
    
    vec3 rayDirectionViewSpace = normalize(viewPosition.xyz / viewPosition.w);
    vec3 rayDirection          = normalize((CAM_INV_VIEW * vec4(rayDirectionViewSpace, 0.0)).xyz);

    float closestDist = CAM_FAR;
    vec3 hitNormal = vec3(0.0);

    for (int i = 0; i < numTriangles; i++) {
        uint idx0 = indices[i * 3 + 0];
        uint idx1 = indices[i * 3 + 1];
        uint idx2 = indices[i * 3 + 2];

        vec3 v0 = vertices[idx0];
        vec3 v1 = vertices[idx1];
        vec3 v2 = vertices[idx2];

        float dist = RayIntersectsTriangle(CAM_POS, rayDirection, v0, v1, v2);
        if (dist > 0.0 && dist < closestDist) {
            closestDist = dist;
            hitNormal = normalize(cross(v1 - v0, v2 - v0));
        }
    }

    if (closestDist > CAM_NEAR && closestDist < CAM_FAR) {
        vec3 hitPoint = CAM_POS + closestDist * rayDirection;

        vec3 lightDirection = normalize(lightPosition - hitPoint);
        float angle = dot(lightDirection, hitNormal);

        color = vec3(1.0, 1.0, 1.0) * (ambient + diffuse * max(0.0, angle));
    }

    FragColor = vec4(color, 1.0);
}