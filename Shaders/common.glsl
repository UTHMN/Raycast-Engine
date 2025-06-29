float RayIntersectsTriangle(vec3 orig, vec3 dir, vec3 v0, vec3 v1, vec3 v2) {
    vec3 edge1 = v1 - v0;
    vec3 edge2 = v2 - v0;

    vec3 h = cross(dir, edge2);
    float a = dot(edge1, h);
    if (abs(a) < 0.0001)  return -1.0;
        
    float f = 1.0 / a;
    vec3 s = orig - v0;
    float u = f * dot(s, h);
    if (u < 0.0 || u > 1.0)  return -1.0;
        
    vec3 q = cross(s, edge1);
    float v = f * dot(dir, q);
    if (v < 0.0 || u + v > 1.0)  return -1.0;
        
    float t = f * dot(edge2, q);
    if (t > 0.0001)  return t;
        
    return -1.0;
}