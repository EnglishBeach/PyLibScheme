import collections
import colorsys

from pylibscheme import parser


def colorize(g: parser.Graph):
    colors_len = max(n.norm.count(".") if n.norm else 0 for n in g.nodes) + 1
    color_map = _get_colormap(colors_len)
    m = 0
    g = g.copy()
    for n in g.nodes:
        level = n.norm.count(".") if n.norm else 0
        m = max([level, m])
        if n.graphics:
            n.graphics.fill = f'"{color_map[level]}"'
    return g


def prune(g: parser.Graph, prune_names: list[str]):
    g = g.copy()
    prune_ids = [i.id for i in g.nodes if i.norm in prune_names]

    entries = []
    for i in g.entries.copy():
        drop = False
        if isinstance(i, parser.Node) and (i.id in prune_ids):
            drop = True

        if isinstance(i, parser.Edge) and ((i.source in prune_ids) or (i.target in prune_ids)):
            drop = True

        if not drop:
            entries.append(i)
    g.entries = entries
    return g


def clusterize(g: parser.Graph, ter_groups: bool) -> parser.Graph:
    g = g.copy()
    nodes = g.nodes
    clusters, _ = _clusterize(
        nodes,
        level=1,
        max_id=len(nodes),
        end_size=not ter_groups,
    )

    g.entries = clusters + g.entries
    return g


def _clusterize(
    nodes: list[parser.Node],
    level: int,
    max_id: int,
    end_size: int,
    gid: int | None = None,
) -> tuple[list[parser.Node], int]:
    groups = collections.defaultdict(lambda: [])
    add_nodes = []
    for n in nodes:
        titles = n.norm.split(".")
        if level < len(titles):
            groups[titles[level]].append(n)

    for group, group_nodes in groups.items():
        if len(group_nodes) > end_size:
            max_id += 1
            add_nodes.append(
                parser.Node(
                    isGroup=1,
                    id=max_id,
                    name=f'"{group}"',
                    label=f'"{group}"',
                    gid=gid,
                )
            )
            for n in group_nodes:
                n.gid = max_id

            inner_clusters, max_id = _clusterize(
                group_nodes,
                level=level + 1,
                max_id=max_id,
                gid=max_id,
                end_size=end_size,
            )
            add_nodes.extend(inner_clusters)

    return add_nodes, max_id


def _get_colormap(n: int) -> list[str]:
    HSV_tuples = [(x / n * 0.8, 1, 1) for x in range(n)]
    RGB_tuples = [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]
    return [f"#{int(255*r):02X}{int(255*g):02X}{int(255*b):02X}" for r, g, b in RGB_tuples]
