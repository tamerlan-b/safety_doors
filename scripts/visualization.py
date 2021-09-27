#!/usr/bin/env python
# coding=utf-8


import numpy as np
import open3d as o3d
import plotly.graph_objects as go


class CloudVis:
    """Класс для визуализации облаков точек с помощью библиотеки plotly"""

    @staticmethod
    def createMeshFromBB(bb):
        # Создаем mesh из обрамляющего прямоугольника
        bbcloud = o3d.geometry.PointCloud()
        bbcloud.points = bb.get_box_points()
        bb.color = bb.color
        hull, _ = bbcloud.compute_convex_hull()
        return hull

    @staticmethod
    def createMeshData(mesh, opacity=0.2):
        verts = np.asarray(mesh.vertices)
        triangs = np.asarray(mesh.triangles)

        mdata = go.Mesh3d(
                x=verts[:,0],
                y=verts[:,1],
                z=verts[:,2],
                i = triangs[:,0],
                j = triangs[:,1],
                k = triangs[:,2],
                opacity=opacity,
            )
        return mdata

    @staticmethod
    def createScatter3dData(pcd):
        points = np.asarray(pcd.points)
        colors = np.asarray(pcd.colors)
        scdata = go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode="markers",
            marker=dict(size=1, color=colors),
        )
        return scdata

    @staticmethod
    def drawGeometry(geometry, width=800, height=600, title=""):
        mydata = []
        for g in geometry:
            if type(g) is o3d.geometry.PointCloud:
                mydata.append(CloudVis.createScatter3dData(g))
            elif (
                type(g) is o3d.geometry.AxisAlignedBoundingBox
                or type(g) is o3d.geometry.OrientedBoundingBox
            ):
                m = CloudVis.createMeshFromBB(g)
                mydata.append(CloudVis.createMeshData(m))
            elif type(g) is o3d.geometry.TriangleMesh:
                mydata.append(CloudVis.createMeshData(g))

        fig = go.Figure(
            data=mydata,
            layout=dict(
                width=width,
                height=height,
                scene=dict(
                    xaxis=dict(visible=True),
                    yaxis=dict(visible=True),
                    zaxis=dict(visible=True),
                ),
                title=title,
            ),
        )
        return fig

    @staticmethod
    def display_inlier_outlier(
        cloud, ind, in_color=None, out_color=[1, 0, 0], title=""
    ):
        inlier_cloud = cloud.select_by_index(ind)
        outlier_cloud = cloud.select_by_index(ind, invert=True)

        print("Showing outliers (red) and inliers (gray): ")
        if not out_color is None:
            outlier_cloud.paint_uniform_color(out_color)
        if not in_color is None:
            inlier_cloud.paint_uniform_color(in_color)
        return CloudVis.drawGeometry([inlier_cloud, outlier_cloud], title=title)
