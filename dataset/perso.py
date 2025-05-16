from docplex.mp.model import Model
from docplex.mp.model_reader import ModelReader
import os

from solver.problem import Problem

def load_perso():
    problems = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    dir = f"{current_dir}/sources/perso_bpsc_train"
    print(f"Loading problems from {dir}...")
    for f in os.listdir(dir):
        model : Model = ModelReader.read(f"{dir}/{f}")
        prob = Problem.from_model(model)
        problems.append(prob)
    return problems
if __name__ == "__main__":
    load_perso()