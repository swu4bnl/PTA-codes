#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi: ts=4 sw=4




################################################################################
#  Short-term settings (specific to a particular user/experiment) can
# be placed in this file. You may instead wish to make a copy of this file in
# the user's data directory, and use that as a working copy.
################################################################################


#logbooks_default = ['User Experiments']
#tags_default = ['CFN Soft-Bio']

import pickle
import os
from shutil import copyfile
from pathlib import Path


from ophyd import EpicsSignal
from bluesky.suspenders import SuspendFloor, SuspendCeil

ring_current = EpicsSignal('SR:OPS-BI{DCCT:1}I:Real-I')
sus = SuspendFloor(ring_current, 100, resume_thresh=300, sleep=600)
RE.install_suspender(sus)

# cms.SAXS.setCalibration([758, 1077], 5.03, [-65, -73])  #20201021, 13.5 keV
# RE.md['experiment_alias_directory'] = '/nsls2/data/cms/legacy/xf11bm/data/2021_3/AAmassian10'
# cms.SAXS.setCalibration([738, 1097], 3.0, [-65, -73])   #3m,13.5kev

#absorber_pos = EpicsSignal( 'XF:11BMB-ES{SM:1-Ax:ArmR}Mtr.RBV')
#sus_abs_low = SuspendFloor(absorber_pos, -56, resume_thresh=-55)
#sus_abs_hi = SuspendCeil(absorber_pos, -54, resume_thresh=-55)
#RE.install_suspender(sus_abs_low)
#RE.install_suspender(sus_abs_hi)
#from ophyd import EpicsSignal
#from bluesky.suspenders import SuspendFloor

#beam_current = EpicsSignal('SR:OPS-BI{DCCT:1}I:Real-I')
#sus = SuspendFloor(beam_current, 100, resume_thresh=101)
#RE.install_suspender(sus)
#RE.clear_suspenders()

### DEFINE YOUR PARENT DATA FOLDER HERE 


# RE.md['experiment_alias_directory'] = 'RLi/1_static'
# RE.md['experiment_alias_directory'] = 'RLi/2_tensile_Guillaume'
RE.md['experiment_alias_directory'] = '1_PTA'
RE.md["userpy_alias_directory"] = '/nsls2/data/cms/shared/config/bluesky/profile_collection/users/2026-2/beamline/ETsai/'

# RE.md['experiment_alias_directory'] = '/nsls2/data/cms/legacy/xf11bm/data/2025_2/QFang/'
# cms.SAXS.setCalibration([732, 1680-582], 3.8, [-65, -73]) #
# cms.SAXS.setCalibration([759, 1680-606], 5, [-65, -73]) #2022Jul
# cms.SAXS.setCalibration([754, 1078], 5.0, [-65, -73]) #
# cms.SAXS.setCalibration([732, 1097], 3, [-65, -73])    #2023 Oct 3m
# cms.SAXS.setCalibration([754, 1080], 5.0, [-65, -73])   #5m,13.5kev, Jan2024
# cms.SAXS.setCalibration([741, 1115], 5.03, [-65, -73])    # 13.5keV, 2m Jan 2025
# cms.SAXS.setCalibration([752, 1085], 5.03, [-65, -73]) # 2025Jan 5 m, 17 keV
# cms.SAXS.setCalibration([752, 1085+2], 5.03, [-65, -73]) # 2025Jan 5 m, 17 keV
# cms.SAXS.setCalibration([753, 1086], 5.0, [-65, -73])  #2024 June 5m
# cms.SAXS.setCalibration([746, 1080], 5.03, [-65, -73])  #2024 June 5m
cms.SAXS.setCalibration([741, 1081], 5.03, [-65, -73])  



def saxs_on():
    detselect(pilatus2M)
    WAXSx.move(-198)    
    WAXSy.move(24)  

def saxs_on_det():
    detselect(pilatus2M)
    WAXSx.move(-225)        
    WAXSy.move(30)    

def waxs_on():
    detselect(pilatus800)
    WAXSx.move(-192)    
    WAXSy.move(18)   


def waxs_on_outer():
    detselect(pilatus800)
    WAXSx.move(-210)    
    WAXSy.move(16)   

def swaxs_on():
    detselect([pilatus2M, pilatus800])
    
    WAXSx.move(-220)        
    WAXSy.move(30) 

# def swaxs_on():  
#     detselect([pilatus2M, pilatus800])
#     WAXSx.move(-210)    
#     WAXSy.move(30)  


if False:
    # The following shortcuts can be used for unit conversions. For instance,
    # for a motor operating in 'mm' units, one could instead do:
    #     sam.xr( 10*um )
    # To move it by 10 micrometers. HOWEVER, one must be careful if using
    # these conversion parameters, since they make implicit assumptions.
    # For instance, they assume linear axes are all using 'mm' units. Conversely,
    # you will not receive an error if you try to use 'um' for a rotation axis!
    m = 1e3
    cm = 10.0
    mm = 1.0
    um = 1e-3
    nm = 1e-6
    
    inch = 25.4
    pixel = 0.172 # Pilatus
    
    deg = 1.0
    rad = np.degrees(1.0)
    mrad = np.degrees(1e-3)
    urad = np.degrees(1e-6)
    
    


def get_default_stage():
    return stg


class SampleTSAXS(SampleTSAXS_Generic):
    
    def __init__(self, name, base=None, **md):
        super().__init__(name=name, base=base, **md)
        self.naming_scheme = ['name', 'extra', 'exposure_time']


class SampleGISAXS(SampleGISAXS_Generic):
    
    def __init__(self, name, base=None, **md):
        super().__init__(name=name, base=base, **md)
        self.naming_scheme = ['name', 'extra', 'th', 'exposure_time']
        self.naming_scheme = ['name', 'extra', 'clock', 'temperature', 'exposure_time']


#class Sample(SampleTSAXS):
class Sample(SampleGISAXS):

    def __init__(self, name, base=None, **md):
       
       super().__init__(name=name, base=base, **md)

       
       #self.naming_scheme = ['name', 'extra', 'clock', 'temperature', 'th', 'exposure_time']
       #self.naming_scheme = ['name', 'extra', 'th', 'exposure_time']
       #self.naming_scheme = ['name', 'extra', 'th', 'exposure_time']
       #self.naming_scheme = ['name', 'extra', 'y', 'th', 'clock', 'exposure_time']
       self.naming_scheme = ['name', 'extra', 'x', 'th', 'exposure_time']
       #self.naming_scheme = ['name', 'extra', 'clock', 'temperature', 'exposure_time']

       self._axes['x'].origin = -18.2    # -0.3   #ykchanged
       self._axes['y'].origin = 7.4# -0.1           

       self.md['exposure_time'] = 1
       #self.SAXS_time = 10 
       #self.WAXS_time = 10
       self.SAXS_time = 10
       self.WAXS_time = 10
       self.WAXS_time_rock = 3
       
       #self.incident_angles_default = [0.08, 0.10, 0.12, 0.15, 0.20]
       #self.incident_angles_default = [0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]
       #self.incident_angles_default = [0.08, 0.12, 0.14, 0.20, 0.26, 0.32] #for 17kev/15kev
       #self.incident_angles_default = [0.10, 0.16, 0.20] #for 17kev/15kev
       #self.incident_angles_default = [0.08, 0.12, 0.15, 0.18, 0.20] #for 10kev
       #self.incident_angles_default = [0.08, 0.12, 0.15, 0.18] #for 10kev LJR
       #self.incident_angles_default = [0.12, 0.16, 0.20, 0.24] #for 10kev, Perovskites
       self.incident_angles_default = [0.12, 0.16, 0.20, 0.24] #for 10kev, Perovskites
       #self.incident_angles_default = [0.02, 0.04, 0.05, 0.06, 0.08, 0.09, 0.1, 0.12, 0.15]
       #self.incident_angles_default = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15]
       #self.incident_angles_default = [0.0]

       self.x_pos_default = [-1, 0, 1]
       
       self.total_flow = 20
       self.wetflow_default = self.total_flow*np.arange(.1, .51, .1)
       self.wetwait_default = [1200,1200,1200,1200,1200]

    # def _set_axes_definitions(self):
    #     '''Internal function which defines the axes for this stage. This is kept
    #     as a separate function so that it can be over-ridden easily.'''
    #     super()._set_axes_definitions()
        
    #     self._axes_definitions.append( {'name': 'phi',
    #                         'motor': srot,
    #                         'enabled': True,
    #                         'scaling': +1.0,
    #                         'units': 'deg',
    #                         'hint': None,
    #                         } )
    #     self._axes_definitions.append( {'name': 'trans2',
    #                         'motor': strans2,
    #                         'enabled': True,
    #                         'scaling': +1.0,
    #                         'units': 'deg',
    #                         'hint': None,
    #                         } )

    def _set_axes_definitions(self):
        '''Internal function which defines the axes for this stage. This is kept
        as a separate function so that it can be over-ridden easily.'''
        super()._set_axes_definitions()
        
        self._axes_definitions.append( {'name': 'yy',
                            'motor': smy2,
                            'enabled': True,
                            'scaling': +1.0,
                            'units': 'mm',
                            'hint': None,
                            } )

    def _measureTimeSeries(self, exposure_time=None, num_frames=10, wait_time=None, extra=None, measure_type='measureTimeSeries', verbosity=3, **md):
        
        self.naming_scheme_hold = self.naming_scheme
        self.naming_scheme = ['name', 'extra', 'clock', 'exposure_time']
        super().measureTimeSeries(exposure_time=exposure_time, num_frames=num_frames, wait_time=wait_time, extra=extra, measure_type=measure_type, verbosity=verbosity, **md)
        self.naming_scheme = self.naming_scheme_hold
    
    def goto(self, label, verbosity=3, **additional):
        super().goto(label, verbosity=verbosity, **additional)
        # You can add customized 'goto' behavior here
        
    def scan_SAXSdet(self, exposure_time=None) :
        SAXS_pos=[-73, 0, 73]
        #SAXSx_pos=[-65, 0, 65]
        
        RE.md['stitchback'] = True
                
        for SAXSx_pos in SAXS_pos:
            for SAXSy_pos in SAXS_pos:
                mov(SAXSx, SAXSx_pos)
                mov(SAXSy, SAXSy_pos)
                self.measure(10)
                



    def do(self, step=0, align_step=0, **md):
        
        #NOTE: if align_step =8 is not working, try align_step=4
        
        if step<=1:
            saxs_on()
            get_beamline().modeAlignment()
            
        if step<=2:
            self.xo() # goto origin


        if step<=4:
            self.yo()
            self.tho()
        
        if step<=5:
            self.align(step=align_step, reflection_angle=0.15)
            #self.setOrigin(['y','th']) # This is done within align

        #if step<=7:
            #self.xr(0.2)

        if step<=8:
            get_beamline().modeMeasurement()
        
        if step<=10:

            if self.incident_angles==None:
                incident_angles = self.incident_angles_default
            else:
                incident_angles = self.incident_angles
                
                
            swaxs_on()
            self.measureIncidentAngles_Stitch(incident_angles, exposure_time=self.SAXS_time, tiling='ygaps', **md)
            #waxs_on()
            #self._test2_measureIncidentAngles(self.incident_angles_default, exposure_time=self.WAXS_time, tiling='ygaps', **md)

            self.thabs(0.0)
            

    def x_scan(self, samth=0.12, exposure_time=10):

        self.gotoOrigin()
        self.thabs(samth)        
        if self.incident_angles==None:
            incident_angles = self.incident_angles_default
        else:
            incident_angles = self.incident_angles
        # saxs_on()
        self.measureIncidentAngles_Stitch(incident_angles, exposure_time=exposure_time, tiling='ygaps', **md)
        for x in np.arange(-1, 1.01, 0.2):
            self.xabs(x)
            self.measure(exposure_time, extra='location1')

        if pilatus2M in cms.detector:
            SAXSy.move(SAXSy.position+5.16)           
        elif pilatus800 in cms.detector:
            WAXSy.move(WAXSy.position+5.16)           

        for x in np.arange(-1, 1.01, 0.2):
            self.xabs(x)
            self.measure(exposure_time, extra='location2')            

        if pilatus2M in cms.detector:
            SAXSy.move(SAXSy.position-5.16)           
        elif pilatus800 in cms.detector:
            WAXSy.move(WAXSy.position-5.16)           

        
    def IC_int(self):
        
        ion_chamber_readout1=caget('XF:11BMB-BI{IM:3}:IC1_MON')
        ion_chamber_readout2=caget('XF:11BMB-BI{IM:3}:IC2_MON')
        ion_chamber_readout3=caget('XF:11BMB-BI{IM:3}:IC3_MON')
        ion_chamber_readout4=caget('XF:11BMB-BI{IM:3}:IC4_MON')
        
        ion_chamber_readout=ion_chamber_readout1+ion_chamber_readout2+ion_chamber_readout3+ion_chamber_readout4
        
        return ion_chamber_readout>1*5e-08


    def do_SAXS(self, step=0, align_step=0, **md):
        
        if step<=1:
            saxs_on()
            get_beamline().modeAlignment()
            
        if step<=2:
            self.xo() # goto origin


        if step<=4:
            self.yo()
            self.tho()
        
        if step<=5:
            self.align(step=align_step, reflection_angle=0.12)
            #self.setOrigin(['y','th']) # This is done within align

        #if step<=7:
            #self.xr(0.2)

        if step<=8:
            get_beamline().modeMeasurement()
        
        if step<=10:
            if self.incident_angles==None:
                incident_angles = self.incident_angles_default
            else:
                incident_angles = self.incident_angles
            
            # if 'ME_TCTA&Ir(ppy)3' in self.name:
            #     self.SAXS_time = 60

            if 'RL_XY_SL' in self.name:
                swaxs_on()
                for xpos in np.arange(-2, 2.1, 0.5):
                    self.xabs(xpos)
                    self.measureIncidentAngles_Stitch(incident_angles, exposure_time=self.SAXS_time, tiling='ygaps', **md)
            else:
                saxs_on()
                self.measureIncidentAngles_Stitch(incident_angles, exposure_time=self.SAXS_time, tiling='ygaps', **md)


            #if self.exposure_time_SAXS==None:
                #self.measureIncidentAngles(incident_angles, exposure_time=self.SAXS_time, tiling=self.tiling, **md)
            #else:
                #self.measureIncidentAngles(incident_angles, exposure_time=self.exposure_time_SAXS, tiling=self.tiling, **md)

            self.thabs(0.0)


    def align(self, step=0, reflection_angle=0.12, verbosity=3):
        '''Align the sample with respect to the beam. GISAXS alignment involves
        vertical translation to the beam center, and rocking theta to get the
        sample plane parralel to the beam. Finally, the angle is re-optimized
        in reflection mode.
        
        The 'step' argument can optionally be given to jump to a particular
        step in the sequence.'''
        start_time = time.time()
        alignment = 'Success'
        initial_y = smy.position
        initial_th = sth.position

        align_crazy = self.swing(reflection_angle=reflection_angle)
        crazy_y = smy.position
        crazy_th = sth.position
        cms.setDirectBeamROI()

        if  align_crazy[0] == False:
            alignment = 'Failed'
            if step<=4:
                if verbosity>=4:
                    print('    align: fitting')
                
                fit_scan(smy, 1.2, 21, fit='HMi')
                ##time.sleep(2)
                fit_scan(sth, 1.5, 21, fit='max')
                ##time.sleep(2)            
                
            #if step<=5:
            #    #fit_scan(smy, 0.6, 17, fit='sigmoid_r')
            #    fit_edge(smy, 0.6, 17)
            #    fit_scan(sth, 1.2, 21, fit='max')


            if step<=8:
                #fit_scan(smy, 0.3, 21, fit='sigmoid_r')
                
                fit_edge(smy, 0.6, 21)
                #time.sleep(2)
                #fit_edge(smy, 0.4, 21)
                fit_scan(sth, 0.8, 21, fit='COM')
                #time.sleep(2)            
                self.setOrigin(['y', 'th'])
        
        
            if step<=9 and reflection_angle is not None:
                # Final alignment using reflected beam
                if verbosity>=4:
                    print('    align: reflected beam')
                get_beamline().setReflectedBeamROI(total_angle=reflection_angle*2.0)
                #get_beamline().setReflectedBeamROI(total_angle=reflection_angle*2.0, size=[12,2])
                
                self.thabs(reflection_angle)
                
                result = fit_scan(sth, 0.4, 41, fit='max') 
                #result = fit_scan(sth, 0.2, 81, fit='max') #it's useful for alignment of SmarAct stage
                sth_target = result.values['x_max']-reflection_angle
                
                if result.values['y_max']>50:
                    th_target = self._axes['th'].motor_to_cur(sth_target)
                    self.thsetOrigin(th_target)

                #fit_scan(smy, 0.2, 21, fit='max')
                #self.setOrigin(['y'])            

            if step<=10:
                self.thabs(0.0)
                beam.off()

        ### save the alignment information
        align_time = time.time() - start_time

        current_data = {'a_sample': self.name,
                        'b_quick_alignment': alignment, 
                        'c_align_time': align_time, 
                        'd_offset_y': smy.position - initial_y,
                        'e_offset_th': sth.position - initial_th, 
                        'f_crazy_offset_y': smy.position - crazy_y,
                        'g_crazy_offset_th': sth.position - crazy_th, 
                        'h_search_no': align_crazy[1]}
        
        temp_data = pds.DataFrame([current_data])


        # # {proposal_path()}experiments/
        # # INT_FILENAME='{}/data/{}.csv'.format(proposal_path()+'/experiments/'+RE.md['experiment_alias_directory'], 'alignment_results.csv')  
        # # os.mkdir(os.path.dirname(__file__)+'/data/',exist_ok=True)
        # (Path(os.path.dirname(__file__))/'data').mkdir(exist_ok=True)
        # INT_FILENAME='{}/data/{}.csv'.format(os.path.dirname(__file__) , 'alignment_results')            
    
        # if os.path.isfile(INT_FILENAME):
        #     output_data = pds.read_csv(INT_FILENAME, index_col=0)
        #     output_data = pds.concat([output_data, temp_data])    
        #     output_data.to_csv(INT_FILENAME)
        # else:
        #     temp_data.to_csv(INT_FILENAME)

    def swing(self, step=0, reflection_angle=0.12, ROI_size=[10, 180], th_range=0.3, int_threshold=10, verbosity=3):

        #setting parameters
        rel_th = 1
        ct = 0
        cycle = 0
        intenisty_threshold = 10

        #re-assure the 3 ROI positon
        get_beamline().setDirectBeamROI()
        get_beamline().setReflectedBeamROI(total_angle=reflection_angle*2)

        #set ROI2 as a fixed area
        get_beamline().setROI2ReflectBeamROI(total_angle=reflection_angle*2, size=ROI_size)
        pilatus2M.roi2.size.y.set(190)
        pilatus2M.roi2.min_xyz.min_y.set(852)


        #def ROI3 in 160pixels with the center located at reflection beam
        # get_beamline().setReflectedBeamROI(total_angle = reflection_angle*2, size=ROI_size) #set ROI3

        # self.thabs(reflection_angle)
        if verbosity>=4:
            print('  Aligning {}'.format(self.name))
        
        # if step<=0:
        #     # Prepare for alignment
            
        #     if RE.state!='idle':
        #         RE.abort()
                
        #     if get_beamline().current_mode!='alignment':
        #         #if verbosity>=2:
        #             #print("WARNING: Beamline is not in alignment mode (mode is '{}')".format(get_beamline().current_mode))
        #         print("Switching to alignment mode (current mode is '{}')".format(get_beamline().current_mode))
        #         get_beamline().modeAlignment()
                
                
            get_beamline().setDirectBeamROI()
            
            beam.on()

        
        if step<=2:
            # if verbosity>=4:
            #     print('    align: searching')
                
            # Estimate full-beam intensity 2025-01-24
            value = None
            if True:
                # You can eliminate this, in which case RE.md['beam_intensity_expected'] is used by default
                self.yr(-2)
                #detector = gs.DETS[0]
                detector = get_beamline().detector[0]
                # value_name = get_beamline().TABLE_COLS[0]
                beam.on()
                RE(count([detector]))
                value = detector.read()['pilatus2m-1_stats4_total']['value']
                self.yr(2)
            
            # if 'beam_intensity_expected' in RE.md:
            #     if value<RE.md['beam_intensity_expected']*0.75:
            #         print('WARNING: Direct beam intensity ({}) lower than it should be ({})'.format(value, RE.md['beam_intensity_expected']))
                
            #check the last value:
            # value=20000
            ii = 0
            while abs(pilatus2M.stats4.total.get() - value)/value < 0.1 and ii < 3: 
                ii += 1
                # Find the step-edge
                RE(self.search_plan(motor=smy, step_size=.1, min_step=0.01, target=0.5, intensity=value, polarity=-1,detector_suffix='_stats4_total'))                
                # Find the peak
                # self.thsearch(step_size=0.2, min_step=0.01, target='max', verbosity=verbosity)
                RE(self.search_plan(motor=sth, step_size=.2, min_step=0.01, target='max',detector_suffix='_stats4_total'))
            #last check for height
            # self.ysearch(step_size=0.05, min_step=0.005, intensity=value, target=0.5, verbosity=verbosity, polarity=-1)
            RE(self.search_plan(motor=smy, step_size=0.05, min_step=0.005, target=0.5, intensity=value, polarity=-1,detector_suffix='_stats4_total'))
                   
        #check reflection beam
        self.thr(reflection_angle)
        RE(count([detector]))
        
        if abs(detector.stats2.max_xy.get().y - detector.stats2.centroid.get().y) < 20 and detector.stats2.max_value.get() > intenisty_threshold:

            #continue the fast alignment 
            print('The reflective beam is found! Continue the fast alignment')
            
            while abs(rel_th) > 0.005 and ct < 5:
            # while detector.roi3.max_value.get() > 50 and ct < 5:
                
                #absolute beam position 
                refl_beam = detector.roi2.min_xyz.min_y.get() + detector.stats2.max_xy.y.get()

                #roi3 position
                roi3_beam = detector.roi3.min_xyz.min_y.get() + detector.roi3.size.y.get()/2

                #distance from current postion to the center of roi2 (the disired rel beam position)
                # rel_ypos = detector.stats2.max_xy.get().y - detector.stats2.size.get().y
                rel_ypos = refl_beam - roi3_beam

                rel_th = rel_ypos/get_beamline().SAXS.distance/1000*0.172/np.pi*180/2
                
                print('The th offset is {}'.format(rel_th))
                self.thr(rel_th)
                
                ct += 1
                RE(count([detector]))

            if detector.stats3.total.get()>50:

                print('The fast alignment works!')
                self.thr(-reflection_angle)

    
                self.setOrigin(['y', 'th'])

                beam.off()

                return True, ii

            else:
                print('Alignment Error: Cannot Locate the reflection beam')
                self.thr(-reflection_angle)
                beam.off()

                return False, ii


        elif abs(detector.stats2.max_xy.get().y - detector.stats2.centroid.get().y) > 5:
            print('Max and Centroid dont Match!')

            #perform the full alignment
            print('Alignment Error: No reflection beam is found!')
            self.thr(-reflection_angle)
            beam.off()
            return False, ii

        else:
            print('Intensiy < threshold!')

            #perform the full alignment
            print('Alignment Error: No reflection beam is found!')
            self.thr(-reflection_angle)
            beam.off()
            return False, ii

    def search_plan(self, motor=smy, step_size=1.0, min_step=0.05, intensity=None, target=0.5, detector=None, detector_suffix=None, polarity=+1, verbosity=3):
        '''Moves this axis, searching for a target value.
        
        Parameters
        ----------
        step_size : float
            The initial step size when moving the axis
        min_step : float
            The final (minimum) step size to try
        intensity : float
            The expected full-beam intensity readout
        target : 0.0 to 1.0
            The target ratio of full-beam intensity; 0.5 searches for half-max.
            The target can also be 'max' to find a local maximum.
        detector, detector_suffix
            The beamline detector (and suffix, such as '_stats4_total') to trigger to measure intensity
        polarity : +1 or -1
            Positive motion assumes, e.g. a step-height 'up' (as the axis goes more positive)
        '''
        print("HERE!!")
        
        if detector is None:
            #detector = gs.DETS[0]
            detector = get_beamline().detector[0]
        if detector_suffix is None:
            #value_name = gs.TABLE_COLS[0]
            value_name = get_beamline().TABLE_COLS[0]
        else:
            value_name = detector.name + detector_suffix

        print(f"detector={detector}")

        @bpp.stage_decorator([detector])
        @bpp.run_decorator(md={})
        def inner_search():
            nonlocal intensity, target, step_size

            if not get_beamline().beam.is_on():
                print('WARNING: Experimental shutter is not open.')
            
            
            if intensity is None:
                intensity = RE.md['beam_intensity_expected']

            # bec.disable_table()
            
            
            # Check current value
            vv = yield from bps.trigger_and_read([detector, motor])
            value = vv[value_name]['value']
            # RE(count([detector]))
            # value = detector.read()[value_name]['value']


            if target == 'max':
                
                if verbosity>=5:
                    print("Performing search on axis '{}' target is 'max'".format(self.name))
                
                max_value = value
                # max_position = self.get_position(verbosity=0)
                
                
                direction = +1*polarity
                
                while step_size>=min_step:
                    if verbosity>=4:
                        print("        move {} by {} × {}".format(self.name, direction, step_size))

                    #  pos = yield from bps.rd(motor)
                    yield from bps.mvr(motor, direction*step_size)
                    # self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)

                    prev_value = value
                    yield from bps.trigger_and_read([detector, motor])
                    # RE(count([detector]))
                    
                    value = detector.read()[value_name]['value']
                    # if verbosity>=3:
                    #     print("      {} = {:.3f} {}; value : {}".format(self.name, self.get_position(verbosity=0), self.units, value))
                        
                    if value>max_value:
                        max_value = value
                        # max_position = self.get_position(verbosity=0)
                        
                    if value>prev_value:
                        # Keep going in this direction...
                        pass
                    else:
                        # Switch directions!
                        direction *= -1
                        step_size *= 0.5
                    
                    
            elif target == 'min':
                
                if verbosity>=5:
                    print("Performing search on axis '{}' target is 'min'".format(self.name))
                
                direction = +1*polarity
                
                while step_size>=min_step:
                    if verbosity>=4:
                        print("        move {} by {} × {}".format(self.name, direction, step_size))

                    # pos = yield from bps.rd(motor)
                    yield from bps.mvr(motor, direction*step_size)
                    # self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)

                    prev_value = value
                    yield from bps.trigger_and_read([detector, motor])
                    # RE(count([detector]))
                    value = detector.read()[value_name]['value']
                    if verbosity>=3:
                        print("      {} = {:.3f} {}; value : {}".format(self.name, self.get_position(verbosity=0), self.units, value))
                        
                    if value<prev_value:
                        # Keep going in this direction...
                        pass
                    else:
                        # Switch directions!
                        direction *= -1
                        step_size *= 0.5
                                    
            else:

                target_rel = target
                target = target_rel*intensity

                if verbosity>=5:
                    print("Performing search on axis '{}' target {} × {} = {}".format(self.name, target_rel, intensity, target))
                if verbosity>=4:
                    print("      value : {} ({:.1f}%)".format(value, 100.0*value/intensity))
                
                
                # Determine initial motion direction
                if value>target:
                    direction = -1*polarity
                else:
                    direction = +1*polarity
                    
                while step_size>=min_step:
                    
                    if verbosity>=4:
                        print("        move {} by {} × {}".format(self.name, direction, step_size))
                    
                    # pos = yield from bps.rd(motor)
                    yield from bps.mvr(motor, direction*step_size)
                    # self.move_relative(move_amount=direction*step_size, verbosity=verbosity-2)
                    
                    yield from bps.trigger_and_read([detector, motor])
                    # RE(count([detector]))
                    value = detector.read()[value_name]['value']
                    #if verbosity>=3:
                    #    print("      {} = {:.3f} {}; value : {} ({:.1f}%)".format(self.name, self.get_position(verbosity=0), self.units, value, 100.0*value/intensity))
                        
                    # Determine direction
                    if value>target:
                        new_direction = -1.0*polarity
                    else:
                        new_direction = +1.0*polarity
                        
                    if abs(direction-new_direction)<1e-4:
                        # Same direction as we've been going...
                        # ...keep moving this way
                        pass
                    else:
                        # Switch directions!
                        direction *= -1
                        step_size *= 0.5
        
            # bec.enable_table()

        yield from inner_search()
    ###############        
    def do_WAXS_only(self, step=0, align_step=0, **md):
        if step<5:
            self.xo()
            self.yo()
            self.tho()
            get_beamline().modeMeasurement()        
        if step<=10:
            if self.incident_angles==None:
                incident_angles = self.incident_angles_default
            else:
                incident_angles = self.incident_angles
                
            waxs_on()
            #for detector in get_beamline().detector:
                #detector.setExposureTime(self.MAXS_time)
            self.measureIncidentAngles_Stitch(incident_angles, exposure_time=self.WAXS_time, tiling='ygaps', **md)
            #self.xabs(0.5)
            #self.measureIncidentAngles_Stitch(incident_angles, exposure_time=self.WAXS_time, tiling='ygaps', **md)
            

    ############### 
    def do_SAXS_measure(self, step=0, align_step=0, **md):
        if step<5:
            self.xo()
            self.yo()
            self.tho()
            get_beamline().modeMeasurement()        
        if step<=10:
            if self.incident_angles==None:
                incident_angles = self.incident_angles_default
            else:
                incident_angles = self.incident_angles
                
            saxs_on()
            #for detector in get_beamline().detector:
                #detector.setExposureTime(self.MAXS_time)
            #self.measureIncidentAngles_Stitch(incident_angles, exposure_time=self.SAXS_time, tiling='ygaps', **md)
            self.measureIncidentAngles_Stitch(incident_angles, exposure_time=self.SAXS_time, tiling='ygaps',**md)
            self.thabs(0.0)            
 
    ##### For checking one sample
    def do_WAXS(self, step=0, align_step=0, reflection_angle=0.12,   **md):
    
        if step<=1:
            saxs_on()
            get_beamline().modeAlignment()
            
        if step<=2:
            self.xo() # goto origin


        if step<=4:
            self.yo()
            self.tho()
        
        if step<=5:
            self.align(step=align_step, reflection_angle=reflection_angle )
            #self.setOrigin(['y','th']) # This is done within align

        #if step<=7:
            #self.xr(0.2)

        if step<=8:
            get_beamline().modeMeasurement()
        
        if step<=10:
            if self.incident_angles==None:
                incident_angles = self.incident_angles_default
            else:
                incident_angles = self.incident_angles


            if self.measure_setting['exposure_time']==None:
                exposure_time = self.WAXS_time
            else:
                exposure_time = self.measure_setting['exposure_time']
                
            waxs_on()
            #for detector in get_beamline().detector:
                #detector.setExposureTime(self.MAXS_time)
            self.measureIncidentAngles_Stitch(incident_angles, exposure_time=exposure_time, tiling='ygaps', **md)
            
            self.thabs(0.0)

    ##### For checking one sample
    def do_WAXS_align(self, step=0, align_step=0, reflection_angle=0.12,   **md):
    
        if step<=1:
            saxs_on()
            get_beamline().modeAlignment()
            
        if step<=2:
            self.xo() # goto origin


        if step<=4:
            self.yo()
            self.tho()
        
        if step<=5:
            self.align(step=align_step, reflection_angle=reflection_angle )
            #self.setOrigin(['y','th']) # This is done within align

        #if step<=7:
            #self.xr(0.2)

        #if step<=8:
            #get_beamline().modeMeasurement()
        
    def do_WAXS_measure(self, step=0, **md):

        if step<=1:
            self.gotoOrigin()

        if step<=10:
            if self.incident_angles==None:
                incident_angles = self.incident_angles_default
            else:
                incident_angles = self.incident_angles

            incident_angle_large = [angle for angle in incident_angles if angle>5]

            if self.measure_setting['exposure_time']==None:
                exposure_time = self.WAXS_time
            else:
                exposure_time = self.measure_setting['exposure_time']
            
            get_beamline().modeMeasurement()            
            waxs_on()

            #for detector in get_beamline().detector:
                #detector.setExposureTime(self.MAXS_time)
            
            # for xpos in np.arange(-5, 5.1, .5):
            #     self.xabs(xpos)
            self.measureIncidentAngles_Stitch(incident_angles, exposure_time=exposure_time, tiling='ygaps', **md)

            #rock
            # if 1: #'PBTTT' in self.name:
            #     rock_angle = 1.16
            #     rock_motor_limits = 0.46
            # elif 'PCD' in self.name:
            #     rock_angle = 0.98
            #     rock_motor_limits = 0.68
            # self.measureRock(rock_angle, exposure_time=self.WAXS_time_rock, rock_motor=sth, rock_motor_limits=rock_motor_limits, extra='rock', **md)


            # self.xabs(1)
            # self.measureIncidentAngles_Stitch(incident_angles, exposure_time=exposure_time, tiling='ygaps', **md)

                
            self.thabs(0.0)        



class GIBar_Custom(GIBar):
    def __init__(self, name='GIBarCustom', base=None, **kwargs):
        super().__init__(name=name, base=base, **kwargs)
       
        #self._axes['x'].origin = -59.3
        ##position for calibration 
        self._axes['x'].origin = -71.65
        self._axes['y'].origin = 7
        self._axes['th'].origin = 0.1
        self.setPosition()
        
        # CREATE DIRECTORIES TO SAVE DATA
        #holder_data_folder = os.path.join(parent_data_folder, self.name)
        #os.makedirs(holder_data_folder, exist_ok=True)
        #os.makedirs(os.path.join(holder_data_folder, 'waxs'), exist_ok=True)
        #os.makedirs(os.path.join(holder_data_folder, 'saxs'), exist_ok=True)
        #os.makedirs(os.path.join(holder_data_folder, 'waxs/raw'), exist_ok=True)
        #os.makedirs(os.path.join(holder_data_folder, 'saxs/raw'), exist_ok=True)
        #RE.md['experiment_alias_directory'] = holder_data_folder
        
        #### COPY CURRENT STATE OF user.py TO SAMPLE DIRECTORY
        #copyfile(os.path.join(parent_data_folder, 'user.py'), os.path.join(holder_data_folder,'user.py'))
                    

    def doSamples(self, verbosity=3):

        #maxs_on()
        for sample in self.getSamples():
            if verbosity>=3:
                print('Doing sample {}...'.format(sample.name))
            if sample.detector=='SAXS' or sample.detector=='BOTH':
                sample.do_SAXS()

        for sample in self.getSamples():
            if verbosity>=3:
                print('Doing sample {}...'.format(sample.name))
            if sample.detector=='WAXS':
                sample.do_WAXS_align()

        for sample in self.getSamples():
            if verbosity>=3:
                print('Doing sample {}...'.format(sample.name))
            if sample.detector=='BOTH' or  sample.detector=='WAXS':
                sample.do_WAXS_measure()

                
    ###############The new alignement procedure.                   
    #def doSamples(self, step=0, verbosity=3):

        #if step<10:
            #self.alignSamples_Custom(step=step)
        
        #if step<15:
            #for sample in self.getSamples():
                #if verbosity>=3:
                    #print('Doing sample {}...'.format(sample.name))
                #if sample.detector=='SAXS' or sample.detector=='SAXS':
                    #sample.do_SAXS_only()

            #for sample in self.getSamples():
                #if verbosity>=3:
                    #print('Doing sample {}...'.format(sample.name))
                #if sample.detector=='WAXS' or sample.detector=='SAXS':
                    #sample.do_WAXS_only()

    def doTemperatures(self, step=0, reset_clock=True, temperature_heat_list=[100], temperature_cool_list=[100, 45],temperature_list=None, tiling=None, output_file='Transmission_output', int_measure=False, wait_time=600, temperature_probe='A', output_channel='1', temperature_tolerance=1,  temp_tolerance=1, poling_period=2.0, verbosity=3,**md):

        #cms.modeMeasurement()
        if temperature_list==None:
            temperature_list = self.temperature_list

        if reset_clock==True:
            for sample in self.getSamples():
                sample.reset_clock()
        #RT
        if step < 1:

            self.doSamples()            

        #heating
        if step < 5:
            for index, temperature in enumerate(temperature_heat_list):
                # Set new temperature
                self.setTemperature(temperature, output_channel=output_channel, verbosity=verbosity)
                
                # Wait until we reach the temperature
                start_time = time.time()
                while abs(self.temperature(temperature_probe=temperature_probe, verbosity=0) - temperature)>temperature_tolerance and time.time()-start_time<1000:
                    if verbosity>=3:
                        print('  setpoint = {:.3f}°C, Temperature = {:.3f}°C          \r'.format(self.temperature_setpoint()-273.15, self.temperature(temperature_probe=temperature_probe, verbosity=0)), end='')
                    time.sleep(poling_period)
                    
                # Allow for additional equilibration at this temperature
                sam=self.gotoSample(1)
                sam.xr(0.2)
                sam.setOrigin['x']
                sam.do_SAXS()
                sam.do_WAXS_measure()

        #max T=150
        if step < 10:
            temperature=150
            self.setTemperature(temperature, output_channel=output_channel, verbosity=verbosity)
            
            # Wait until we reach the temperature
            start_time = time.time()
            while abs(self.temperature(temperature_probe=temperature_probe, verbosity=0) - temperature)>temperature_tolerance and time.time()-start_time<1000:
                if verbosity>=3:
                    print('  setpoint = {:.3f}°C, Temperature = {:.3f}°C          \r'.format(self.temperature_setpoint()-273.15, self.temperature(temperature_probe=temperature_probe, verbosity=0)), end='')
                time.sleep(poling_period)

            start_time_150 = time.time()    
            self.doSamples()         

            while time.time() - start_time_150< 3600*3:
                sam=self.gotoSample(1)
                sam.xr(0.2)
                sam.setOrigin['x']
                sam.do_SAXS()
                sam.do_WAXS_measure()
                time.sleep(60*15)

        #cooling
        if step < 15:
            for index, temperature in enumerate(temperature_cool_list):
                # Set new temperature
                self.setTemperature(temperature, output_channel=output_channel, verbosity=verbosity)
                
                # Wait until we reach the temperature
                start_time = time.time()
                while abs(self.temperature(temperature_probe=temperature_probe, verbosity=0) - temperature)>temperature_tolerance and time.time()-start_time<1000:
                    if verbosity>=3:
                        print('  setpoint = {:.3f}°C, Temperature = {:.3f}°C          \r'.format(self.temperature_setpoint()-273.15, self.temperature(temperature_probe=temperature_probe, verbosity=0)), end='')
                    time.sleep(poling_period)
                    
                # Allow for additional equilibration at this temperature
                sam=self.gotoSample(1)
                sam.xr(0.2)
                sam.setOrigin['x']
                sam.do_SAXS()
                sam.do_WAXS_measure()                


        if step < 20:
            temperature=45
            self.setTemperature(temperature, output_channel=output_channel, verbosity=verbosity)
            
            # Wait until we reach the temperature
            start_time = time.time()
            while abs(self.temperature(temperature_probe=temperature_probe, verbosity=0) - temperature)>temperature_tolerance and time.time()-start_time<1000:
                if verbosity>=3:
                    print('  setpoint = {:.3f}°C, Temperature = {:.3f}°C          \r'.format(self.temperature_setpoint()-273.15, self.temperature(temperature_probe=temperature_probe, verbosity=0)), end='')
                time.sleep(poling_period)

            self.doSamples()      

        if step < 25:
            self.setTemperature(25)
                
    def alignSamples_Custom(self, step=0, align_step=0, verbosity=3, **md):
    
        cali_sample=None

        #search the middle sample for a full alignment
        if step < 10:
            #cali_sample = self.getSample(1) 
            sample_pos_list = []
            for sample in self.getSamples():
                sample_pos_list.append(sample.position)
                cali_sample = sample
            hol_xcenter = min(sample_pos_list)/2+max(sample_pos_list)/2
            
            print(sample_pos_list)
            
            #locate the sample for alignning the holder
            for sample in self.getSamples():
                if abs(sample.position-hol_xcenter) < abs(cali_sample.position-hol_xcenter):
                    cali_sample = sample
                print('The current calibraion sample is {}'.format(cali_sample.name))

            print('The calibraion sample is {}'.format(cali_sample.name))
                
        if step < 15:
            #full alignment on cali_sample
            #cali_sample.align()
            saxs_on()
            get_beamline().modeAlignment()
            cali_sample.gotoOrigin()
            cali_sample.align(step=0)           
            cali_sample.gotoOrigin()
            #cali_sample.yo()
            #cali_sample.tho()

        #set the th and y of other samples
        if step < 20:
            for sample in self.getSamples():
                sample.setOrigin(['th', 'y'])
            
        #quickly align other samples
        if step < 30:
            cms.modeAlignment()
            for sample in self.getSamples():
                if sample != cali_sample:
                    
                    print('Aligning sample {}...'.format(sample.name))
                    sample.gotoOrigin()
                    sample.align_custom(step=align_step)   
                    sample.gotoOrigin()
                    #wsam()
    

#cms.SAXS.setCalibration([737, 1089], 2.8, [-65, -73])  #20190320, 
#cms.SAXS.setCalibration([737, 1089], 5.05, [-65, -73])  #20190320
#cms.SAXS.setCalibration([755, 1072], 5.05, [-65, -73])  #20191020
#cms.SAXS.setCalibration([748, 1680-590], 2.01, [-64, -73]) # 13.5 keV 
#cms.SAXS.setCalibration([756, 1074], 5.05, [-65, -73]) 
#cms.SAXS.setCalibration([754, 1075], 5.03, [-65, -73])  #20201021, 13.5 keV
# cms.SAXS.setCalibration([740, 1098], 3.0, [-65, -73]) 

if True:
    
    cali = CapillaryHolder(base=stg)
    #hol = CapillaryHolderCustom(base=stg)

    cali.addSampleSlot( Sample('Lab6_cali_5m_13.5kev'), 2.0 )
    cali.addSampleSlot( Sample('FL_screen'), 5.0 )
    cali.addSampleSlot( Sample('AgBH_cali_5m_13.5kev'), 7.0 )
    cali.addSampleSlot( Sample('AgBHCeO2_cali_5m_13.5kev'), 8.0 )
    cali.addSampleSlot( Sample('Empty'), 11.0 )


if True:
    
    hol1 = CapillaryHolder(base=stg)
    #hol = CapillaryHolderCustom(base=stg)

    # hol1.addSampleSlot( Sample('Empty'), 2 )
    # hol1.addSampleSlot( Sample('BAB-100'), 4 )
    # hol1.addSampleSlot( Sample('Cailaries_water'), 6 )
    # hol1.addSampleSlot( Sample('iPEG_41k'), 7 )
    # hol1.addSampleSlot( Sample('iPEG_35k_clean'), 8 )
    # hol1.addSampleSlot( Sample('iPEG_35k_PS'), 9 )
    # hol1.addSampleSlot( Sample('iPEG_35k_TFSI'), 10 )
    # hol1.addSampleSlot( Sample('iPEG_35k+0.5eq LITFSI'), 11 )
    # hol1.addSampleSlot( Sample('iPEG_35k_recovery #27'), 12 )
    # hol1.addSampleSlot( Sample('iPEG_35k_recovery #28'), 13 )
    # hol1.addSampleSlot( Sample('PS solution 1wt%'), 14 )
    # hol1.addSampleSlot( Sample('PS solution 0.1wt%'), 15 )
    # hol1 = CapillaryHolder(base=stg)

    
    # hol = CapillaryHolderCustom(base=stg)

    hol1.addSampleSlot( Sample('Sample1'), 1 )
    hol1.addSampleSlot( Sample('Sample2'), 2 )
    hol1.addSampleSlot( Sample('Sample3'), 4 )
    hol1.addSampleSlot( Sample('Sample4'), 6 )
    hol1.addSampleSlot( Sample('Sample5'), 7 )
    hol1.addSampleSlot( Sample('Sample6'), 9 )
    hol1.addSampleSlot( Sample('Sample7'), 11 )
    hol1.addSampleSlot( Sample('Sample8'), 13 )


if 0:
    
    # Example of a multi-sample holder
    
    md = {
        'owner' : 'beamline' ,
        'series' : 'various' ,
        }

    # hol1 = GIBar_Custom(base=stg)
    # hol1.addGaragePosition(1,1)
    # hol1.name = 'hol1'
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s1', **md),1, 10,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s2', **md),2, 18,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s3', **md),3, 33,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s4', **md),4, 52,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s5', **md),5, 64,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])


    # hol1 = GIBar_Custom(base=stg)
    # hol1.addGaragePosition(1,1)
    # hol1.name = 'hol1'
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s1', **md),1, 10,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s2', **md),2, 18,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s3', **md),3, 33,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s4', **md),4, 52,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])
    # hol1.addSampleSlotPosition( Sample('RL_Vladimir_s5', **md),5, 64,'BOTH', incident_angles=[0.05,0.08, 0.1, 0.12, 0.15])





    # hol2 = GIBar_Custom(base=stg)
    # hol2.addGaragePosition(1,2)
    # hol2.name = 'hol2'
    # hol2.addSampleSlotPosition( Sample('RL_Zhenyang_ILs1', **md),1, 16,'WAXS', incident_angles=[0.05, 0.08, 0.1, 0.15, 0.2])
    # hol2.addSampleSlotPosition( Sample('RL_Zhenyang_controls2', **md),2, 37,'WAXS', incident_angles=[0.05, 0.08, 0.1, 0.15, 0.2])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s1', **md),3, 48,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s2', **md),4, 58,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s3', **md),5, 66.5,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s4', **md),6, 73,'SAXS', incident_angles=[ 0.05, 0.08, 0.1, 0.12, 0.15])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s5', **md),7, 82,'SAXS', incident_angles=[ 0.05, 0.08, 0.1, 0.12, 0.15])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s6', **md),8, 90.5,'SAXS', incident_angles=[ 0.05, 0.08, 0.1, 0.12, 0.15])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s7', **md),9, 96.5,'SAXS', incident_angles=[ 0.05, 0.08, 0.1, 0.12, 0.15])
    # hol2.addSampleSlotPosition( Sample('RL_XY_SL_260519_s8', **md),9, 96.5,'SAXS', incident_angles=[ 0.05, 0.08, 0.1, 0.12, 0.15])


    # hol3 = GIBar_Custom(base=stg)
    # hol3.addGaragePosition(1,3)
    # hol3.name = 'hol3'
    # hol3.addSampleSlotPosition( Sample('RL_XY_SL_260519_s9', **md),1, 4,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol3.addSampleSlotPosition( Sample('RL_XY_SL_260519_s10', **md),2, 13,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol3.addSampleSlotPosition( Sample('RL_XY_SL_260519_s11', **md),3, 21,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol3.addSampleSlotPosition( Sample('RL_XY_SL_260519_s12', **md),4, 29.5,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol3.addSampleSlotPosition( Sample('RL_XY_SL_260519_s13', **md),5, 37,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # hol3.addSampleSlotPosition( Sample('RL_XY_SL_260519_s14', **md),6, 44.5,'SAXS', incident_angles=[0.05, 0.08, 0.1, 0.12, 0.15])
    # # hol3.addSampleSlotPosition( Sample('RL_Duke_intermidiate_s1', **md),7, 60,'WAXS', incident_angles=[ 0.1, 0.15, 0.2, 0.25, 0.5])
    # hol3.addSampleSlotPosition( Sample('RL_Duke_intermidiate_s2', **md),8, 74,'WAXS', incident_angles=[ 0.1, 0.15, 0.2, 0.25, 0.5])
    # hol3.addSampleSlotPosition( Sample('RL_Duke_intermidiate_s3', **md),9, 88,'WAXS', incident_angles=[ 0.1, 0.15, 0.2, 0.25, 0.5])




    

    que = Queue(base=stg)



    que.addHolderIntoQueue(hol3, [1, 1], 1)   
    # que.addHolderIntoQueue(hol2, [1, 2], 2)   
    # que.addHolderIntoQueue(hol3, [1, 3], 3) 
    # # que.addHolderIntoQueue(hol4, [1, 2], 4)
    # que.addHolderIntoQueue(hol1, [2, 1], 5)   
    # que.addHolderIntoQueue(hol8, [2, 3], 6)   
    # que.addHolderIntoQueue(hol9, [3, 1], 7)   
    # que.addHolderIntoQueue(hol10, [3, 2], 8)   
    # que.addHolderIntoQueue(hol11, [3, 3], 9)  
    # que.addHolderIntoQueue(hol12, [4, 1], 10)  
    # que.addHolderIntoQueue(hol13, [4, 2], 11)  
    # que.addHolderIntoQueue(hol12, [4, 3], 12)  

     

    que.setSequence()  
    que.checkStatus(verbosity=5) 


# sam=Sample('test')
# detselect([fs4])
# sam.measure(1)

'''
2025_1

rod
In [132]: wbs()
bsx = -11.000014
bsy = 17.0005
bsphi = -181.50260699999998






#new beamstop setup at 2023C2

rod bs

In [69]: wbs()
bsx = -13.10041
bsy = 14.500015
bsphi = -178.00030500000003

round bs 

In [90]: wbs()
bsx = -16.700347
bsy = -0.1998869999999997
bsphi = -19.999025000000003


que.runHolders()


#cali.origin
In [89]: wsam()
smx = -16.2
smy = -2.0
sth = 0.0


In [425]: hol6.saveSampleStates()
Out[425]: 
{1: {'origin': {'x': 7.0, 'y': 0.04625000000000057, 'th': -0.137109375}},
 2: {'origin': {'x': 23.0, 'y': 0.050050000000000594, 'th': -0.148515625}},
 3: {'origin': {'x': 40.0, 'y': 0.08125000000000071, 'th': 0.080390625}},
 4: {'origin': {'x': 55.0, 'y': 0.0, 'th': 0.0}},
 5: {'origin': {'x': 72.0, 'y': 0.0, 'th': 0.0}},
 6: {'origin': {'x': 88.0, 'y': 0.0, 'th': 0.0}}}


 


cms.ventSample()
cms.pumpSample()

#Click the tiny green button once, then in the "800k" tab, click  ctrl+X twice to restart the WAXS detector

an alternative solution is : startWAXS()

ctrl+S to save the scripts first, then
"%run -i ..."  to reload the scripts
%
y
n
hol1
y


hol1.listSamples()   #check sample name has been updated
hol1.gotoOrigin()    #goto hol1 origin
hol1.yr(-4)          #lower the bar
hol1.setOrigin('y')  #reset the origin
hol2.setOrigin('y')
..

que.runHolders()


history




'''


'''
#change sample
#put tensile onto sample stage, push it down to the end and close chamber
cms.pumpChamber() # pump chamber
startWAXS() #start WAXS detector 
sam=Sample('test')
#define the tensile protocol
sam.series_measure(num_frames=110, exposure_time=9.99, exposure_period=10)
cms.ventChamber()

'''