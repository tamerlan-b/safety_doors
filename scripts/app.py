#!/usr/bin/env python
# coding=utf-8

import open3d as o3d
import streamlit as st
import tempfile
from cloud_processing import CloudProcessor, ClustersProcessor

from visualization import CloudVis

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
  with st.sidebar.expander("Downsampling"):
    voxel_size = st.slider('Voxel size', min_value=0.03, max_value=1.0, value=0.03)

  with st.sidebar.expander("Filtration"):
    st.write("Statistical filtration")
    neighbours_num = st.slider('Number of neighbours', min_value=1, max_value=100, value=20)

    st.write("Radial filtration")
    points_num = st.slider('Number of points', min_value=1, max_value=100, value=15)
    radius = st.slider('Radius', min_value=0.05, max_value=1.0, value=0.2)
  
  with st.sidebar.expander("Ground plane segmentation"): 
    g_distance_threshold = st.slider('Distance threshold', min_value=0.01, max_value=0.75, value=0.04, key="ground")
    g_ransac_n = st.slider('Ransac n', min_value=1, max_value=50, value=3, key="ground")
    g_num_iterations = st.slider('Number of iterations', min_value=100, max_value=10000, value=1000, key="ground")


  with st.sidebar.expander("Door plane segmentation"):
    d_distance_threshold = st.slider('Distance threshold', min_value=0.001, max_value=0.75, value=0.005, key="door")
    d_ransac_n = st.slider('Ransac n', min_value=1, max_value=50, value=3, key="door")
    d_num_iterations = st.slider('Number of iterations', min_value=100, max_value=10000, value=1000, key="door")

  with st.sidebar.expander("Clusterization"):
    eps = st.slider('Epsilon', min_value=0.01, max_value=0.9, value=0.1)
    min_points = st.slider('Minimum number of points', min_value=1, max_value=1000, value=10)

  with st.sidebar.expander("Meshes"):
    opacity = st.slider('Opacity', min_value=0.0, max_value=1.0, value=0.1)


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
  tof_processor.radialFiltration(nb_points=points_num, radius=radius)
  # Удаляем наибольшую плоскость
  tof_processor.removePlane(distance_threshold=g_distance_threshold, ransac_n=g_ransac_n, num_iterations=g_num_iterations)
  # Находим следующую наибольшую плоскость (предположительно дверь)
  door_plane, inliers = tof_processor.cloud.segment_plane(distance_threshold=d_distance_threshold, ransac_n=d_ransac_n, num_iterations=d_num_iterations)
  # Выделяем дверь из облака точек
  door_cloud = tof_processor.cloud.select_by_index(inliers)
  # Запоминаем обрамляющий прямоугольник двери
  door_bb = door_cloud.get_axis_aligned_bounding_box()
  # Удаляем задетектированную дверь
  tof_processor.cutPoints(inliers, invert=True)
  # Детектируем кластеры
  tof_clusters = ClustersProcessor(tof_processor.DbscanClusterization(eps=eps, min_points=min_points, verbose=False))
  # Фильтруем кластеры по количеству точек в них
  tof_clusters = tof_clusters.filterByNumPoints()
  # Создаем mesh'и кластеров
  clusters_meshes = tof_clusters.createMeshes(alpha=opacity)
  # Создаем mesh портала двери
  door_mesh = CloudVis.createMeshFromBB(door_bb)
  # Вычисляем количество пересечений объектов с порталом двери
  intersections = [mesh.is_intersecting(door_mesh) for mesh in clusters_meshes]
  # Отображаем кластеры и портал двери
  fig = CloudVis.drawGeometry(clusters_meshes + [door_mesh])

  # Визуализируем слева исходное облако, справа - обработанное
  left_column.write("### Source cloud")
  left_column.plotly_chart(fig_src)
  right_column.write("### Processed cloud")
  right_column.plotly_chart(fig)
