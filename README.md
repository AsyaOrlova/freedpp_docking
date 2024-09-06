# Docking script

## Installation
```conda install -c conda-forge openbabel```

```chmod 755 qvina02```

## Usage
```python docking_script.py --smiles "O=C(O)c1cc(Nc2nccc(C3CCOC3)n2)cc(-c2nnco2)c1" --receptor 3fqs.pdb --box_center "0.739,1.018,12.059" --box_size "21.846,22.098,18.886" --vina_program ./qvina02```

**smiles** - сгенерированная молекула

**receptor** - белок в формате .pdb (предоставляется пользователем)

**box_center, box_size** - координаты центра связывания и его размеры (предоставляются пользователем)

**vina_program** - путь к программе для докинга
