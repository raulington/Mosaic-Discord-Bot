from mosaic import KDTree, generate
from io import BytesIO
import threading

themes = ['amongus','berserk', 'chainsawman', 'dragonball', 'food', 'onepunchman', 'spiderman', 'splatoon', 'streetfighter', 'TaylorSwift', 'jojo', 'metroid', 'zelda']
trees = {}

def create_tree(theme):
    print('Preparing tiles for', theme)
    path = f"./imgs/{theme}"
    trees[theme] = KDTree(path)
    print('Finished preperation for', theme)
    
threads = []

# Preprocess KDTrees for each theme
for theme in themes:
    t = threading.Thread(target=create_tree, args=(theme,))
    t.start()
    threads.append(t)

# Join each thread created
for t in threads:
    t.join()

def generator(tileSize, tilesAcross, theme, file):
    print('Making Mosaic')
    tree, squares = trees[theme]
    mosaic = generate(file, tree, squares, tileSize, tilesAcross)

    # Get Image bytes
    bytes_io = BytesIO()
    mosaic.save(bytes_io, format="JPEG")
    image_bytes = bytes_io.getvalue()
    bytes_io.close()
    print('Finished Mosaic')
    return image_bytes