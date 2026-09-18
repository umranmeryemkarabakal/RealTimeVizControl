# RealTimeVizControl

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt5" />
  <img src="https://img.shields.io/badge/OpenGL-5586A4?style=for-the-badge" alt="OpenGL" />
  <img src="https://img.shields.io/badge/pyqtgraph-1F2A44?style=for-the-badge" alt="pyqtgraph" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
</p>

## 🇬🇧 Overview

A real-time monitoring panel in PyQt5: it reads orientation data over serial, rotates a 3D model with OpenGL, plots the values live with pyqtgraph, shows the webcam feed and logs everything to CSV.

**Quick start:** `pip install -r requirements.txt && python main.py`

## 🇹🇷 Proje hakkında

Seri porttan gelen açı verisiyle bir 3B modeli OpenGL üzerinde döndüren, değerleri pyqtgraph ile canlı çizen, kamera görüntüsünü gösteren ve verileri CSV'ye kaydeden PyQt5 izleme paneli.

## ✨ Özellikler

- `cubeObje.obj` modelini okuyup X/Y/Z eksenlerinde döndürme
- Üç kanallı canlı grafik
- OpenCV ile kamera akışı
- Tablo ve CSV kaydı
- Seri porta veri gönderme

## ⚙️ Kurulum ve çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

```bash
python main.py
```

## 📁 Dosya yapısı

```text
RealTimeVizControl/
├── cubeObje.obj
├── gui.py
└── main.py
```
