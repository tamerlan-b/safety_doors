#!/usr/bin/env python
# coding=utf-8

import numpy as np
import open3d as o3d
import streamlit as st
import plotly.graph_objects as go
import tempfile

st.write("""
# Point cloud viewer
""")

def createScatter3dData(pcd):
  points = np.asarray(pcd.points)
  colors = np.asarray(pcd.colors)
  scdata = go.Scatter3d(
            x=points[:,0], 
            y=points[:,1], 
            z=points[:,2], 
            mode='markers',
            marker=dict(size=1, color=colors))
  return scdata

def drawGeometry(geometry, width=800, height=600, title=""):
  mydata = []
  for g in geometry:
    mydata.append(createScatter3dData(g))
  fig = go.Figure(
    data=mydata,
    layout=dict(
        width = width,
        height = height,
        scene=dict(
            xaxis=dict(visible=True),
            yaxis=dict(visible=True),
            zaxis=dict(visible=True)
        ),
        title=title,
    )
  )

  return fig

# Загрузка файла через drag and drop
pcd_file = st.file_uploader('Load point cloud in pcd format',type=['pcd'], accept_multiple_files=False)

if not pcd_file is None:

  # Создаем временный файл облака точек
  tp = tempfile.NamedTemporaryFile(suffix=".pcd")
  # Записываем байты во временный файл
  tp.write(pcd_file.getvalue())
  # Открываем облако
  pcd = o3d.io.read_point_cloud(tp.name)

  # Закрываем временный файл
  tp.close()

  # Добавим виджет для настройки степени сжатия облака
  voxel_size = st.slider('Voxel size', min_value=0.05, max_value=0.8)

  # Сжимаем облако
  compressed = pcd.voxel_down_sample(voxel_size=voxel_size)

  # Создаем отображение
  fig = drawGeometry([compressed])

  # Визуализируем
  st.plotly_chart(fig)


