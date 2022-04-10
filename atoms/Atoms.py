import drawSvg.elements
import drawSvg as draw


# Interface for all instances of Atoms
class Atom:
    def get_regex(self) -> str:
        pass

    def get_name(self) -> str:
        pass

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.DrawingBasicElement:
        pass

    def get_points(self, parameters: list) -> list:
        pass


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
        if len(parameters) != self.cardinality:
            raise Exception(f"Received {len(parameters)} attempting to draw the {self.get_name()} atom. Expected {self.cardinality}.")
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return draw.Line(x1 + x_adj, y1 + y_adj, x2 + x_adj, y2 + y_adj, stroke='grey', stroke_width=5)

    def get_points(self, parameters: list) -> list:
        if len(parameters) != self.cardinality:
            raise Exception(f"Received {len(parameters)} attempting to extract coords for the {self.get_name()} atom. Expected {self.cardinality}.")
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
        if len(parameters) != self.cardinality:
            raise Exception(f"Received {len(parameters)} attempting to draw the {self.get_name()} atom. Expected {self.cardinality}.")
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return draw.Line(x1 + x_adj, y1 + y_adj, x2 + x_adj, y2 + y_adj, stroke='red', stroke_width=2)

    def get_points(self, parameters: list) -> list:
        if len(parameters) != self.cardinality:
            raise Exception(f"Received {len(parameters)} attempting to extract coords for the {self.get_name()} atom. Expected {self.cardinality}.")
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return [(x1, y1), (x2, y2)]
