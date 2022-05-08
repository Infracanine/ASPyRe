import drawSvg.elements
import drawSvg as draw
import random
import re

# Interface for all instances of Atoms
# When attempting to visualise some answer set atom you must create a subclass of the Atom class and implement all empty methods
class Atom:
    # Get string representing the regex used for parsing this atom from raw answer set text
    def get_regex(self) -> str:
        pass

    # Plain language name for this atom, if not overridden returns class name
    def get_name(self) -> str:
        return self.__class__.get_name()

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.DrawingBasicElement:
        pass

    def get_points(self, parameters: list) -> list:
        pass

    # Given an atom instance, extract the arguments of this atom based on its regex
    def get_args(self, atom_instance: str, scaling=1):
        # Replace regex with capture group expression
        capture_regex = self.get_regex().replace("(", "((").replace("\\)", ")\\)").replace(",", "),(")
        matcher = re.compile(capture_regex)
        capture = matcher.search(atom_instance)
        output = []
        for each in capture.groups():
            try:
                i = int(each)
                output.append(i * scaling)
            except ValueError as e:
                output.append(each)
        return output

    # Order of atom which dictates the order atoms are rendered in. Higher atoms are drawn later, i.e. are drawn on top
    # Defaults to zero if not overridden
    def get_order(self) -> int:
        return 0

    # Helper method for validating that some input matches the arity/cardinality of this atom
    def validate_cardinality(self, parameters: list, cardinality: int):
        if len(parameters) != cardinality:
            raise Exception(
                    f"Received {len(parameters)} attempting to draw the {self.get_name()} atom. Expected {cardinality}.")
