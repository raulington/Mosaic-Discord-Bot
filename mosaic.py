import os
from PIL import Image
from scipy import spatial
import numpy as np

def KDTree(path):
    squares = []
    colors = []
    for file in os.listdir(path):
        if len(squares) == 200:
            break
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            square = Image.open(path + '/' + file)
            d = square.size[0] / 50
            verticalTiles = int(square.size[1] / d)

            new_w = int(50 * 20)
            new_h = int(verticalTiles * 20)
            
            square = square.resize((new_w, new_h)).convert('RGB')
            coloraverage = list(np.array(square).mean(axis=0).mean(axis=0))
            if len(coloraverage) == 3:
                colors.append(coloraverage)
                squares.append(square)
    
    kdtree = spatial.KDTree(colors)
    
    return (kdtree, squares)

def generate(path, KDtree, squares, tileSize, tilesAcross):
    square_size = (tileSize, tileSize)
  
    baseimage = Image.open(path)
    baseimage = baseimage.convert("RGB")
    
    d = baseimage.size[0] / tilesAcross
    verticalTiles = int(baseimage.size[1] / d)
 
    new_w = int(tilesAcross * tileSize)
    new_h = int(verticalTiles * tileSize)
    
    resized_photo = baseimage.resize((tilesAcross, verticalTiles))
    
    mosaic = Image.new('RGB', (new_w, new_h))
    
    new_squares = {}
    for i in range(tilesAcross):
        for j in range(verticalTiles):
            x, y = i*tileSize, j*tileSize
            rgb = resized_photo.getpixel((i, j))
            close_val = KDtree.query(rgb)
            idx = close_val[1]
            if idx not in new_squares:
                new_squares[idx] = squares[idx].resize(square_size)
            mosaic.paste(new_squares[idx], (x, y))

    
    return mosaic