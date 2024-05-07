import old_nifti_methods as nim
import dialog

# For more info visit https://nipy.org/nibabel/coordinate_systems.html

def main():
    
    # initial directory
    #inic_dir = 'E:/Pladema/Datos/sauce/Mar_Val'
    inic_dir = 'E:/ladema/Datos/sauce/Surcos_Mariana/raw/resolucion_rara'

    # select the images to process
    fnames = dialog.selectFiles(inic_dir)

    # Step 2 of the re-orientation phase for the AMI dataset
    # For 180x320x320 -> 1 .75 .75
    # For (190-200)x320x320 -> 1 .725 .725
    # for 185x256x256 -> 1 .9 .9 
    for f in fnames:
        nim.reorient2canonical(f)
        #nim.rotateNii(f, rotation_degrees=[90,0,90])
        #nim.changeOriginPoint(f, point=[88,176,163])
        #nim.setPixDim(f,[1, .75, .75], "_pd") # for T1 
        #nim.setPixDim(f,[.56, 1, 1]) # for FLAIR
        #nim.setPixDim(f,[1,0.75,0.75])
        #nim.affine2diag(f)
        #nim.affine2identity(f)
        #nim.reslice(f,[121,145,121], [1.5,1.5,1.5])
        #nim.reslice(f,[320,320,180], [0.75,0.75,1])
        #print(f)

    # Step 3 of the re-orientation phase for the AMI dataset
    #fix_pixdim(fnames)

    print_end()

def fix_pixdim(fnames):
# This scripts fixes those images with a resolution different from [185,256,256]
# and a pixdim equals to [1,1,1]
    count = 0
    for f in fnames:

        [reso, pixdim] = nim.getDims(f)
        
        if nim.checkDim(f,[185,256,256],[1,1,1]):
            nim.setPixDim(f,[1, .9, .9], "_pd")
            count = count + 1

    print("\n[INFO] Images fixed: " + str(count))

""""
        if (reso != [185,256,256]).any() & (pixdim == [1,1,1]).all():
            nim.setPixDim(f,[1,0.75,0.75])
            print("[INFO] Fixing: " + f)
            print("	>"+str(reso))
            print("	>"+str(pixdim))
            count += 1
"""

def print_end():
    print("[INFO] Job done!")

if __name__ == '__main__':
    main()