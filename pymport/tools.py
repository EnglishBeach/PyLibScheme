import collections
import colorsys

from pymport import parser

# def rename_nodes(g: parser.Graph, label2name: bool = True) -> parser.Graph:
#     g = g.model_copy(deep=True)
#     for n in g.nodes:
#         if label2name:
#             n.name = n.label if n.label else n.name
#         else:
#             n.label = n.name if n.name else n.label
#     return g


# def add_name_nodes(g: parser.Graph, prefix: str) -> parser.Graph:
#     g = g.model_copy(deep=True)
#     for n in g.nodes:
#         n.name = f"{prefix}.{n.name}"
#     return g


def clusterize(g: parser.Graph, cluster_volume=1) -> parser.Graph:
    g = g.model_copy(deep=True)
    nodes = g.nodes
    clusters, _ = _make_groups(
        nodes, level=1, gid=len(nodes), cluster_volume=cluster_volume
    )

    g.entries = clusters + g.entries
    return g


def colorize(g: parser.Graph):
    colors_len = max(n.label.count(".") if n.label else 0 for n in g.nodes) + 1
    color_map = _get_colormap(colors_len)
    m = 0
    g = g.model_copy(deep=True)
    for n in g.nodes:
        level = n.label.count(".") if n.label else 0
        m = max([level, m])
        if n.graphics:
            n.graphics.fill = f'"{color_map[level]}"'
    return g


def prune(g: parser.Graph, prune_names: list[str]):
    g = g.model_copy(deep=True)
    prune_ids = [i.id for i in g.nodes if i.norm in prune_names]

    entries = []
    for i in g.entries.copy():
        drop = False
        if isinstance(i, parser.Node) and (i.id in prune_ids):
            drop = True

        if isinstance(i, parser.Edge) and (
            (i.source in prune_ids) or (i.target in prune_ids)
        ):
            drop = True

        if not drop:
            entries.append(i)
    g.entries = entries
    return g


def _make_groups(
    nodes: list[parser.Node],
    level: int,
    gid: int,
    cluster_volume: int,
    external_gid: int | None = None,
) -> tuple[list[parser.Node], int]:
    groups = collections.defaultdict(lambda: [])
    add_nodes = []
    for n in nodes:
        titles = n.norm.split(".")
        if len(titles) < level + 1:
            continue
        else:
            groups[titles[level]].append(n)

    for group, group_nodes in groups.items():
        if len(group_nodes) > cluster_volume:
            gid += 1
            add_nodes.append(
                parser.Node(
                    isGroup=1,
                    id=gid,
                    name=f'"{group}"',
                    label=f'"{group}"',
                    gid=external_gid,
                )
            )
            for n in group_nodes:
                n.gid = gid

            inner_clusters, gid = _make_groups(
                group_nodes,
                level=level + 1,
                gid=gid,
                external_gid=gid,
                cluster_volume=cluster_volume,
            )
            add_nodes.extend(inner_clusters)

    return add_nodes, gid


def _get_colormap(n: int) -> list[str]:
    HSV_tuples = [(x / n * 0.8, 1, 1) for x in range(n)]
    RGB_tuples = [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]
    return [
        f"#{int(255*r):02X}{int(255*g):02X}{int(255*b):02X}" for r, g, b in RGB_tuples
    ]
