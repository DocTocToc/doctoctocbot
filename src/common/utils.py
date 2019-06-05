from itertools import zip_longest
from itertools import takewhile
import locale

def dictextract(key, var):                                                 
    if hasattr(var, 'items'):                                                   
        for k, v in var.items():                                                
            if k == key:                                                        
                yield v                                                         
            if isinstance(v, dict):                                             
                for result in dictextract(key, v):                         
                    yield result                                                
            elif isinstance(v, list):                                           
                for d in v:                                                     
                    for result in dictextract(key, d):                     
                        yield result

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def trim_grouper(iterable, n, fillvalue=None):
    for group in grouper(iterable, n, fillvalue=fillvalue):
        yield tuple(takewhile((lambda x: x), group))

def localized_tuple_list_sort(lst, n, loc=None):
    if loc is not None:
        locale.setlocale(locale.LC_ALL, loc)
    return sorted(lst, key=lambda x: locale.strxfrm(x[n]))