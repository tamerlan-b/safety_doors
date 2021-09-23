#!/usr/bin/env python
# coding=utf-8

import numpy as np
import open3d as o3d

class CloudProcessor:
    """Класс для обработки облака точек"""
    
    def __init__(self, cloud):
        self.cloud = cloud

    def downsample(self, voxel_size=0.03):
        self.cloud = self.cloud.voxel_down_sample(voxel_size=voxel_size)
        return self

    def alignPlaneWithZ(self, plane):
        # Параметры плоскости
        [a,b,c,d] = plane
        # Ось вращения для совмещения нормали к плоскости с осью z
        axis = np.array([b,a,0])
        # Угол поворота
        angle = np.arccos(c)
        # Приводим ось вращения в формат вектора Родриго
        axis = (axis / np.linalg.norm(axis)) * angle
        # Получаем матрицу поворота вокруг вектора на заданный угол
        R = self.cloud.get_rotation_matrix_from_axis_angle(axis)
        # Поворачиваем облако
        self.cloud.rotate(R, center=(0,0,0))
        # Переносим облако для совпадения плоскостей
        self.cloud.translate((0,0,d))
        return self
  
    def statisticalFiltration(self, nb_neighbors=20, std_ratio=0.01):
        self.cloud, ind_f1 = self.cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors,
                                                            std_ratio=std_ratio)
        return self

    def radialFiltration(self, nb_points=15, radius=0.15):
        self.cloud, ind_f2 = self.cloud.remove_radius_outlier(nb_points=nb_points, radius=radius)
        return self
  
    def removePlane(self, distance_threshold=0.04, ransac_n=3, num_iterations=1000):
        plane_model, inliers = self.cloud.segment_plane(distance_threshold=0.04,
                                            ransac_n=3, num_iterations=1000)
        self.cutPoints(inliers, invert=True)
        return self

    def cutPoints(self, indices, invert=False):
        self.cloud = self.cloud.select_by_index(indices, invert=invert)
        return self

    # Кластеризация с использованием алгоритма DBSCAN
    def DbscanClusterization(self, eps=0.1, min_points=10, verbose=False):
        # with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
        labels = np.array(self.cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=verbose))

        max_label = labels.max()
        clusters = []
        for i in range(max_label + 1):
            cluster = o3d.geometry.PointCloud()
            cluster.points = o3d.utility.Vector3dVector(np.asarray(self.cloud.points)[labels == i])
            cluster.colors = o3d.utility.Vector3dVector(np.asarray(self.cloud.colors)[labels == i])
            clusters.append(cluster)

        return clusters


class ClustersProcessor:
    """Класс для обработки кластеров облаков точек"""

    def __init__(self, clusters):
        self.clusters = clusters

    def filterByNumPoints(self, min_points_num = 80):
        filtered_clusters = []
        for cl in self.clusters:
            if len(cl.points) > min_points_num:
                filtered_clusters.append(cl)
        self.clusters = filtered_clusters
        return self

    def getAABB(self, color = (1, 0, 0)):
        bb = []
        for cl in self.clusters:
            aabb = cl.get_axis_aligned_bounding_box()
            aabb.color = color
            bb.append(aabb)
        return bb

    def getOBB(self, color = (1, 0, 0)):
        bb = []
        for cl in self.clusters:
            obb = cl.get_oriented_bounding_box()
            obb.color = color
            bb.append(obb)
        return bb

    def createMeshes(self, alpha=0.2):
        meshes = []
        for cluster in self.clusters:
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(cluster, alpha=0.2)
            mesh.compute_vertex_normals()
            meshes.append(mesh)
        return meshes
