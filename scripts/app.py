#!/usr/bin/env python
# coding=utf-8

import open3d as o3d
import streamlit as st
import tempfile
from cloud_processing import CloudProcessor, ClustersProcessor

from visualiztion import CloudVis

st.set_page_config(layout="wide")

st.write("""
# Safety doors
""")


# Загрузка файла через drag and drop
pcd_file = st.file_uploader('Load point cloud in pcd format',type=['pcd'], accept_multiple_files=False)

# Облако точек
pcd = None
# Загружаем облако точек из временного файла
if not pcd_file is None:
  with tempfile.NamedTemporaryFile(suffix=".pcd") as tp:
    tp.write(pcd_file.getvalue())
    pcd = o3d.io.read_point_cloud(tp.name)

  # Добавляем виджеты для конфигурирования обработки облака точек
  st.sidebar.write("Downsampling")
  voxel_size = st.sidebar.slider('Voxel size', min_value=0.05, max_value=0.8, value=0.1)

  st.sidebar.write("Statistical filtration")
  neighbours_num = st.sidebar.slider('Number of neighbours', min_value=1, max_value=100, value=20)

  st.sidebar.write("Radial filtration")
  points_num = st.sidebar.slider('Number of points', min_value=1, max_value=100, value=6)
  radius = st.sidebar.slider('Radius', min_value=0.05, max_value=1.0, value=0.2)

  # Создаем две колонки
  left_column, right_column = st.columns(2)

  # Создаем отображение исходного облака
  fig_src = CloudVis.drawGeometry([pcd])

  tof_processor = CloudProcessor(pcd)
  # Сжимаем облако
  tof_processor.downsample(voxel_size=voxel_size)
  # Статистическая фильтрация
  tof_processor.statisticalFiltration(nb_neighbors=neighbours_num, std_ratio=0.01)
  # Радиальная фильтрация
  tof_processor.radialFiltration(nb_points=points_num, radius=0.2)

  # Создаем отображение обработанного облака
  fig = CloudVis.drawGeometry([tof_processor.cloud])

  # Визуализируем слева исходное облако, справа - обработанное
  left_column.write("### Source cloud")
  left_column.plotly_chart(fig_src)
  right_column.write("### Processed cloud")
  right_column.plotly_chart(fig)
