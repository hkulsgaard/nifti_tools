import os
import utils
import numpy as np
import nibabel as nib
import nibabel.processing as nibpro
from nibabel.affines import apply_affine 

class NiftiFunction:
    def __init__(self, params, title='', suffix=''):
        self.params = params
        if self.getParam('save_partial')==None:
            self.setParam('save_partial', False)
        self.title = title
        self.suffix = suffix
        self.exportable = True

    def apply(self, nii):
        self.print_info()

    def getSuffix(self):
        return self.suffix
    
    def print_info(self):
        print('[INFO]{}: {}'.format(self.title, self.params))

    def printParams(self):
        print('      Parameters:', self.params)

    def getParam(self, key):
        try:
            param = self.params[key]
        except:
            param = None

        return param
    
    def setParam(self, key, value):
        self.params[key] = value
    
    def isExportable(self):
        return self.exportable
    

class ReorderToCanonical(NiftiFunction):
    def __init__(self, params):
        super().__init__(params=params,
                         title='Reorder to canonical',
                         suffix='reo')

    def apply(self, nii):
        super().apply(nii)

        canonical_nii = nib.as_closest_canonical(nii)

        # needed to set the qform code as "scanner"
        canonical_nii.set_qform(canonical_nii.get_qform())

        return canonical_nii
    

class Rotate(NiftiFunction):
    def __init__(self, params):
        super().__init__(params=params, 
                         title='Rotate',
                         suffix='rot_' + utils.list2str(params['degrees']))

    def apply(self, nii):
        super().apply(nii)
        header = nii.header
        axis1_rad = round(np.deg2rad(self.params['degrees'][0]),2)
        axis2_rad = round(np.deg2rad(self.params['degrees'][1]),2)
        axis3_rad = round(np.deg2rad(self.params['degrees'][2]),2)

        rot1 = np.array([[1, 0, 0, 0],
                        [0, np.cos(axis1_rad), -np.sin(axis1_rad), 0],
                        [0, np.sin(axis1_rad), np.cos(axis1_rad), 0],
                        [0, 0, 0, 1]])
        
        rot2 = np.array([[np.cos(axis2_rad), 0, np.sin(axis2_rad), 0],
                        [0, 1, 0, 0],
                        [-np.sin(axis2_rad), 0, np.cos(axis2_rad), 0],
                        [0,0,0,1]])
        
        rot3 = np.array([[np.cos(axis3_rad), -np.sin(axis3_rad), 0, 0],
                        [np.sin(axis3_rad), np.cos(axis3_rad), 0, 0],
                        [0,0,1,0],
                        [0,0,0,1]])

        rotations = list([rot1,rot2,rot3])

        rotated_affine = nii.affine
        for rotation in rotations:
            rotated_affine = rotation.dot(rotated_affine)

        img = np.array(nii.get_fdata())
        rotated_nii = nib.Nifti1Image(img, rotated_affine, header)

        return rotated_nii


class SetOriginPoint(NiftiFunction):
    def __init__(self, params):
        super().__init__(params=params,
                         title='Set origin point',
                         suffix='op')

    def apply(self, nii):
        super().apply(nii)
        anat_point = apply_affine(nii.affine, self.params['voxel'])
        #origin = anat_point - nii.affine[:3,3]
        origin = -anat_point

        #transform = np.identity(4)
        #transform[:3,3] = origin
        #new_affine = transform.dot(nii.affine)

        transform = np.identity(4)
        transform[:3,3] = origin
        new_affine = transform.dot(nii.affine)

        translated_nii = nib.Nifti1Image(np.array(nii.get_fdata()), new_affine, nii.header)
        
        return translated_nii
    

class SetPixDim(NiftiFunction):
    def __init__(self, params):
        super().__init__(params=params, 
                         title='Set pixel dimension',
                         suffix='pd')

    def apply(self, nii):
    # This function sets the pixdim of the nifti and rescales the affine matrix
        super().apply(nii)
        header = nii.header
        #if ((header['pixdim'][1:4]).round(2)!=new_pixdim).any():
        #print_info(path, "Fixing pixdim " + str(header['pixdim'][1:4]) + "->" + str(pixdim))

        # Sets the voxel dimensions to new_pixdim
        header['pixdim'][1:4]  = self.params['pixdim']
        new_affine = nib.affines.rescale_affine(nii.affine, nii.shape, self.params['pixdim'])

        img = np.array(nii.get_fdata())

        # use the new header before writing
        new_nii = nib.Nifti1Image(img, new_affine, header)
        return new_nii
    

class AffineToIdentity(NiftiFunction):
    def __init__(self, params):
        super().__init__(params=params, 
                         title='Affine to identity',
                         suffix='ident')

    def apply(self, nii):
    # Sets the affine matrix with a identity matrix
        super().apply(nii)
        affine = np.eye(4)
        new_nii = nib.Nifti1Image(np.array(nii.get_fdata()), affine=affine)
        return new_nii

class AffineToDiagonal(NiftiFunction):
    def __init__(self, params):
        super().__init__(params=params, 
                         title='Affine to diagonal',
                         suffix='diag')

    def apply(self, nii):
        super().apply(nii)
        aff = nii.affine
        off = np.array([nii.header['qoffSet_x'], nii.header['qoffSet_y'], nii.header['qoffSet_z']])
        pixdim = nii.header['pixdim'][1:4]

        # Create the new affine matrix with pixdim values as diagonal
        new_aff = nib.affines.from_matvec(np.diag(pixdim), [0,0,0])
        
        # Biuld a equation system to obtain the voxel coordinates of the center of the image (world [0,0,0])
        A = np.array([aff[0,0:3], aff[1,0:3], aff[2,0:3]])
        b = np.array(off)
        center = np.linalg.solve(A, b).round().astype(int)

        # Calculate the new offset for "new_affine"
        for i in range(3):
            new_aff[i,3] = (new_aff[i,0] * center[0] + new_aff[i,1]*center[1] + new_aff[i,2]*center[2])

        # DON'T DO THIS:
        #nii.set_sform(new_aff)
        #nii.set_qform(new_aff)
        
        new_nii = nib.Nifti1Image(np.array(nii.get_fdata()), new_aff, nii.header)
        return new_nii
    

class Reslice(NiftiFunction):
    def __init__(self, params):
        super().__init__(params=params, 
                         title='Affine to diagonal',
                         suffix='res')

    def apply(self, nii):
        super().apply(nii)
        # this function does the reslicing with linear interpolation
        resliced_nii = nibpro.conform(nii, self.params['dim'], self.params['pixdim'])
        
        # this function adapts the shape of the image
        #resliced_nii = nibpro.resample_to_output(nii,pixdim)

        #due to the interpolation, some values go under zero, so those are converted to zero 
        img = np.array(resliced_nii.get_fdata())
        img[img<0] = 0
        
        new_nii = nib.Nifti1Image(img, resliced_nii.affine, resliced_nii.header)
        return new_nii