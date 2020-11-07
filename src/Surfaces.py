from numpy.matrixlib.defmatrix import matrix
from src.Core import v2, v3
from typing import Literal, Tuple, List


class BilinearSurface():
    default_points = [
        [
            v3((-150,-150,0)),
            v3((-150, 150,0)),
        ],
        [
            v3(( 150,-150,0)),
            v3(( 150, 150,0))
        ]
    ]

    def __init__(self, points: List[v3] = default_points):
        self.m = matrix(points)

    def calculate(self, u: float,w: float):
        a = matrix(
            [1-u, u]
        )
        b = matrix(
            [
                [1-w],
                [w]
            ]
        )
        m: matrix = a*self.m*b
        return v3.from_matrix(m.item(0,0))


if __name__ == "__main__":
    a = BilinearSurface()
    a.calculate(0,0)
