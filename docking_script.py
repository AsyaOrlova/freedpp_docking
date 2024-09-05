from docking_utils import DockingVina, parse_args, get_docking_config
from operator import methodcaller

args = parse_args()
smiles = args.smiles
args.docking_config = get_docking_config(args)

f = methodcaller('__call__', smiles)
docking_score = f(DockingVina(args.docking_config))

print(docking_score)