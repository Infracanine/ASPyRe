from datetime import datetime
import atoms.Atoms as Atoms
import drawSvg as draw
import sys
import getopt
import os.path
import re
import inspect

canvas_width: int = 500
canvas_height: int = 500
canvas_centroid = (canvas_width / 2, canvas_height / 2)
title_font_size = canvas_height / 50
body_font_size = title_font_size * 0.8
PIXEL_SCALE = 1

boundary_pattern: str = r"boundary\(\d*,\d*,\d*,\d*\)"
road_pattern: str = r"road\(\d*,\d*,\d*,\d*\)"
# Dictionary mapping an atom's pattern to a corresponding SVG object
atom_dict = dict()

# #
# # def create_environment():
# #
# def draw(output_file):
#     # Origin is bottom left
#     d = draw.Drawing(100, 100, origin=(0, 0), displayInline=False)
#     d.append(draw.Rectangle(0, 0, 1000, 1000, fill="#378805"))
#
#     d.setPixelScale(1)
#
#     # Create some transport routes
#     r = Road(0, 0, 40, 40)
#
#     d.savePng(output_file)


def load_atoms():
    print("Loading defined atoms from Atoms module.")
    for name, obj in inspect.getmembers(Atoms):
        if obj is not Atoms.Atom and isinstance(obj, type) and issubclass(obj, Atoms.Atom):
            instance = obj()
            atom_dict[instance.get_regex()] = instance


def extract_answer_sets(clingo_output: str) -> (str, list):
    if "SATISFIABLE" not in clingo_output:
        raise Exception("Received non-satisfiable answer set.")
    # Extract answer sets from Clingo text output
    split = re.split(r"SATISFIABLE|Answer: \d*", clingo_output.replace("\n", " "))
    metadata = split[0]
    answer_sets = split[1:-1]
    return metadata, answer_sets


def extract_atoms(answer_set):
    return re.split("\s", answer_set.strip())


def calculate_centroid(render_points: list):
    xs = []
    ys = []
    for x, y in render_points:
        xs.append(x)
        ys.append(y)
    x_centroid = sum(xs) / len(xs)
    y_centroid = sum(ys) / len(ys)
    return x_centroid, y_centroid


# Do rendering in a better, object oriented way using a dictionary of objects mapping a regex to <something>
def render_answer_set(drawing: draw.Drawing, answer_set: str, title: str):
    # Draw background of image
    drawing.append(draw.Rectangle(0, 0, canvas_width, canvas_height, fill="white"))
    drawing.setPixelScale(PIXEL_SCALE)
    # Create objects list for pre-processing purposes
    points_set = set()

    print(f"Raw Clingo string to render: {answer_set}")
    atoms = extract_atoms(answer_set)
    print(f"Identified {len(atoms)} atoms, performing pre-processing.")
    # Calculate centroid of all mapped atoms
    for atom in atoms:
        matched = False
        for pattern in atom_dict.keys():
            if re.match(pattern, atom):
                # Extract all numbers and convert to int
                matches = [int(x) for x in re.findall(r"\d+", atom)]
                # Store points in a set for later centroid calculation
                for point in atom_dict[pattern].get_points(matches):
                    points_set.add(point)
                matched = True
                break
        if not matched:
            atoms.remove(atom)
            print(f"Unmapped atom pattern found! Pattern was {atom}")
    # Perform adjustment calculation
    centroid_x, centroid_y = calculate_centroid(list(points_set))
    x_adj = canvas_centroid[0] - centroid_x
    y_adj = canvas_centroid[1] - centroid_y

    # Draw all atoms on canvas
    for atom in atoms:
        for pattern in atom_dict.keys():
            # Maybe implement something so we don't have to perform matching a second time
            if re.match(pattern, atom):
                # Convert matches to integers
                matches = [int(x) for x in re.findall(r"\d+", atom)]
                svg_object = atom_dict[pattern].draw(matches, x_adj, y_adj)
                drawing.append(svg_object)
                break
    drawing.append(draw.Text(title, fontSize=title_font_size, x=5, y=canvas_width - title_font_size))
    drawing.append(draw.Text("Atoms:" + answer_set.replace(" ", "\n"), fontSize=9, x=5, y=canvas_height * 0.8))
    print(f"Rendered {title}")
    return drawing


def validate_parameters(input_param, output_param):
    print(f'Input file is "{input_param}"')
    print(f'Output directory is "{output_param}"')
    if input_param == "" or not os.path.exists(input_param):
        raise IOError(f"Could not find input file '{input_param}'")
    if output_param == "" or not os.path.exists(output_param):
        raise IOError(f"Could not find output dir '{output_param}'")


# Calculate name of directory to store rendered artifacts in
def generate_directory_name():

    dt = datetime.now().strftime("%d-%m-%Y-%H%M")
    directory = f"outputs/Output-{dt}"
    # Handle case where we've already created a directory with this name.
    # Generally this happens if  we've executed pyviz twice in the same minute
    if os.path.exists(directory):
        print("Default path already existed!")
        count = 1
        new_dir = f"{directory}[{count}]"
        while os.path.exists(new_dir):
            count += 1
            new_dir = f"{directory}[{count}]"
        directory = new_dir
    return directory


'''
Main Pyviz script for visualising the output of Clingo
Accept the text output of a Clingo execution, typically something like:

    clingo version 5.4.0
    Reading from ...project_source/more_experimentation.lp
    Solving...
    Answer: 1
    boundary(0,0,10,0) boundary(10,0,10,10) boundary(10,10,0,10) boundary(0,10,0,0)
    SATISFIABLE
    
    Models       : 1
    Calls        : 1
    Time         : 0.006s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
    CPU Time     : 0.001s

And outputs pngs based on user defined classes in the Atoms module
'''


def main(argv):
    input_file = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "odir="])
    except getopt.GetoptError:
        print('pyviz.py -i <inputfile> -o <outputdirectory>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('pyviz.py -i <inputfile> -o <outputdirectory>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--odir"):
            output_file = arg
    try:
        validate_parameters(input_file, output_file)
    except IOError as err:
        print("IO error: {0}".format(err))
        return
    # Open file
    with open(input_file) as f:
        input_contents = f.read()
    if input_contents == "":
        print("Input file was empty, exiting pyviz")
        return
    # Load user defined Atom classes from atoms module
    load_atoms()
    # Validate input text file is correct format
    print("------------Input file------------")
    print(input_contents)
    print("----------------------------------")
    metadata, answer_sets = extract_answer_sets(input_contents)
    print(f"Extracted {len(answer_sets)} answer sets\n")
    # Calculate name of directory to store rendered artifacts in
    directory = generate_directory_name()
    os.mkdir(directory)
    answer_set_count = 0
    # Iterate through all identified answer sets and render that output
    for each in answer_sets:
        answer_set_count += 1
        d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
        render_answer_set(d, each, f"Answer Set {answer_set_count}")
        full_path = f"{directory}/AnswerSet{answer_set_count}.png"
        print(f"Attempting to save artefact to {full_path}")
        d.savePng(full_path)
    print(f"COMPLETE: Successfully rendered {answer_set_count} answer sets!")


if __name__ == '__main__':
    main(sys.argv[1:])
