# Herramientas de edición de historias (Pampai)

Scripts usados para editar las historias 9:16 de 30 s:

- `matte.py` — recorta a la presentadora con Robust Video Matting
  (modelo: https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx,
  guardarlo en `/home/claude/models/rvm.onnx`). Uso: `python3 matte.py src.mov alpha.mkv fgr.mp4`
- `art.py` / `art2.py` — dibujan fondos ilustrados, placas de beneficios y la placa final (CTA) con PIL y la fuente Inter Display.
- `cfgs.py` — configuración por video: escenas de fondo, cortes de subtítulos con tiempos y placas.
- `render.py` — compone presentadora + fondos + subtítulos animados + placas. Uso: `CFG=v3 python3 render.py v3/video.mp4`
- `music.py` — música de fondo sintetizada (sin derechos) + mezcla con la voz. Uso: `CFG=v3 python3 music.py`
- `link_overlay.png` — etiqueta "www.pampai.com" que se superpone abajo con ffmpeg.

Dependencias: `pip install --break-system-packages onnxruntime opencv-python-headless numpy pillow` y ffmpeg.
