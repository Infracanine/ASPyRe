import drawSvg.elements
import drawSvg as draw


# Interface for all instances of Atoms
# When attempting to visualise some answer set atom you must create a subclass of the Atom class and define a mapping
# From the base atom to a drawing element, and what coordinates
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

    # Order of atom which dictates the order atoms are rendered in. Higher atoms are drawn later, i.e. are drawn on top
    def get_order(self) -> int:
        return 0

    def validate_cardinality(self, parameters: list, cardinality: int):
        if len(parameters) != cardinality:
            raise Exception(f"Received {len(parameters)} attempting to draw the {self.get_name()} atom. Expected {cardinality}.")


class RoadAtom(Atom):
    def __init__(self):
        self.regex = r"road\(\d*,\d*,\d*,\d*\)"
        self.name = "road"
        self.cardinality = 4

    def get_regex(self) -> str:
        return self.regex

    def get_name(self):
        return self.name

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Line:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return draw.Line(x1 + x_adj, y1 + y_adj, x2 + x_adj, y2 + y_adj, stroke='grey', stroke_width=5)

    def get_order(self) -> int:
        return 1

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return [(x1, y1), (x2, y2)]


class BoundaryAtom(Atom):
    def __init__(self):
        self.regex = r"boundary\(\d*,\d*,\d*,\d*\)"
        self.name = "boundary"
        self.cardinality = 4

    def get_regex(self) -> str:
        return self.regex

    def get_name(self):
        return self.name

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Line:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return draw.Line(x1 + x_adj, y1 + y_adj, x2 + x_adj, y2 + y_adj, stroke='red', stroke_width=2)

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return [(x1, y1), (x2, y2)]


class IntersectAtom(Atom):
    def __init__(self):
        self.regex = r"intersect\(\d*,\d*\)"
        self.name = "intersect"
        self.cardinality = 2

    def get_regex(self) -> str:
        return self.regex

    def get_name(self) -> str:
        return self.name

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.DrawingBasicElement:
        self.validate_cardinality(parameters, self.cardinality)
        x = parameters[0]
        y = parameters[1]
        return draw.Circle(x + x_adj, y + y_adj, 1, stroke="blue")

    def get_order(self) -> int:
        return 2

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x = parameters[0]
        y = parameters[1]
        return [(x, y)]
