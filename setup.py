from setuptools import setup, find_packages

setup(name='ai2thor-web',
      packages=find_packages(),
      version='0.1',
      description='Ai2thor in browser',
      install_requires=[
          'numpy',
          'scipy',
          'pandas',
          'matplotlib',
          'ai2thor',
          'flask',
          'bootstrap-flask',
          'SQLAlchemy',
          'Flask-SQLAlchemy',
          'flask-migrate'
      ])
