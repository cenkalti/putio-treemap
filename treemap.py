import threading
from typing import Dict

import putiopy
import plotly.graph_objects as go


class File:
    def __init__(self, putio_file):
        self.id = putio_file.id
        self.parent_id = putio_file.parent_id
        self.name = putio_file.name
        self.size = putio_file.size


def get(token: str, file_id: int):
    client = putiopy.Client(token)

    files: Dict[int, File] = {}
    processed = 0
    root = client.File.get(file_id)
    total_size = root.size

    def append_file(putio_file):
        nonlocal processed
        # print("appending file id:", putio_file.id)
        f = File(putio_file)
        files[f.id] = f
        if putio_file.content_type != 'application/x-directory':
            processed += putio_file.size
            print("processed %d of %d gb" % (
                processed // 2**30, total_size // 2**30))

    append_file(root)

    def get_folder_recursive(putio_file):
        if putio_file.folder_type == 'SHARED_ROOT':
            return

        if putio_file.content_type == 'application/x-directory':
            total_size = 0
            children = putio_file.dir()
            threads = []
            for child in children:
                total_size += child.size
                if child.content_type == 'application/x-directory':
                    t = threading.Thread(target=get_folder_recursive,
                                         args=(child, ))
                    t.start()
                    threads.append(t)
                else:
                    append_file(child)
            for t in threads:
                t.join()

        putio_file.size = total_size
        append_file(putio_file)

    get_folder_recursive(root)

    ids = []
    labels = []
    values = []
    parents = []

    for id, file in files.items():
        ids.append(file.id)
        labels.append(file.name)
        values.append(file.size)
        try:
            parents.append(files[file.parent_id].id)
        except KeyError:
            parents.append('')

    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        values=values,
        parents=parents,
        marker_colorscale='Reds',
        branchvalues='total',
        texttemplate='%{label}',
        hovertemplate='%{label}<br>%{value:.2s}<extra></extra>',
    ))
    return fig.to_html(include_plotlyjs='cdn')

# TODO thread pool
# TODO combine many items
# TODO favorite tools
# TODO filter small items
# TODO api method children count
