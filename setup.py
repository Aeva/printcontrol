from setuptools import setup

setup(name="printcontrol",
      version="zero",
      description="",
      url="https://github.com/Aeva/printcontrol",
      author="Aeva Palecek",
      author_email="aeva.ntsc@gmail.com",
      license="GPLv3",
      packages=["printcontrol"],
      zip_safe=False,

      entry_points = {
        "console_scripts" : [
            "printcontrol=printcontrol.main:main",
            ],
        },

      install_requires = [
        "PyGObject",
        ])
