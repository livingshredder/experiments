import graphviz
import itertools

colour_map = {
    "green": "#ddc94c",
    "orange": "#e36e42",
    "red": "#d63b3f",
}

graph = graphviz.Digraph(engine="fdp")

# first panel, position: 10

panels = {
    # top on panel with 2 dials
    1: {
        "nodes": {
            "green": ["O", "B", "2"],
            "orange": ["3", "T", "U", "Z"],
            "red": ["N", "K", "2", "G", "D"],
        },
        "groups": [
            {"green": ["B"], "orange": ["3"], "red": "2"},
            {"green": ["O", "B", "2"], "orange": ["T", "U", "Z"], "red": ["N", "K", "G", "D"]},
        ],
    },
    # top on panel with 4x4 dial grid
    2: {
        "nodes": {
            "green": ["R", "M"],
            "orange": ["M", "2", "3"],
            "red": ["F", "V", "N", "M"],
        },
        "groups": [
            {"green": ["R"], "orange": ["2", "3"], "red": ["F", "M", "V", "N"]},
        ],
    },
    # middle on panel with 2x2 clr grid
    3: {
        "nodes": {
            "green": ["2", "S", "Q"],
            "red": ["Y", "X", "3"],
        },
        "groups": [
            {"green": ["2", "S", "Q"], "red": ["Y", "X", "3"]},
        ],
    }
}

for panel_id, panel in panels.items():
    with graph.subgraph(name=f"cluster_{panel_id}") as subgraph:
        subgraph.attr(color="red")
        subgraph.attr(label=f"Panel {panel_id}")

        for colour, values in panel["nodes"].items():
            for value in values:
                subgraph.node(f"{panel_id}/{colour}/{value}", value, shape="circle", style="filled", color=colour_map[colour])
        for i, group in enumerate(panel["groups"]):
            name = f"{panel_id}/group/{i}"
            subgraph.node(name, "", shape="doublecircle")

            for colour, nodes in group.items():
                for node in nodes:
                    subgraph.edge(f"{panel_id}/{colour}/{node}", name)

graph.unflatten()
graph.render(format="png")
