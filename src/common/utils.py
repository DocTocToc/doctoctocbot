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
