from importlib import import_module
from src.AtomSmasher import Atoms
from src.mylogging import MyLogger
import inspect


def import_user_mappings(user_mappings_loc: str):
    return import_module(user_mappings_loc)


def format_file_name(file_str: str):
    output = file_str
    if "/" in file_str:
        output = output.replace("/", ".")
    if ".py" in output:
        output = output.replace(".py","")
    return output


class AtomImporter:
    def __init__(self, logger: MyLogger):
        self.logger = logger
    # Load atoms from user inputted file

    def load_atoms(self, atoms_file: str):
        self.logger.log(f"Attempting to load atoms from {atoms_file}.")
        atoms_file = format_file_name(atoms_file)
        print(atoms_file)
        return_dict = dict()
        atoms_module = import_user_mappings(atoms_file)
        for name, obj in inspect.getmembers(atoms_module):
            if obj is not Atoms.Atom and isinstance(obj, type) and issubclass(obj, Atoms.Atom):
                instance = obj()
                self.logger.log(f"Successfully loaded Atom {name}")
                return_dict[instance.get_regex()] = instance
        self.logger.log(f"Completed Atom mapping import successfully! Loaded {len(return_dict)} Atoms.")
        return return_dict
