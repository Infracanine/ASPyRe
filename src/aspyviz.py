from datetime import datetime
from src.AtomSmasher.AtomImporter import AtomImporter
import argparse
import drawSvg as draw
import os.path
import re
import sys
from src.logging import mylogging as mylogs
import time

# Statics
canvas_width: int = 500
canvas_height: int = 500
canvas_centroid = (canvas_width / 2, canvas_height / 2)
title_font_size = canvas_height / 50
body_font_size = title_font_size * 0.8
PIXEL_SCALE = 1
RENDER_SCALING = 10

# Instantiate logger
logger = mylogs.MyLogger()


# Stores a copy of the answer set input file alongside generated artefacts
def write_raw_clingo_to_file(raw_answer_set: str, directory: str):
    with open(f'{directory}/raw_pyviz_input.txt', 'w') as f:
        f.write(raw_answer_set)


# Extract individual answers sets from raw text output of Clingo
def extract_models(clingo_output: str) -> (str, list):
    if "SATISFIABLE" not in clingo_output:
        raise Exception("Received non-satisfiable answer set.")
    # Extract answer sets from Clingo text output
    split = re.split(r"SATISFIABLE|Answer: \d*", clingo_output.replace("\n", " "))
    metadata = split[0]
    answer_sets = split[1:-1]
    return metadata, answer_sets


# Split an answer set string into substrings representing individual atoms
def extract_atoms(model):
    return re.split("\s", model.strip())


# Calculate the approximate center of the artefact
def calculate_centroid(render_points: list):
    xs = []
    ys = []
    for x, y in render_points:
        xs.append(x)
        ys.append(y)
    x_centroid = sum(xs) / len(xs)
    y_centroid = sum(ys) / len(ys)
    return x_centroid, y_centroid


def render_model(atom_dict: dict, drawing: draw.Drawing, answer_set: str, title: str, scaling: int = 1, render_atom_text = False, verbosity = False):
    # Draw background of image
    drawing.append(draw.Rectangle(0, 0, canvas_width, canvas_height, fill="white"))
    drawing.setPixelScale(PIXEL_SCALE)
    # Create objects list for pre-processing purposes
    points_set = set()
    if verbosity:
        logger.log(f"Raw Clingo string to render: {answer_set}")
    atoms = extract_atoms(answer_set)
    logger.log(f"Identified {len(atoms)} atoms, performing pre-processing.")
    atoms_and_orders = []
    # Calculate centroid of all mapped atoms
    for atom in atoms:
        matched = False
        for pattern in atom_dict.keys():
            if re.match(pattern, atom):
                # Extract all numbers and convert to int
                matches = atom_dict[pattern].get_args(atom, scaling)
                # Store points in a set for later centroid calculation
                for point in atom_dict[pattern].get_points(matches):
                    points_set.add(point)
                atoms_and_orders.append([atom, atom_dict[pattern], matches])
                matched = True
                break
        if not matched:
            logger.log(f"Unmapped atom pattern found! Pattern was {atom}")
    # Perform adjustment calculation
    centroid_x, centroid_y = calculate_centroid(list(points_set))
    x_adj = canvas_centroid[0] - centroid_x
    y_adj = canvas_centroid[1] - centroid_y

    # Sort atoms prior to processing based on order
    atoms_and_orders.sort(key=lambda x: x[1].get_order())
    # Draw all atoms on canvas
    for each in atoms_and_orders:
        atom, atom_class, matches = each[0], each[1], each[2]
        svg_object = atom_class.draw(matches, x_adj, y_adj)
        drawing.append(svg_object)
    drawing.append(draw.Text(title, fontSize=title_font_size, x=5, y=canvas_width - title_font_size))
    if render_atom_text:
        drawing.append(draw.Text("Atoms:" + answer_set.replace(" ", "\n"), fontSize=9, x=5, y=canvas_height * 0.8))
    return drawing


# Initial validation of parameters passed to command line tool
def validate_io_parameters(input_param, output_param):
    logger.log(f'Input file is "{input_param}"')
    logger.log(f'Output directory is "{output_param}"')
    if input_param == "" or not os.path.exists(input_param):
        raise IOError(f"Could not find input file '{input_param}'")
    if output_param == "" or not os.path.exists(output_param):
        raise IOError(f"Could not find output dir '{output_param}'")


# Determine name of directory to store rendered artifacts in
def generate_directory_name(title: str, root_dir: str):
    dt = datetime.now().strftime("%d-%m-%Y-%H%M")
    directory = root_dir + "/"
    if title != "":
        directory += f"{title}-{dt}"
    else:
        directory += f"PyVizOutput-{dt}"
    # Handle case where we've already created a directory with this name.
    # Generally this happens if  we've executed pyviz multiple times in a short amount of time
    directory = directory.replace(" ", "")
    if os.path.exists(directory):
        logger.log("Default path already existed!")
        count = 1
        new_dir = f"{directory}[{count}]"
        while os.path.exists(new_dir):
            count += 1
            new_dir = f"{directory}[{count}]"
        directory = new_dir
    return directory


def pyviz_parser_factory():
    my_parser = argparse.ArgumentParser(prog="PyViz", description="ASPyViz, a tool for visualising Answer Sets produced by CLINGO")
    my_parser.add_argument("input_file", type=str,
                           help="Specify the input file for PyViz, which should be a .txt")
    my_parser.add_argument("output_dir", type=str,
                           help="Specify the directory to output artefacts.")
    my_parser.add_argument("mapping_file", type=str,
                           help="Specify Python file containing atom mappings.")
    my_parser.add_argument("-W", "--canvas_width",
                           type=int,
                           help="Specify the width of the canvases images generated")
    my_parser.add_argument("-H", "--canvas_height",
                           type=int,
                           help="Specify the height of the canvases images generated")
    my_parser.add_argument("-a", "--show_atom_text",
                           action='store_true',
                           help="Set if you wish to show the string representation of atoms rendered alongside each corresponding artefact.")
    my_parser.add_argument("-t", "--title",
                           type=str,
                           help="Optional argument, specifying a title for the Answer Set being processed. "
                                "This will be reflected in the name of the output folder created.")
    my_parser.add_argument("-v", "--verbose",
                           action='store_true',
                           help="Configure verbosity of logging for ASPyViz.")
    return my_parser


# Extract models from Clingo output
def parse_clingo_output_file(input_file: str, output_dir: str):
    with open(input_file) as f:
        input_contents = f.read()
    if input_contents == "":
        logger.log("Input file was empty, exiting pyviz")
        return
    metadata, models = extract_models(input_contents)
    print(output_dir)
    logger.log(f"Extracted {len(models)} models from file {input_file}")
    print("Contents:" + input_contents)
    write_raw_clingo_to_file(raw_answer_set=input_contents, directory=output_dir)
    return metadata, models


# Takes a list of models, represented as strings, and renders them in the given directory
def render_models(models: list,
                  render_dir: str,
                  atom_dict: dict,
                  render_atom_text: bool,
                  title=""):
    model_count = 0
    start_time = time.time()
    for each in models:
        model_count += 1
        d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
        subtitle = (title + " ") if title != "" else ""

        subtitle += f"Answer Set {model_count}"
        render_model(drawing=d, answer_set=each, title=subtitle, atom_dict=atom_dict, scaling=RENDER_SCALING, render_atom_text=render_atom_text)
        full_path = f"{render_dir}/AnswerSet{model_count}.png"
        logger.log(f"Saved {subtitle} to '{full_path}'")
        d.savePng(full_path)
    execution_time = time.time() - start_time
    logger.log(f"COMPLETE: Successfully rendered {model_count} answer sets in {float('%.5g' % execution_time)} seconds!")


'''
Accept the text output of a Clingo execution, typically something like:

    clingo version 5.4.0
    Reading from ...project_source/experimentation.lp
    Solving...
    Answer: 1
    boundary(0,0,10,0) boundary(10,0,10,10) boundary(10,10,0,10) boundary(0,10,0,0)
    SATISFIABLE
    
    Models       : 1
    Calls        : 1
    Time         : 0.006s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
    CPU Time     : 0.001s
'''


# Main function, primarily concerned with argument parsing for the command line tool, and feeding these to our function
# Which parses Clingo output into a set of models, and then renders the models
def main(argv):
    # Parse arguments
    parser = pyviz_parser_factory()
    args = parser.parse_args(argv)
    input_file = args.input_file
    output_dir = args.output_dir
    mapping_file = args.mapping_file
    raw_title = args.title
    render_atom_text = args.show_atom_text
    if raw_title is None:
        raw_title = ""
    verbose = args.verbose
    if verbose:
        logger.log("Running in verbose mode!")
    try:
        validate_io_parameters(input_file, output_dir)
    except IOError as err:
        logger.log("IO error: {0}".format(err))
        return
    atom_importer = AtomImporter(logger)
    atom_dict = atom_importer.load_atoms(mapping_file)
    # Extract metadata and models from the clingo file
    render_directory = generate_directory_name(raw_title, output_dir)
    os.mkdir(render_directory)
    metadata, models = parse_clingo_output_file(input_file, render_directory)
    # Render models
    render_models(models, output_dir, atom_dict, render_atom_text, raw_title)

    # Print time to 5 significant figures


if __name__ == '__main__':
    main(sys.argv[1:])
