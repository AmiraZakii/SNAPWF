
#%% Import necessary libraries
from glob import glob
from os import mkdir, remove
from os.path import exists, join, basename
from shutil import move, rmtree
import subprocess
import pickle
import time

project_folder = '/sns/fadeli/SNAPWF/codes/'
data_folder = project_folder + 'data/'
graph_folder = project_folder + 'graphs/'
output_folder = project_folder + 'output/'
graph2run_folder = output_folder + 'graph2run/'
split_folder = output_folder + '01_split/'
geo_folder = output_folder + '02_geo/'
esd_folder = output_folder + '03_esd/'
ifg_folder = output_folder + '04_ifg/'
dbr_folder = output_folder + '05_dpr/'
merge_folder = output_folder + '06_merge/'
ml_folder = output_folder + '07_ml/'
flt_folder = output_folder + '08_flt/'

mk_folder =[output_folder, graph2run_folder, split_folder, geo_folder,
            dbr_folder, ifg_folder, merge_folder, ml_folder, flt_folder]

for i in mk_folder:
    if not exists(i):
        mkdir(i)

# Get the data files
data_files = glob(data_folder + '/*.zip')

######### Set the processing parameters #########
GPT = "/home/fadeli/snap/bin/gpt"
CACHE = '100G'
CPU = '20'
java_max_memory = '-Xmx200G'
    
IWs_list = ['IW1', 'IW2', 'IW3']

split_graph = graph_folder + 'step01_split_orbit.xml'
split_graph2run = graph2run_folder + 'step01_split_orbit2run.xml'

geo_graph = graph_folder + 'step02_geo.xml'
geo_graph2run = graph2run_folder + 'step02_geo2run.xml'

esd_graph = graph_folder + 'step03_esd.xml'
esd_graph2run = graph2run_folder + 'step03_esd2run.xml'

ifg_graph = graph_folder + 'step03_ifg.xml'
ifg_graph2run = graph2run_folder + 'step03_ifg2run.xml'

dbr_graph = graph_folder + 'step04_dbr.xml'
dbr_graph2run = graph2run_folder + 'step04_dpr2run.xml'

merge_graph = graph_folder + 'step05_mrg.xml'
merge_graph2run = graph2run_folder + 'step05_mrg2run.xml'

ml_graph = graph_folder + 'step06_ml.xml'
ml_graph2run = graph2run_folder + 'step06_ml2run.xml'

flt_graph = graph_folder + 'step07_flt.xml'
flt_graph2run = graph2run_folder + 'step07_flt2run.xml'

######### Define function to run the graphs #########
def rungraph(graph, GPT, CACHE, CPU, java_max_memory, message=''):
    #args = [GPT, '-J' + java_max_memory, graph, '-c', CACHE, '-q', CPU] 
    # args = [GPT, graph, '-c', CACHE, '-q', CPU]
    args = [GPT, graph]
    # Launch the processing
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    timeStarted = time.time()
    stdout = process.communicate()[0]
    print('SNAP STDOUT:{}'.format(stdout))
    print(process.returncode)
    timeDelta = time.time() - timeStarted

    print('Finished process in ' + str(timeDelta) + ' seconds.')
    print('Finished process in : {} seconds\n'.format(timeDelta))

    if process.returncode != 0:
        message = 'Error!!!'+  message + '.\n'
    else:
        message = 'Successfully completed!!! ' + message + '.\n'
    
    return process.returncode, message

#%% Move each file into a folder that has the date as the name
'''First step: sort the data into folders with the date of the 
satellite acqusition. Nothing will happen in this cell if the 
files are already  moved into the folders or the folder is empty'''
for i in data_files:
    date = i.split('/')[-1].split('.')[0].split('_')[-5].split('T')[0]
    print(date)
    date_path = data_folder + '/' + date
    print(date_path)
    if not exists(date_path):
        mkdir(date_path)
    move(i, date_path)
    print('---')

#%% Single frame preparation
# Get the data folders
input_list = sorted(glob(data_folder + '/*/'))

for input in input_list:
    try:
        input_sar = glob(input + '*.zip')[0]
        print(input_sar)
    except:
        print('No SAR data found')
        continue

    # Get the date of the sar acqusition to use as folder name
    input_date = input.split('/')[-2]
    output_folder = split_folder + input_date + '/'

    # Make a folder for the split data
    if not exists(output_folder):
        mkdir(output_folder)

    output_iw1 = output_folder + input_date + '_IW1.dim'
    output_iw2 = output_folder + input_date + '_IW2.dim'
    output_iw3 = output_folder + input_date + '_IW3.dim'
    with open(split_graph, 'r') as graph2read:
        graph = graph2read.read()
        graph = graph.replace('INPUTFILE', input_sar)
        graph = graph.replace('OUTPUTFILE_IW1', output_iw1)
        graph = graph.replace('OUTPUTFILE_IW2', output_iw2)
        graph = graph.replace('OUTPUTFILE_IW3', output_iw3)
    with open(split_graph2run, 'w') as graph2write:
        graph2write.write(graph)

    # check if the output_iw* files exist and if not run the graph
    if not exists(output_iw1) or not exists(output_iw2) or not exists(output_iw3):
        message = rungraph(split_graph2run, GPT, CACHE, CPU)
        print(message)
    else:
        print(output_folder + ': Split files already exist')

#%% Apply the workflow to calculate the interferogram for each subswath
###### Get the interferogram pairs to be processed ######
ifg_pairs = []

with open(join(data_folder, 'inter_pairs.pkl'), 'rb') as f:
    inter_pairs = pickle.load(f)

# Remove the duplicates from inter_pairs list by switching files
for i in inter_pairs:
    slave1 = i[0]
    slave2 = i[1]
    for j in inter_pairs:
        if slave1 == j[1] and slave2 == j[0]:
            inter_pairs.remove(j)

for i in inter_pairs:
    slave1 = i[0]
    slave1_nm = '%s%s'%(split_folder, slave1[17:25])
    slave2 = i[1]
    slave2_nm = '%s%s'%(split_folder, slave2[17:25])
    if exists(slave1_nm) and exists(slave2_nm):
        ifg_pairs.append([slave1_nm, slave2_nm])
        print("Slave 1: ", slave1_nm,  "Slave 2: ", slave2_nm)
print('-----------------------------------')

for slave_pair in ifg_pairs:
    slave1 = slave_pair[0] + '/'
    slave2 = slave_pair[1] + '/'
    for iw in IWs_list:
        ############## Apply the geocode workflow ##############
        slave1_iw = glob(slave1 + '*' + iw + '.dim')[0]
        slave2_iw = glob(slave2 + '*' + iw + '.dim')[0]

        slave1_date = slave1_iw.split('/')[-1].split('.')[0].split('_')[0]
        slave2_date = slave2_iw.split('/')[-1].split('.')[0].split('_')[0]

        output_geo_folder = geo_folder + slave1_date + '-' + slave2_date + '/'
        
        if not exists(output_geo_folder):
            mkdir(output_geo_folder)
        
        output_geo_iw = output_geo_folder + slave1_date + '-' + slave2_date + '_' + iw + '_Geo.dim'
        output_geo_data = output_geo_iw.replace('.dim', '.data')

        print("Slave 1" + iw + ' :' + slave1_iw)
        print("Slave 2" + iw + ' :' + slave2_iw)
        print("Output Geocode name :" + output_geo_iw)

        with open(geo_graph, 'r') as graph2read:
            graph = graph2read.read()
            graph = graph.replace('INPUTSLAVE1_IW', slave1_iw)
            graph = graph.replace('INPUTSLAVE2_IW', slave2_iw)
            graph = graph.replace('OUTPUTGEO_IW', output_geo_iw)

        with open(geo_graph2run, 'w') as graph2write:
            graph2write.write(graph)
        
        # Check if the output_ifg_iw file exists and if not run the graph
        if not exists(output_geo_iw):
            proc_stat, message = rungraph(geo_graph2run, GPT, CACHE, CPU, 'Geocoding')
            print(message)
            if proc_stat != 0:
                print('Removing output file')
                remove(output_geo_iw)
                rmtree(output_geo_data)
                continue
        else:
            print(output_geo_iw + ': Geocoding already exists')
        print('-----------------------------------')

        ############## Apply the esd workflow ##############
        input_esd_iw = output_geo_iw
        
        output_esd_folder = esd_folder + slave1_date + '-' + slave2_date + '/'
        
        if not exists(output_esd_folder):
            mkdir(output_esd_folder)
            
        output_esd_file = output_esd_folder + slave1_date + '-' + slave2_date + '_' + iw + '_Esd.dim'
        output_esd_data = output_esd_file.replace('.dim', '.data')
        
        print('-----------------------------------')
        print("Output esd file: " + output_esd_file)
        
        with open(esd_graph, 'r') as graph2read:
            graph = graph2read.read()
            graph = graph.replace('INPUTGEO_IW', input_esd_iw)
            graph = graph.replace('OUTPUTESD_IW', output_esd_file)
        
        with open(esd_graph2run, 'w') as graph2write:
            graph2write.write(graph)
            
        # Check if the output_esd_iw file exists and if not run the graph
        if not exists(output_esd_file):
            proc_stat, message = rungraph(esd_graph2run, GPT, CACHE, CPU, 'Enhanced Spectral Diversity')
            print(message)
            if proc_stat != 0:
                print('Removing output file')
                remove(output_esd_file)
                rmtree(output_esd_data)
                continue
        else:
            print(output_esd_file + ': Enhanced Spectral Diversity already exists')
        print('-----------------------------------')
        
        ############## Apply the interferogram workflow ##############
        output_ifg_folder = ifg_folder + slave1_date + '-' + slave2_date + '/'
        if not exists(output_ifg_folder):
            mkdir(output_ifg_folder)
        
        output_ifg_iw = output_ifg_folder + slave1_date + '-' + slave2_date + '_' + iw + '_Ifg.dim'
        outout_ifg_data = output_ifg_iw.replace('.dim', '.data')

        print("Out put interferogram: " + output_ifg_iw)

        with open(ifg_graph, 'r') as graph2read:
            graph = graph2read.read()
            graph = graph.replace('INPUTGEO_IW', output_geo_iw)
            graph = graph.replace('OUTPUTIFG_IW', output_ifg_iw)
        
        with open(ifg_graph2run, 'w') as graph2write:
            graph2write.write(graph)

        # Check if the output_ifg_iw file exists and if not run the graph
        if not exists(output_ifg_iw):
            proc_stat, message = rungraph(ifg_graph2run, GPT, CACHE, CPU, 'Interferogram')
            print(message)
            if proc_stat != 0:
                print('Removing output file')
                remove(output_ifg_iw)
                rmtree(outout_ifg_data)
                continue
        else:
            print(output_ifg_iw + ': Interferogram already exists')
        print('-----------------------------------')
            
        ############## Apply the deburst workflow ##############
        input_dbr_iw = output_ifg_iw
        
        output_dbr_folder = dbr_folder + slave1_date + '-' + slave2_date + '/'
         
        if not exists(output_dbr_folder):
             mkdir(output_dbr_folder)
             
        output_dbr_file = output_dbr_folder + slave1_date + '-' + slave2_date + '_' + iw + '_Dbr.dim'
        output_dbr_data = output_dbr_file.replace('.dim', '.data')
        
        print('-----------------------------------')
        print("Output deburst file: " + output_dbr_file)
        
        with open(dbr_graph, 'r') as graph2read:
            graph = graph2read.read()
            graph = graph.replace('INPUTIFG_IW', input_dbr_iw)
            graph = graph.replace('OUTPUTDPR_IW', output_dbr_file)
            
        with open(dbr_graph2run, 'w') as graph2write:
            graph2write.write(graph)
            
        # Check if the output_dpr_iw file exists and if not run the graph
        if not exists(output_dbr_file):
            proc_stat, message = rungraph(dbr_graph2run, GPT, CACHE, CPU, 'Deburst')
            print(message)
            if proc_stat != 0:
                print('Removing output file')
                remove(output_dbr_file)
                rmtree(output_dbr_data)
                continue
        else:
            print(output_dbr_file + ': Deburst already exists')
        print('-----------------------------------')
        
    ############## Apply the merge workflow ##############
    input_mrg_iw1 = output_dbr_folder + slave1_date + '-' + slave2_date + 'IW1_Dbr.dim'
    input_mrg_iw2 = output_dbr_folder + slave1_date + '-' + slave2_date + 'IW2_Dbr.dim'
    input_mrg_iw3 = output_dbr_folder + slave1_date + '-' + slave2_date + 'IW3_Dbr.dim'
    
    output_mrg_folder = merge_folder + slave1_date + '-' + slave2_date + '/'
    if not exists(output_mrg_folder):
        mkdir(output_mrg_folder)
        
    output_mrg_file = output_mrg_folder + slave1_date + '-' + slave2_date + '_Mrg.dim'
    output_mrg_data = output_mrg_file.replace('.dim', '.data')
    
    print('-----------------------------------')
    print("Output merge file: " + output_mrg_file)
    
    with open(merge_graph, 'r') as graph2read:
        graph = graph2read.read()
        graph = graph.replace('INPUTDB_IW1', input_mrg_iw1)
        graph = graph.replace('INPUTDB_IW2', input_mrg_iw2)
        graph = graph.replace('INPUTDB_IW3', input_mrg_iw3)
        graph = graph.replace('OUTPUTMRG', output_mrg_file)
        
    with open(merge_graph2run, 'w') as graph2write:
        graph2write.write(graph)
        
    # Check if the output_mrg_iw file exists and if not run the graph
    if not exists(output_mrg_file):
        proc_stat, message = rungraph(merge_graph2run, GPT, CACHE, CPU, 'Merge')
        print(message)
        if proc_stat != 0:
            print('Removing output file')
            rmtree(output_mrg_folder)
            continue
    else:
        print(output_mrg_file + ': Merge already exists')
    print('-----------------------------------')
        
    ############## Apply the ml workflow ##############
    input_ml_file = output_mrg_file
    
    output_ml_folder = ml_folder + slave1_date + '-' + slave2_date + '/'
    
    if not exists(output_ml_folder):
        mkdir(output_ml_folder)
        
    output_ml_file = output_ml_folder + slave1_date + '-' + slave2_date + '_Ml.dim'
    output_ml_data = output_ml_file.replace('.dim', '.data')
    
    print('-----------------------------------')
    print("Output ml file: " + output_ml_file)
    
    with open(ml_graph, 'r') as graph2read:
        graph = graph2read.read()
        graph = graph.replace('INPUTMRG', input_ml_file)
        graph = graph.replace('OUTPUTML', output_ml_file)
    
    with open(ml_graph2run, 'w') as graph2write:
        graph2write.write(graph)
        
    # Check if the output_ml_iw file exists and if not run the graph
    if not exists(output_ml_file):
        proc_stat, message = rungraph(ml_graph2run, GPT, CACHE, CPU, 'Multi-looking')
        print(message)
        if proc_stat != 0:
            print('Removing output file')
            rmtree(output_ml_folder)
            continue
    else:
        print(output_ml_file + ': Multi-looking already exists')
        
    ############## Apply the flt workflow ##############
    input_flt_iw = output_ml_file
    
    output_flt_folder = flt_folder + slave1_date + '-' + slave2_date + '/'
    
    if not exists(output_flt_folder):
        mkdir(output_flt_folder)
    
    output_flt_file = output_flt_folder + slave1_date + '-' + slave2_date + '_Flt.dim'
    output_flt_data = output_flt_file.replace('.dim', '.data')
    
    print('-----------------------------------')
    print("Output flt file: " + output_flt_file)
    
    with open(flt_graph, 'r') as graph2read:
        graph = graph2read.read()
        graph = graph.replace('INPUTML', input_flt_iw)
        graph = graph.replace('OUTPUTFLT', output_flt_file)
        
    with open(flt_graph2run, 'w') as graph2write:
        graph2write.write(graph)
        
    # Check if the output_flt_iw file exists and if not run the graph
    if not exists(output_flt_file):
        proc_stat, message = rungraph(flt_graph2run, GPT, CACHE, CPU, 'Filtering')
        print(message)
        if proc_stat != 0:
            print('Removing output file')
            rmtree(output_flt_folder)
            continue
    else:
        print(output_flt_file + ': Filtering already exists')
    print('-----------------------------------')
        

#%%