# Gengar Theme

Tema de interfaz de escritorio para PokeMMO inspirado en Gengar.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `mod/` | Archivos que se empaquetan, incluidos el manifiesto, el icono, el tema y los sonidos. |
| `fuentes/audio/` y `fuentes/imagenes/` | Material de origen para editar el tema. |
| `fuentes/variantes/tema-anterior/` | Archivos de la versión anterior que difieren de los de `mod/`, conservados con sus rutas relativas. |
| `fuentes/tema-base/` | XML de los temas `default` y `android` del juego, tomados de [PokeMMO/PokeMMO_Mods](https://github.com/PokeMMO/PokeMMO_Mods) (`theme_history`). Los usa el validador cuando el juego no está instalado. |
| `herramientas/` | Scripts de Python para generar texturas, tintes y XML, y el validador `validar.py`. Los scripts de texturas usan Pillow. |
| `dist/` | Paquetes locales excluidos de Git mediante `.gitignore`. |

## Generar el paquete

Ejecuta lo siguiente en PowerShell desde esta carpeta.

```powershell
.\build.ps1
```

El script primero corre `herramientas/validar.py` y después empaqueta `mod/` en `dist/GengarTheme.mod`, sin compresión para que funcione en Android. Si la validación encuentra errores, no genera el paquete. Para empaquetar sin validar usa `.\build.ps1 -SinValidar`.

## Validación

`python herramientas/validar.py` revisa:

- Que todos los XML de `mod/` estén bien formados y que no haya archivos `.txt` dentro de `mod/`.
- Que existan los temas y textos declarados en `info.xml`, y los archivos que cargan los `include`, `images` y `fontDef`.
- Que cada `merge="true"` apunte a una ventana que existe en la versión final del tema del juego.
- Que las imágenes y fuentes que usa el mod estén definidas, y que cada imagen se defina antes de usarse.
- Que los tintes usen constantes definidas.

Para el tema del juego usa primero `C:\Program Files\PokeMMO\data\themes` (otra ruta con `--juego` o la variable `POKEMMO_DIR`) y, si no existe, `fuentes/tema-base/`. Cuando PokeMMO actualice su interfaz, actualiza `fuentes/tema-base/` con la carpeta `theme_history` de PokeMMO_Mods. Usa esta carpeta, `GengarTheme/`, como raíz del repositorio cuando lo subas a Git.

## Sonido shiny

`mod/sounds/2/1554.wav` usa el audio de `fuentes/audio/Gengar_Shiny_Bruma.wav` para el destello shiny en combate. PokeMMO puede reproducirlo cuando el destello aparece en cualquiera de los dos lados.
