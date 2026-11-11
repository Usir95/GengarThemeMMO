# Gengar Theme

Tema de interfaz de escritorio para PokeMMO inspirado en Gengar.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `mod/` | Archivos que se empaquetan, incluidos el manifiesto, el icono, el tema y los sonidos. |
| `fuentes/audio/` y `fuentes/imagenes/` | Material de origen para editar el tema. |
| `fuentes/variantes/tema-anterior/` | Archivos de la versión anterior que difieren de los de `mod/`, conservados con sus rutas relativas. |
| `herramientas/` | Scripts de Python para recolorear texturas y tintes XML. El script de texturas usa Pillow. |
| `dist/` | Paquetes locales excluidos de Git mediante `.gitignore`. |

## Generar el paquete

Ejecuta lo siguiente en PowerShell desde esta carpeta.

```powershell
.\build.ps1
```

El script empaqueta `mod/` en `dist/GengarTheme.mod`. Usa esta carpeta, `GengarTheme/`, como raíz del repositorio cuando lo subas a Git.

## Sonido shiny

`mod/sounds/2/1554.wav` usa el audio de `fuentes/audio/Gengar_Shiny_Bruma.wav` para el destello shiny en combate. PokeMMO puede reproducirlo cuando el destello aparece en cualquiera de los dos lados.
