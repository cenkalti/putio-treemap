import time
import threading
from queue import Queue, Empty
from typing import Dict

import putiopy
import plotly.graph_objects as go

MAX_CHILDREN = 20
MAX_LEVEL = 4


class File:
    def __init__(self, putio_file, size):
        self.id = putio_file.id
        self.parent_id = putio_file.parent_id
        self.name = putio_file.name
        self.size = size


def list_children(file_id: int, client: putiopy.Client):
    params = {
            'parent_id': file_id,
            'per_page': str(MAX_CHILDREN),
            'sort_by': 'SIZE_DESC',
    }
    d = client.request('/files/list', params=params)
    files = d['files']
    return [client.File(f) for f in files]


def get(token: str, file_id: int):
    def log(*args):
        print(f'[{token[:4]}]', *args)

    client = putiopy.Client(token)
    files: Dict[int, File] = {}
    processed = 0
    root = client.File.get(file_id)
    total_size = root.size
    log("total size of file(%d): %d gb" % (file_id, total_size // 2**30))

    def append_children_recursive(
            putio_file, total_sizes: Queue, level: int) -> None:
        nonlocal processed
        children = list_children(putio_file.id, client)
        threads = []
        children_sizes: Queue[int] = Queue()
        for child in children:
            if child.folder_type == 'SHARED_ROOT':
                continue

            if level > MAX_LEVEL:
                continue

            if child.content_type == 'application/x-directory':
                t = threading.Thread(
                        target=append_children_recursive,
                        args=(child, children_sizes, level + 1))
                t.start()
                threads.append(t)
            else:
                children_sizes.put(child.size)
                files[child.id] = File(child, child.size)
                processed += child.size
                log("processed %d of %d gb" % (
                    processed // 2**30, total_size // 2**30))

        for t in threads:
            t.join()

        children_size = 0
        while True:
            try:
                children_size += children_sizes.get_nowait()
            except Empty:
                break

        dir_size = putio_file.size
        if children_size > dir_size:
            dir_size = children_size

        total_sizes.put(dir_size)
        files[putio_file.id] = File(putio_file, dir_size)

    start = time.time()
    append_children_recursive(root, Queue(), level=1)
    end = time.time()
    log('file tree traversed in %s seconds' % (end - start))

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
