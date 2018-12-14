import math
import numpy as np
import time


def d2xy(n,d):
    t=d
    x,y = (0,0)
    s = 1
    while s< n:
        rx = 1 & (t//2)
        ry = 1 & (t ^ rx)
        x,y = rot(s,x,y,rx,ry)
        x += s * rx
        y += s * ry
        t = t//4
        s *=2
    return (x,y)


def xy2d(n,x,y):
    d = 0
    s = n//2
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s * (( 3 * rx ) ^ ry)
        x,y = rot(s,x,y,rx,ry)
        s = s//2
    return d


def rot(n,x,y,rx,ry):
    if ry  == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        z = x
        m = y
        x = m
        y = z
    return (x,y)


def get_n(x,y):
    d = max(x,y)
    return 2**(math.ceil(math.log2(d)))


def build_mat(arr,x,y):
    mat = []
    for i in arr:
        if i % x == 0:
            mat.append([])
        mat[-1].append(i)
    return mat


class HilbertList:
    def __init__(self,mat):
        start_time = time.time()
        self.rows = len(mat)
        self.cols = len(mat[0])
        self.n = get_n(self.rows,self.cols)
        self.mat = mat
        self.hilbert_dict = {}
        self.hilbert_indicies = {}
        for row_idx,row in enumerate(mat):
            for col_idx,col in enumerate(row):
                d = xy2d(self.n,col_idx,row_idx)
                self.hilbert_dict[(col_idx,row_idx)] = d
        self.set_hilbert_order()
        print(time.time() - start_time)
        
    def __getitem__(self,item):
        if not isinstance(item,int):
            foo = str(type(item))
            raise  TypeError ('list indicies must be int not %s'%foo)
        try:
            col,row = self.hilbert_indicies[item]
        except KeyError:
            raise IndexError
        return self.mat[row][col]
    
    def __setitem__(self,name,value):
        if isinstance(name,int):
            col, row = self.hilbert_indicies[name]
            self.mat[row][col] = value
        else:
            raise TypeError(f'list indicies must be int not {str(type(name))}')

    def __len__(self):
        return len(self.hilbert_dict)

    def set_hilbert_order(self):
        indicies = [item[0] for item in sorted(
            self.hilbert_dict.items(), key=lambda x:x[1])]
        self.hilbert_indicies = {idx: pair for idx, pair in enumerate(indicies)}

    def stitch_img(self):
        tile_list = np.array(self.row_col_order())
        row_list = np.split(tile_list,self.rows)
        pix_map = np.concatenate([np.concatenate(row,axis=1)
                                  for row in row_list])
        return pix_map

    def hilbert_order(self):
        indicies = [item[0] for item in sorted(
            self.hilbert_dict.items(),key=lambda x:x[1])]
        return [self.mat[row][col] for col,row in indicies]

    def row_col_order(self):
        return [col for row in self.mat for col in row]

    def print_mat(self):
        print('\n\n'.join('\t'.join('% 6s'%col for col in row) for row in self.mat))
