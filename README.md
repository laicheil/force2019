# force2019

```bash
## run this to install module symlink
## (so it can be used from anywhere, don't have to be in directory)
pip3 install --user --upgrade --editable .
laicheil.force2019.cli --help

# windows
laicheil.force2019.cli stage-one --skip-weights --eval-k --from ..\force2019-data-000\data-000\

# linux
rm -rf var/tbg/
laicheil.force2019.cli stage-one --skip-weights --epochs 1 --batch-size 1 --steps-per-epoch 1 --eval-k --from ../force2019-data-000/data-000/
tensorboard --logdir var/tbg/
# http://localhost:6006/
```

```bash
## run without installing ...
python -m src.laicheil.force2019.cli
```

```
!pip3 install --no-cache-dir --upgrade git+https://github.com/laicheil/force2019.git@master
from laicheil.force2019 import something
something()
```

```
!pip3 install --no-cache-dir --upgrade git+https://github.com/laicheil/force2019.git@master
!laicheil.force2019.cli
```

## run from git in colab

Go to https://colab.research.google.com

Then first time run

```bash
!git clone https://github.com/laicheil/force2019.git
!git clone https://github.com/laicheil/force2019-data-000.git
!pip3 install --user --upgrade --editable force2019
```

Clear data

```bash
!rm -vr var/ # clear data
```

Run every iteration:

```bash
# get code
!git -C force2019 pull
!git -C force2019-data-000 pull
# run ...
!python3 -m laicheil.force2019.cli --vardir var/ stage-one --epochs 1 --eval-k --from force2019-data-000/data-000/
```

```
from tensorboardcolab import TensorBoardColab
tbc=TensorBoardColab(graph_path='var/tbg')
```

```bash
!python3 -m laicheil.force2019.cli stage-one --epochs 1 force2019-data-000/data-000/
!python3 -m laicheil.force2019.cli stage-one --epochs 1 --eval-k force2019-data-000/data-000/
!python3 -m laicheil.force2019.cli stage-one --from force2019-data-000/data-000/
```

## load data

```bash
laicheil.force2019.cli stage-one --from force2019-data-000/data-000/
```

```
20190918T101939 iwana@iwana-ub.zoic.eu.org:~/d/github.com/laicheil
$ laicheil.force2019.cli stage-one --from force2019-data-000/data-000/
2019-09-18T10:19:42 27444 7f2ac3a67680 020:INFO     laicheil.force2019.cli cli:83:main start ...
2019-09-18T10:19:42 27444 7f2ac3a67680 020:INFO     laicheil.force2019.cli cli:45:load_files labels shape (200,)
2019-09-18T10:19:42 27444 7f2ac3a67680 020:INFO     laicheil.force2019.cli cli:46:load_files data shape (200, 40, 39, 1)
```

## ...

```
20190918T092055 iwana@iwana-ub.zoic.eu.org:~/d/github.com/laicheil/force2019
$ laicheil.force2019.cli --help
usage: laicheil.force2019.cli [-h] [--version] [-v]

optional arguments:
  -h, --help     show this help message and exit
  --version      show program's version number and exit
  -v, --verbose  increase verbosity level
20190918T092056 iwana@iwana-ub.zoic.eu.org:~/d/github.com/laicheil/force2019
$ laicheil.force2019.cli
2019-09-18T09:20:59 9466 7feac9aa9680 020:INFO     laicheil.force2019.cli cli:58:main start ...
```

```
!pip3 install --no-cache-dir --upgrade laicheil.force2019
```

```
laicheil.force2019.cli stage-one --skip-weights --from ../force2019-data-000/data-000/
laicheil.force2019.cli stage-one --skip-weights --epochs 1 --from ../force2019-data-000/data-000/
```
