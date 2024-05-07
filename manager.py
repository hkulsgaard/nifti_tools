import os
import yaml
import nifti_functions as nim
import nibabel as nib
import utils

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        print('[INFO]Loaded configuration file:"{}"'.format(config_path))

    else:
        print('[ERROR]Configuration file does not exist "{}"'.format(config_path))
        config = None
    
    nib.openers.Opener.default_compresslevel = 5

    return config

def run_tools(config, paths):
    # Pipeline manager
    print('[INFO]Nifti images to process: {}'.format(len(paths)))
    print('[INFO]Functions to perform: {}'.format(len(config)))
    
    functions = load_functions(config)

    for path in paths:
        print()
        path = os.path.normpath(path)
        nii = nib.load(path)
        suffix_acum = ''
        print('[INFO]Image: "{}"'.format(path))
        for func in functions:
            nii = func.apply(nii)
            suffix = func.getSuffix()
            if suffix != None:
                suffix_acum += '_[' + suffix + ']'
            
            # Save partial processed nifti
            if func.getParam('save_partial') & func.isExportable():
                save_nifti(nii, path, suffix_acum)
        
        # Save full processed nifti
        save_nifti(nii, path, suffix_acum)


def save_nifti(nii, path, suffix_acum, verbose=True):
    new_fname = utils.addSufix(path, suffix_acum)
    nib.save(nii, new_fname + '.gz')
    if verbose:
        print('[INFO]Saved: "{}"'.format(new_fname))


def load_functions(config):
    mdict={ 'reorder_to_canonical':nim.ReorderToCanonical,
            'rotate':nim.Rotate,
            'set_origin_point':nim.setOriginPoint,
            'set_pixel_dimension':nim.setPixDim,
            'affine_to_diagonal':nim.AffineToDiagonal,
            'affine_to_identity':nim.AffineToIdentity,
            'reslice':nim.Reslice}

    functions = list()
    for f in config:
        func_name = list(f.keys())[0]
        params = f[func_name]
        functions.append(mdict[func_name](params=params))

    return functions