virenv:
	sudo apt-get update
	sudo apt install -y build-essential cmake pkg-config libjpeg-dev libtiff5-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev libhdf5-serial-dev libhdf5-103 libqt5gui5 libqt5webkit5 libqt5test5 python3-pyqt5 python3-dev
	sudo apt-get install libopenblas-dev
	python3 -m venv .future-engineer-env 

install:
	pip install --upgrade pip setuptools wheel
	pip install -e .
	git submodule add git@github.com:niru-5/imusensor.git _deps/imusensor
	git submodule update --init --remote
	pip install -r _deps/imusensor/requirements.txt
	pip install -e _deps/imusensor