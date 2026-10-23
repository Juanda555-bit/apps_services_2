# Pruebas Clase 7_8: JWT

- Registro: usuario `editor1` creado, respuesta 201, rol devuelto: [reader/editor]
- Login: respuesta 200, devolvió access_token
- GET /api/me: devolvió el usuario con rol [reader/editor]
- Crear/editar item: [resultado, por ejemplo "200 con editor" o "403 con reader"]