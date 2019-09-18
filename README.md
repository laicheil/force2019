# force2019

```bash
pip3 install --user --upgrade --editable .
laicheil.force2019.cli --help
laicheil.force2019.cli
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

## load data

```bash
laicheil.force2019.cli load_files --from force2019-data-000/data-000/
```

```
20190918T101939 iwana@iwana-ub.zoic.eu.org:~/d/github.com/laicheil
$ laicheil.force2019.cli load_files --from force2019-data-000/data-000/
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
