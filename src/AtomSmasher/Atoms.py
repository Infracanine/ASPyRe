import drawSvg.elements
import drawSvg as draw
import random
import re


r_int = lambda: random.randint(0, 255)


def get_random_colour():
    return '#%02X%02X%02X' % (r_int(), r_int(), r_int())

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

    # Given an atom instance, extract the arguments of this atom based on its regex
    def get_args(self, atom_instance: str, scaling=1):
        # Replace regex with capture group expression
        capture_regex = self.get_regex().replace("(", "((").replace("\)", ")\)").replace(",", "),(")
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


class RoadAtom(Atom):
    def __init__(self):
        self.regex = r"road\(\d*,\d*,\d*,\d*\)"
        self.name = "road"
        self.cardinality = 4

    def get_regex(self) -> str:
        return self.regex

    def get_name(self):
        return self.name

    # Possibly just make this return a tuple of points and the element to draw, maybe? Not sure if this'll work, but this
    # API definitely needs simplification
    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Line:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return draw.Line(x1 + x_adj, y1 + y_adj, x2 + x_adj, y2 + y_adj, stroke='grey', stroke_width=6)

    def get_order(self) -> int:
        return 4

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return [(x1, y1), (x2, y2)]


class MainRoadAtom(Atom):
    def __init__(self):
        self.regex = r"main_road\(\d*,\d*,\d*,\d*\)"
        self.name = "main_road"
        self.cardinality = 4

    def get_regex(self) -> str:
        return self.regex

    def get_name(self):
        return self.name

    # Possibly just make this return a tuple of points and the element to draw, maybe? Not sure if this'll work, but this
    # API definitely needs simplification
    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Line:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return draw.Line(x1 + x_adj, y1 + y_adj, x2 + x_adj, y2 + y_adj, stroke='grey', stroke_width=6)

    def get_order(self) -> int:
        return 4

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
        return draw.Circle(x + x_adj, y + y_adj, 2, fill="white", stroke_transparency=0)

    def get_order(self) -> int:
        return 7

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x = parameters[0]
        y = parameters[1]
        return [(x, y)]


class IngressPoint(Atom):
    def __init__(self):
        self.regex = r"ingress_point\(\d*,\d*\)"
        self.name = "ingress"
        self.cardinality = 2

    def get_regex(self) -> str:
        return self.regex

    def get_name(self) -> str:
        return self.name

    def get_order(self) -> int:
        return 6

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Circle:
        self.validate_cardinality(parameters, self.cardinality)
        x = parameters[0]
        y = parameters[1]
        return draw.Circle(x + x_adj, y + y_adj, 1, stroke="green")

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x = parameters[0]
        y = parameters[1]
        return [(x, y)]


class PlotAtom(Atom):
    def __init__(self):
        self.regex = r"plot\(\d*,\d*,\d*,\d*\)"
        self.name = "plot"
        self.cardinality = 4

    def get_regex(self) -> str:
        return self.regex

    def get_name(self):
        return self.name

    def get_order(self) -> int:
        return 0

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Rectangle:
        self.validate_cardinality(parameters, self.cardinality)
        margin = 1
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        width = x2 - x1 - (2 * margin)
        height = y2 - y1 - (2 * margin)
        return draw.Rectangle(x1 + x_adj + margin, y1 + y_adj + margin, width, height, fill='green',
                              stroke_transparency=0, fill_opacity=1)

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return [(x1, y1), (x2, y2)]


# Pick a few future features and draw them manually to indicate future work (e.g. housing)
class SubplotAtom(Atom):
    def __init__(self):
        self.regex = r"sub_plot\(\d*,\d*,\d*,\d*,\w+\)"
        self.name = "sub_plot"
        self.cardinality = 5

    def get_regex(self) -> str:
        return self.regex

    def get_name(self):
        return self.name

    def get_order(self) -> int:
        return 3

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Rectangle:
        self.validate_cardinality(parameters, self.cardinality)
        margin = 1
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        assignment = parameters[4]
        colour = ""
        if assignment == 'urban':
            colour = "#D3D3D3"
        elif assignment == "green_space":
            colour = 'green'
        width = x2 - x1 - (2 * margin)
        height = y2 - y1 - (2 * margin)
        return draw.Rectangle(x1 + x_adj + margin, y1 + y_adj + margin, width, height, fill=colour,
                              stroke_transparency=0, fill_opacity=1)

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return [(x1, y1), (x2, y2)]


class SideRoadAtom(Atom):
    def __init__(self):
        self.regex = r"side_road\(\d*,\d*,\d*,\d*\)"
        self.name = "side_road"
        self.cardinality = 4

    def get_regex(self) -> str:
        return self.regex

    def get_name(self):
        return self.name

    # Possibly just make this return a tuple of points and the element to draw, maybe? Not sure if this'll work, but this
    # API definitely needs simplification
    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.Line:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return draw.Line(x1 + x_adj, y1 + y_adj, x2 + x_adj, y2 + y_adj, stroke='grey', stroke_width=3)

    def get_order(self) -> int:
        return 4

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x1 = parameters[0]
        y1 = parameters[1]
        x2 = parameters[2]
        y2 = parameters[3]
        return [(x1, y1), (x2, y2)]


class SubIntersectAtom(Atom):
    def __init__(self):
        self.regex = r"sub_intersect\(\d*,\d*\)"
        self.name = "sub_intersect"
        self.cardinality = 2

    def get_regex(self) -> str:
        return self.regex

    def get_name(self) -> str:
        return self.name

    def draw(self, parameters: list, x_adj=0, y_adj=0) -> drawSvg.elements.DrawingBasicElement:
        self.validate_cardinality(parameters, self.cardinality)
        x = parameters[0]
        y = parameters[1]
        return draw.Rectangle(x + x_adj, y + y_adj, width=2, height=2, stroke="white")

    def get_order(self) -> int:
        return 5

    def get_points(self, parameters: list) -> list:
        self.validate_cardinality(parameters, self.cardinality)
        x = parameters[0]
        y = parameters[1]
        return [(x, y)]
