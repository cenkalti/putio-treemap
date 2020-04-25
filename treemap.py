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

    def get_folder_recursive(putio_file):
        nonlocal processed

        if putio_file.folder_type == 'SHARED_ROOT':
            return

        print("appending file id:", putio_file.id)
        f = File(putio_file)
        files[f.id] = f
        if putio_file.content_type != 'application/x-directory':
            processed += putio_file.size
            print("processed %d of %d gb" % (
                processed // 2**30, total_size // 2**30))

        if putio_file.content_type == 'application/x-directory':
            children = putio_file.dir()
            for child in children:
                get_folder_recursive(child)

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
    return fig.to_html()

# TODO thread pool
# TODO combine many items
# TODO heroku
# TODO github
# TODO deploy on push
# TODO auth
# TODO favorite tools
# TODO filter small items
# TODO api method children count
# TODO show sizes in human
# TODO gunicorn
