import os, subprocess
import numpy as np

class Pycorem:

    def __init__(self, path_corem):
        self.path_corem = path_corem if path_corem[-1] is "/" else path_corem+"/"

        self.retina_params = [
            23.1, # tau_photoreceptor
            2.95, # tau_horizontal
            3.3,  # tau_off_bipolar
            8.0,  # tau_on_bipolar
            -0.0055, # slope_photoreceptor
            0.994,   # slope_horizontal
            15.08,   # slope_off_bipolar
            -22.73]  # slope_on_bipolar

        self.hyper_params = {
            "sim_time" : "185",
            "multim_start" : "100",
            "multim_mode" : "temporal",
            "multim_show" : "False",
            "cell_x" : "10",
            "cell_y" : "10",
            "input" : "retina.Input('impulse',{'start','100.0','stop','120.0','amplitude','200.0','offset','0.0','sizeX','20','sizeY','20'})"
        }

    def retina_params_single_ring(self, ring):
        """
        Return the parameters for the Retina script for a specific ring
        @params
          ring : which ring (1 to 6)
        """
        return [
            [27.35769,4.35913,5.02094,5.76994,-0.01000,1.00000,78.02489,-86.65619],
            [23.58143,2.85156,3.33654,7.85565,-0.00601,0.99041,14.98305,-23.33950],
            [22.46325,2.05628,2.29225,5.66703,-0.00424,0.94431,23.90276,-29.42842],
            [18.52141,2.05788,5.37845,7.05406,-0.00646,0.89962,34.27840,-40.85430],
            [23.35984,2.42037,-50.10615,8.86794,-0.00134,0.94972,23.35984,-36.66481],
            [22.09490,3.69305,2.18441,5.54354,-0.00333,0.94556,16.74568,-21.16623]][ring-1]

    def generate_script(self, hyper_params, retina_params, name):
        """
        Save a customized retina script to be used by COREM in the current directory
        into the "Retina_scripts/" subdirectory
        @params
          hyper_params : the hyperparameters of the script
          retina_params : the parameters for the individual cells
          name : the name of the script
        """

        try:
            f = open("{}Retina_scripts/{}".format(self.path_corem, name), "w")
        except Exception as e:
            print("Failed to open Retina script file. Maybe COREM directory is not right?")
            raise e

        f.write("\
        retina.TempStep('1')\n\
        retina.SimTime('"+hyper_params['sim_time']+"')\n\
        retina.NumTrials('1')\n\
        retina.PixelsPerDegree({'20.0'})\n\
        retina.DisplayDelay('0')\n\
        retina.DisplayZoom({'10.0'})\n\
        retina.DisplayWindows('3')\n\
        "+hyper_params['input']+"\n\
        retina.Create('LinearFilter','tmp_photoreceptor',{'type','Gamma','tau','"+str(retina_params[0])+"','n','10.0'})\n\
        retina.Create('StaticNonLinearity','SNL_photoreceptor',{'slope','"+str(retina_params[4])+"','offset','0.0','exponent','1.0'})\n\
        retina.Create('LinearFilter','tmp_horizontal',{'type','Gamma','tau','"+str(retina_params[1])+"','n','1.0'})\n\
        retina.Create('StaticNonLinearity','SNL_horizontal',{'slope','"+str(retina_params[5])+"','offset','0.0','exponent','1.0'})\n\
        retina.Create('LinearFilter','tmp_OFF_bipolar',{'type','Gamma','tau','"+str(retina_params[2])+"','n','1.0'})\n\
        retina.Create('StaticNonLinearity','SNL_OFF_bipolar',{'slope','"+str(retina_params[6])+"','offset','0.0','exponent','1.0'})\n\
        retina.Create('LinearFilter','tmp_ON_bipolar',{'type','Gamma','tau','"+str(retina_params[3])+"','n','1.0'})\n\
        retina.Create('StaticNonLinearity','SNL_ON_bipolar',{'slope','"+str(retina_params[7])+"','offset','0.0','exponent','1.0'})\n\
        retina.Connect('L_cones','tmp_photoreceptor','Current')\n\
        retina.Connect('tmp_photoreceptor','SNL_photoreceptor','Current')\n\
        retina.Connect('SNL_photoreceptor', 'tmp_horizontal', 'Current')\n\
        retina.Connect('tmp_horizontal', 'SNL_horizontal', 'Current')\n\
        retina.Connect({'SNL_photoreceptor','-','SNL_horizontal'},'tmp_OFF_bipolar', 'Current')\n\
        retina.Connect('tmp_OFF_bipolar', 'SNL_OFF_bipolar', 'Current')\n\
        retina.Connect({'SNL_photoreceptor','-','SNL_horizontal'},'tmp_ON_bipolar', 'Current')\n\
        retina.Connect('tmp_ON_bipolar', 'SNL_ON_bipolar', 'Current')\n\
        retina.multimeter('"+hyper_params['multim_mode']+"', 'SNL_photoreceptor', 'SNL_photoreceptor', {'x','"+hyper_params['cell_x']+"','y','"+hyper_params['cell_y']+"'}, 'Show','"+hyper_params['multim_show']+"','startTime','"+hyper_params['multim_start']+"')\n\
        retina.multimeter('"+hyper_params['multim_mode']+"', 'SNL_OFF_bipolar', 'SNL_OFF_bipolar', {'x','"+hyper_params['cell_x']+"','y','"+hyper_params['cell_y']+"'}, 'Show','"+hyper_params['multim_show']+"','startTime','"+hyper_params['multim_start']+"')\n\
        retina.multimeter('"+hyper_params['multim_mode']+"', 'SNL_ON_bipolar', 'SNL_ON_bipolar', {'x','"+hyper_params['cell_x']+"','y','"+hyper_params['cell_y']+"'}, 'Show','"+hyper_params['multim_show']+"','startTime','"+hyper_params['multim_start']+"')\n\
        ")

        f.close()

    def call_script(self, name, no_stdout=False):
        """
        Calls the retina script of specified name
        @params
          name : Name of the retina script to call
          no_stdout : if this is True, COREM will not print to the console
        """
        # Save current directory
        last_dir = os.getcwd()
        # Change to COREM directory
        os.chdir(self.path_corem)
        # Call the script
        if no_stdout is True:
            with open(os.devnull, "wb") as devnull: # We do not want the output from corem
                subprocess.check_call(['./corem', 'Retina_scripts/'+name], stdout=devnull, stderr=subprocess.STDOUT)
        else:
            os.system("./corem Retina_scripts/" + name)
        # Change back to previous directory
        os.chdir(last_dir)

    def read_results(self, ids, n=""):
        """
        Read the results the COREM script generated from COREM's results directory.
        If all cell outputs were recorded, it has to be specified which cell should be read.
        @params
          ids : IDs of the cells that should be read
          n : number of cell that should be read
        @return
          returns a list whose elements are the results of the cells specified in ids
        """
        return [np.float64(np.loadtxt(self.path_corem+'results/'+id+n)) for id in ids]

    def get_eccentricity_function(self, cell, r):
        """
        Return the eccentricity scaling function for a specific cell
        @params
          cell : name of the cell
        """
        if cell == "photoreceptor" or cell == "on_bipolar":
            return np.exp( -0.2 * r) + 0.7
        if cell == "off_bipolar":
            return 0.7 * np.exp(-0.2 * r) + 0.8
        else:
            print("No such parameters. Either 'photoreceptor', 'off_bipolar' or 'on_bipolar'")
