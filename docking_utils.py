#!/usr/bin/env python

import os
from subprocess import run
from tempfile import NamedTemporaryFile
import argparse

def lmap(f, l):
    return list(map(f, l))

def str2floats(s):
    return lmap(float, s.split(','))

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--seed', help='RNG seed', type=int, default=666)
    parser.add_argument('--smiles', type=str, default='O=C(O)c1cc(Nc2nccc(C3CCOC3)n2)cc(-c2nnco2)c1')
    parser.add_argument('--receptor', required=True)
    parser.add_argument('--box_center', required=True, type=str2floats)
    parser.add_argument('--box_size', required=True, type=str2floats)
    parser.add_argument('--vina_program', required=True)
    parser.add_argument('--exhaustiveness', type=int, default=8)
    parser.add_argument('--num_modes', type=int, default=10)
    parser.add_argument('--num_sub_proc', type=int, default=1)
    parser.add_argument('--n_conf', type=int, default=3)
    parser.add_argument('--error_val', type=float, default=99.9)
    parser.add_argument('--timeout_gen3d', type=int, default=None)
    parser.add_argument('--timeout_dock', type=int, default=None)
    return parser.parse_args()

def get_docking_config(args):
    docking_config = {
        'receptor': args.receptor,
        'box_center': args.box_center,
        'box_size': args.box_size,
        'vina_program': args.vina_program,
        'exhaustiveness': args.exhaustiveness,
        'num_sub_proc': args.num_sub_proc,
        'num_modes': args.num_modes,
        'timeout_gen3d': args.timeout_gen3d,
        'timeout_dock': args.timeout_dock,
        'seed': args.seed,
        'n_conf': args.n_conf,
        'error_val': args.error_val
    }

    return docking_config

class DockingVina:
    def __init__(self, config):
        self.config = config

    def __call__(self, smile):
        affinities = list()
        for i in range(self.config['n_conf']):
            os.environ['OB_RANDOM_SEED'] = str(self.config['seed'] + i)
            affinities.append(DockingVina.docking(smile, **self.config))
        return min(affinities)

    @staticmethod
    def docking(smile, *, vina_program, receptor, box_center,
                box_size, error_val, seed, num_modes, exhaustiveness,
                timeout_dock, timeout_gen3d, **kwargs):
        with NamedTemporaryFile(mode=('r+t')) as f1, NamedTemporaryFile(mode=('r+t')) as f2:
            ligand = f1.name
            docking_file = f2.name
            #run_line = 'obabel {} -xr -xn -xp -O {}qt'.format(receptor, receptor)
            #result = run(run_line.split(), capture_output=True, text=True, timeout=timeout_gen3d, env=os.environ)
            #receptor = receptor + 'qt'
            run_line = "obabel -:{} --gen3D -h -opdbqt -O {}".format(smile, ligand)
            result = run(run_line.split(), capture_output=True, text=True, timeout=timeout_gen3d, env=os.environ)
            try:
                result = run(run_line.split(), capture_output=True, text=True, timeout=timeout_gen3d, env=os.environ)
            except:
                return error_val

            if "Open Babel Error" in result.stdout or "3D coordinate generation failed" in result.stdout:
                return error_val

            run_line = vina_program
            run_line += " --receptor {} --ligand {} --out {}".format(receptor, ligand, docking_file)
            run_line += " --center_x {} --center_y {} --center_z {}".format(*box_center)
            run_line += " --size_x {} --size_y {} --size_z {}".format(*box_size)
            run_line += " --num_modes {}".format(num_modes)
            run_line += " --exhaustiveness {}".format(exhaustiveness)
            run_line += " --seed {}".format(seed)
            result = run(run_line.split(), capture_output=True, text=True, timeout=timeout_dock)
            try:
                result = run(run_line.split(), capture_output=True, text=True, timeout=timeout_dock)
            except:
                return error_val

            return DockingVina.parse_output(result.stdout, error_val)
    
    @staticmethod
    def parse_output(result, error_val):
        result_lines = result.split('\n')
        check_result = False
        affinity = error_val

        for result_line in result_lines:
            if result_line.startswith('-----+'):
                check_result = True
                continue
            if not check_result:
                continue
            if result_line.startswith('Writing output'):
                break
            if result_line.startswith('Refine time'):
                break
            lis = result_line.strip().split()
            if not lis[0].isdigit():
                break
            affinity = float(lis[1])
            break
        return affinity
