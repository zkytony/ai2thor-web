from setuptools import setup, find_packages
import thortils

setup(name='ai2thor-web',
      packages=find_packages(),
      version='0.1',
      description='Ai2thor in browser',
      install_requires=[
          'numpy',
          'scipy',
          'pandas',
          'matplotlib',
          'ai2thor=={}'.format(thortils.AI2THOR_VERSION),
          'flask',
          'bootstrap-flask',
          'SQLAlchemy',
          'Flask-SQLAlchemy',
          'flask-migrate'
      ])
