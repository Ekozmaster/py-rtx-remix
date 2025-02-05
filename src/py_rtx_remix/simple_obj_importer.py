from collections import OrderedDict
from typing import List

from .components import Float3D, Float2D, Vertex, MeshSurface, Mesh, Material


def _load_obj_from_split(
    lines: list[str],
    mat: Material | None,
    vertices: List[Float3D],
    normals: List[Float3D],
    texcoords: List[Float2D],
) -> Mesh:
    materials_index = [0] + [lines.index(line) for line in lines if line.startswith('usemtl ')] + [None]
    materials_split = [lines[materials_index[i] + 1:materials_index[i + 1]] for i in range(len(materials_index) - 1)]

    surfaces = list()
    for mat_split in materials_split:
        indices = []
        faces = [
            [vtn_idx.split('/') for vtn_idx in line.split(' ', 1)[1].split(' ')]
            for line in mat_split if line.startswith('f ')
        ]
        if not faces:
            continue

        vertices_dict = OrderedDict()
        for face_primitive in faces:  # triangles or quads. I.e: 2/1/1 3/2/1 1/3/1
            for vert in face_primitive:
                vtn_key = (vert[0], vert[1], vert[2])
                if vtn_key not in vertices_dict:
                    # Stupidly, positive indices start at 1, not zero, while negative indices are fine.
                    pos_idx = int(vert[0]) + (0 if vert[0].startswith('-') else -1)
                    tex_idx = int(vert[1]) + (0 if vert[1].startswith('-') else -1) if vert[1] else None
                    nrm_idx = int(vert[2]) + (0 if vert[2].startswith('-') else -1)
                    vertices_dict[vtn_key] = Vertex(
                        position=vertices[pos_idx],
                        texcoord=texcoords[tex_idx] if tex_idx is not None else Float2D(0, 0),  # Models with no UVs.
                        normal=normals[nrm_idx]
                    ).as_struct()

        vtn_indices = dict(zip(vertices_dict.keys(), range(len(vertices_dict))))
        for face in faces:
            for vert in face:
                vtn_key = (vert[0], vert[1], vert[2])
                indices.append(vtn_indices[vtn_key])

        mesh_vertices = list(vertices_dict.values())

        surfaces.append(MeshSurface(vertices=mesh_vertices, indices=indices, material=mat).as_struct())
    return Mesh(surfaces=surfaces)


def load_obj(file_path: str, mat: Material | None) -> List[Mesh]:
    """
    Loads a Wavefront OBJ file. Supports multiple meshes with multiple materials each.
    :param file_path: The path to the file.
    :param mat: Which material to use for all meshes.
    :return: A list of all meshes in the file. You still need to set their mesh_hash before calling create_mesh.
    """
    # TODO: Decouple materials to set externally.
    with open(file_path, "r") as f:
        obj_contents = f.read()

    lines = obj_contents.splitlines()
    vertices = [
        Float3D(float(v[1]), float(v[2]), float(v[3]))
        for line in lines if line.startswith('v ')
        if (v := line.rsplit(' ', 3))
    ]
    normals = [
        Float3D(float(v[1]), float(v[2]), float(v[3]))
        for line in lines if line.startswith('vn ')
        if (v := line.rsplit(' ', 3))
    ]
    texcoords = [
        Float2D(float(v[1]), float(v[2]))
        for line in lines if line.startswith('vt ')
        if (v := line.rsplit(' ', 2))
    ]
    objects_index = [0] + [lines.index(line) for line in lines if line.startswith('o ')] + [None]
    objs_split = [lines[objects_index[i] + 1:objects_index[i + 1]] for i in range(len(objects_index) - 1)]
    meshes = [
        _load_obj_from_split(obj_split, mat, vertices, normals, texcoords)
        for obj_split in objs_split
    ]
    return meshes


if __name__ == "__main__":
    material = None
    meshes = load_obj('tests/unit/fixtures/TestQuads.obj', material)
    ...
