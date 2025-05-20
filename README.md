## ❓ ¿Qué hace este programa?

**BlockTexturePreviewer** es una herramienta visual interactiva para previsualizar texturas para bloques de Minecraft.

- Permite **rotar, hacer zoom y examinar bloques 3D renderizados**.
- Carga **modelos JSON de bloques** de Minecraft (como los del directorio `assets/minecraft/models/block/`).
- Usa las **texturas definidas en el archivo `.json`** para mostrar el bloque en 3D.

---

## 📁 Estructura esperada de archivos

Al ejecutar el `.exe` o el `.py`, el programa busca en la misma carpeta un archivo llamado:

`path.json`

Este archivo debe contener la ruta al modelo `.json` del bloque que quieres previsualizar. Ejemplo:

```json
{
  "model_path": "C:/Users/MyUsuario/Desktop/carpeta_principal/cube_top_bottom.json"
}
```
ó simplemente: 
```json
{
  "model_path": "cube_top_bottom.json"
}
```
⚠️ Importante: Las texturas deben estar ubicadas en el mismo nivel que el modelo, en una subcarpeta textures/, por ejemplo:


```bash
📂 carpeta_principal/
├── BlockTexturePreviewer.exe
├── cube_top_bottom.json
├── path.json
└── 📂 textures/
    └── 📂 block/
         └── texture_top.png
         └── dirt.png
         └── texture_side.png
```

![example](https://github.com/user-attachments/assets/e9b9d23c-d435-401f-9685-aa7386bb233d)
