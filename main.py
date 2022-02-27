from datetime import datetime

import drawSvg as draw
import sys
import getopt
import os.path
import re


canvas_width: int = 500
canvas_height: int = 500
boundary_pattern: str = r"boundary\(\d*,\d*,\d*,\d*\)"
road_pattern: str = r"road\(\d*,\d*,\d*,\d*\)"
city_object_list: list = []


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


'''
Accept the text output of a Clingo execution, typically something like:
---
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
---
And returns a tuple containing the metadatas string and an  array of the string representation of each answer set in the output
'''
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


def render(drawing: draw.Drawing, answer_set: str, title: str):
    drawing.append(draw.Rectangle(0, 0, canvas_width, canvas_height, fill="white"))
    drawing.setPixelScale(1)
    # Create objects list for pre-processing purposes
    objects_list = []
    print(f"Raw Clingo string to render: {answer_set}")
    atoms = extract_atoms(answer_set)
    print(f"Identified {len(atoms)} atoms, performing pre-processing.")
    for each in atoms:
        if re.match(road_pattern, each):
            matches = re.findall(r"\d+", each)
            x1, y1, x2, y2 = int(matches[0]), int(matches[1]), int(matches[2]), int(matches[3])
            objects_list.append(("road", [x1, y1, x2, y2]))
            # print(f"Road at ({x1},{y1}) ({x2},{y2})")
        elif re.match(boundary_pattern, each):
            matches = re.findall(r"\d+", each)
            x1, y1, x2, y2 = int(matches[0]), int(matches[1]), int(matches[2]), int(matches[3])
            objects_list.append(("boundary", [x1, y1, x2, y2]))
            # print(f"Boundary at ({x1},{y1}) ({x2},{y2})")
        else:
            print(f"Unexpected atom pattern found! Pattern was {each}")
    # Center city on canvas by calculating centroid and adjusting position of elements in the answer set
    canvas_centroid = (canvas_width / 2, canvas_height / 2)
    summed_x = 0
    summed_y = 0
    points_count = 0
    # TODO: Sort this so points in the same place do not both contribute to centroid calculation, thus resulting in wonky centralisation
    for city_obj_type, coordinates in objects_list:
        if city_obj_type == "road" or city_obj_type == "boundary":
            points_count += 2
            summed_x += coordinates[0]
            summed_x += coordinates[2]
            summed_y += coordinates[1]
            summed_y += coordinates[3]
        else:
            print("Unrecognised city object type!")
    city_centroid_x = summed_x / points_count
    city_centroid_y = summed_y / points_count
    x_adj = canvas_centroid[0] - city_centroid_x
    y_adj = canvas_centroid[1] - city_centroid_y
    for city_obj_type, coordinates in objects_list:
        if city_obj_type == "road":
            drawing.append(draw.Line(coordinates[0] + x_adj, coordinates[1] + y_adj, coordinates[2] + x_adj, coordinates[3] + y_adj, stroke='grey', stroke_width=5))
        elif city_obj_type == "boundary":
            drawing.append(draw.Line(coordinates[0] + x_adj, coordinates[1] + y_adj, coordinates[2] + x_adj, coordinates[3] + y_adj, stroke='red', stroke_width=2))
    title_font_size = canvas_height / 50
    drawing.append(draw.Text(title, fontSize=title_font_size, x=5, y=canvas_width - title_font_size))
    drawing.append(draw.Text(answer_set, fontSize=9, x=10, y=10))
    print(f"Rendered {title}")
    return drawing


def validate_parameters(input_param, output_param):
    print(f'Input file is "{input_param}"')
    print(f'Output directory is "{output_param}"')
    if input_param == "" or not os.path.exists(input_param):
        raise IOError(f"Could not find input file '{input_param}'")
    if output_param == "" or not os.path.exists(output_param):
        raise IOError(f"Could not find output dir '{output_param}'")


# Main Pyviz script
# Answer Set visualisation tool, to turn ASP representation of urban plans into svg image
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
    # Validate input text file is correct format
    print("------------Input file------------")
    print(input_contents)
    print("----------------------------------")
    metadata, answer_sets = extract_answer_sets(input_contents)
    print(f"Extracted {len(answer_sets)} answer sets\n")
    # Do Drawing (for the moment just render the first one)
    dt = datetime.now().strftime("%d-%m-%Y-%H%M")
    directory = f"Output-{dt}"
    os.mkdir("outputs/" + directory)
    number = 0
    # Iterate through all identified answer sets and render that output
    for each in answer_sets:
        number += 1
        d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
        render(d, each, f"Answer Set {number}")
        d.savePng(f"outputs/{directory}/AnswerSet{number}.png")
    print(f"COMPLETE: Successfully rendered {number} answer sets!")


if __name__ == '__main__':
    main(sys.argv[1:])


