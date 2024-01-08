# -*- coding: utf-8 -*-

from dataclasses import dataclass

from tritonoa.at.env.array import Receiver, Source


@dataclass
class Ray:
    r: list[float]
    z: list[float]
    launch_angle: float
    num_top_bounce: int
    num_bot_bounce: int


@dataclass
class RayFan:
    rays: list[Ray]


class Beams:
    def __init__(self, source: Source, receiver: Receiver) -> None:
        self.source = source
        self.receiver = receiver

    def read_beams(self, rayfil: str) -> str:
        self.rayfil = f"{rayfil}.ray"

        with open(self.rayfil, "rb") as f:
            self.title = f.readline().decode("utf-8").strip()[1:-1].strip()
            self.freq = float(f.readline().decode("utf-8").strip())
            Nsxyz = [int(i) for i in f.readline().decode("utf-8").strip().split()]
            NBeamAngles = [int(i) for i in f.readline().decode("utf-8").strip().split()]
            self.depth_top = float(f.readline().decode("utf-8").strip())
            self.depth_bot = float(f.readline().decode("utf-8").strip())
            self.type = f.readline().decode("utf-8").strip()[1:-1].strip()
            self.num_sx = Nsxyz[0]
            self.num_sy = Nsxyz[1]
            self.num_sz = Nsxyz[2]
            self.num_beams = NBeamAngles[0]

            sources = []
            for i in range(self.num_sz):
                rays = []
                for j in range(self.num_beams):
                    raw_alpha0 = f.readline().decode("utf-8").strip()
                    if not raw_alpha0:
                        sources.append(rays)
                        break
                    alpha0 = float(raw_alpha0)
                    ray_metadata = f.readline().decode("utf-8").strip().split()
                    num_steps = int(ray_metadata[0])
                    num_top_bounce = int(ray_metadata[1])
                    num_bot_bounce = int(ray_metadata[2])
                    if self.type == "rz":
                        raw_ray_data = [f.readline() for _ in range(num_steps)]
                        ray_data = [
                            i.decode("utf-8").strip().split() for i in raw_ray_data
                        ]
                        ranges = [float(i[0]) for i in ray_data]
                        depths = [float(i[1]) for i in ray_data]
                    if self.type == "xyz":
                        pass

                    rays.append(
                        Ray(ranges, depths, alpha0, num_top_bounce, num_bot_bounce)
                    )
                else:
                    sources.append(rays)
                    continue
                break

            self.sources = sources
            return self.rayfil
