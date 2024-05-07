import utils
import manager as manager
import os

print('\n-----------\nNIFTI TOOLS\n-----------\n')

# Load configuration file
config_path = utils.askConfigFile(os.getcwd(), title='Select the YAML configuration file')

if config_path !='':
    config = manager.load_config(config_path)

    inic = os.path.normpath('E:\Pladema\Datos\Vallejo\segunda_tirada\prueba2')
    paths = utils.askFiles(title='Select the nifti images to process', initialdir=inic)

    manager.run_tools(config, paths)

else:
    print('[INFO]No config file selected')

print('\n')