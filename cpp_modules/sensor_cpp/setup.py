from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "sensor_cpp",
        ["sensor.cpp"],
        cxx_std=17,
    ),
]

setup(
    name="sensor_cpp",
    ext_modules=ext_modules,
    cmdclass={"build_ext" : build_ext},
    # 테스트 의존성 추가
    extras_require ={
        "test" : ["pytest"],
    }
)