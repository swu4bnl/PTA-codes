#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Imports
########################################

import sys, os
# Update this to point to the directory where you copied the SciAnalysis base code
#SciAnalysis_PATH='/home/kyager/current/code/SciAnalysis/main/'
SciAnalysis_PATH='/Users/carlyzincone/Desktop'
SciAnalysis_PATH in sys.path or sys.path.append(SciAnalysis_PATH)

import glob
from SciAnalysis import tools
from SciAnalysis.XSAnalysis.Data import *
from SciAnalysis.XSAnalysis import Protocols
import time



# Define some custom analysis routines
########################################
# TBD
######################### Carly

class circular_average_q2I_fit_sorted(Protocols.circular_average_q2I_fit):
    """Subclass of circular_average_q2I_fit that sorts fitted peak positions in ascending q order.
    Useful when num_curves>=2 and the optimizer may return peaks in arbitrary order."""

    def _fit(self, line, results, **run_args):
        # Run the standard lmfit-based fitting
        lines = super()._fit(line, results, **run_args)

        num_curves = run_args.get('num_curves', 1)
        if num_curves >= 2:
            fit_name = 'fit_peaks'

            # Collect each peak's parameter set
            peaks = []
            for i in range(num_curves):
                peaks.append({
                    'x_center':   results.get('{}_x_center{}'.format(fit_name, i + 1)),
                    'prefactor':  results.get('{}_prefactor{}'.format(fit_name, i + 1)),
                    'sigma':      results.get('{}_sigma{}'.format(fit_name, i + 1)),
                    'd0':         results.get('{}_d0{}'.format(fit_name, i + 1)),
                    'grain_size': results.get('{}_grain_size{}'.format(fit_name, i + 1)),
                })

            # Sort ascending by q (x_center value)
            peaks_sorted = sorted(peaks, key=lambda p: p['x_center']['value'])

            # Write sorted peaks back into results (same dict reference â also updates lines.results)
            for i, peak in enumerate(peaks_sorted):
                results['{}_x_center{}'.format(fit_name, i + 1)]  = peak['x_center']
                results['{}_prefactor{}'.format(fit_name, i + 1)] = peak['prefactor']
                results['{}_sigma{}'.format(fit_name, i + 1)]     = peak['sigma']
                results['{}_d0{}'.format(fit_name, i + 1)]        = peak['d0']
                results['{}_grain_size{}'.format(fit_name, i + 1)]= peak['grain_size']

            # Refresh single-peak aliases to point to the lowest-q peak
            results['{}_d0'.format(fit_name)]         = results['{}_d01'.format(fit_name)]
            results['{}_grain_size'.format(fit_name)] = results['{}_grain_size1'.format(fit_name)]
        return lines

class circular_average_q2I_fit_FWHM(circular_average_q2I_fit_sorted):
    """Same Gaussian peak fit as circular_average_q2I_fit_sorted, but also
    computes the FWHM (in q, Å⁻¹) for each peak: FWHM = 2*sqrt(2*ln2)*sigma,
    and annotates it on the fit plot."""

    def _fit(self, line, results, **run_args):
        lines = super()._fit(line, results, **run_args)

        fit_name = 'fit_peaks'
        FWHM_factor = 2.0 * np.sqrt(2.0 * np.log(2.0))  # ≈ 2.35482
        num_curves = run_args.get('num_curves', 1)

        for i in range(num_curves):
            sigma_res = results.get('{}_sigma{}'.format(fit_name, i + 1))
            if sigma_res is None:
                continue
            sigma = sigma_res['value']
            sigma_err = sigma_res.get('error')

            fwhm = FWHM_factor * sigma
            if sigma_err is None or np.isnan(sigma_err):
                fwhm_err = 0
            else:
                fwhm_err = FWHM_factor * sigma_err

            results['{}_fwhm{}'.format(fit_name, i + 1)] = {'value': fwhm, 'error': fwhm_err}
            print('  Peak {}: q0 = {:.4f} Å⁻¹, sigma = {:.5f}, FWHM = {:.5f} Å⁻¹'.format(
                i + 1, results['{}_x_center{}'.format(fit_name, i + 1)]['value'], sigma, fwhm))

            # --- Model-free FWHM cross-check (data-based, no Gaussian assumption) ---
            # Uses the same line that was fed to the fit, within the fit_range.
        try:
            xs = np.asarray(line.x)
            ys = np.asarray(line.y)

            # Restrict to the fit range so we measure the same peak the fit saw
            if 'fit_range' in run_args:
                lo, hi = run_args['fit_range']
                m = (xs >= lo) & (xs <= hi)
                xs, ys = xs[m], ys[m]

            # Linear background from the two endpoints of the range
            bg = ys[0] + (ys[-1] - ys[0]) * (xs - xs[0]) / (xs[-1] - xs[0])
            yb = ys - bg

            ipeak = np.argmax(yb)
            qpeak = xs[ipeak]
            half = yb[ipeak] / 2.0

            # Walk left from the peak to the half-max crossing, interpolate
            il = ipeak
            while il > 0 and yb[il] > half:
                il -= 1
            ql = np.interp(half, [yb[il], yb[il + 1]], [xs[il], xs[il + 1]])

            # Walk right
            ir = ipeak
            while ir < len(yb) - 1 and yb[ir] > half:
                ir += 1
            qr = np.interp(half, [yb[ir], yb[ir - 1]], [xs[ir], xs[ir - 1]])

            fwhm_data = abs(qr - ql)
            fwhm_fit = results.get('{}_fwhm1'.format(fit_name), {}).get('value', float('nan'))
            diff_pct = 100.0 * (fwhm_data - fwhm_fit) / fwhm_fit if fwhm_fit else float('nan')

            print('  FWHM fit  = {:.5f} Å⁻¹'.format(fwhm_fit))
            print('  FWHM data = {:.5f} Å⁻¹  (peak at q={:.4f})'.format(fwhm_data, qpeak))
            print('  difference = {:+.1f}%'.format(diff_pct))

            results['{}_fwhm1_data'.format(fit_name)] = {'value': fwhm_data, 'error': 0}
        except Exception as e:
            print('  Model-free FWHM check skipped: {}'.format(e))
        # --- end cross-check ---
        # Add FWHM annotation by subclassing the DataLines object's own class,
        # so the parent's _plot_extra still runs and ours adds to it.
        parent_cls = type(lines)

        # Add FWHM annotation by subclassing the DataLines object's own class,
        # so the parent's _plot_extra still runs and ours adds to it.
        parent_cls = type(lines)
        n_curves = num_curves

        class DataLines_fwhm(parent_cls):
            def _plot_extra(self, **plot_args):
                super()._plot_extra(**plot_args)  # parent's q0/d/sigma/chi2 labels
                try:
                    xi, xf, yi, yf = self.ax.axis()
                    v_spacing = (yf - yi) * 0.06
                    for i in range(n_curves):
                        fwhm_res = self.results.get('{}_fwhm{}'.format(fit_name, i + 1))
                        q0_res = self.results.get('{}_x_center{}'.format(fit_name, i + 1))
                        pref_res = self.results.get('{}_prefactor{}'.format(fit_name, i + 1))
                        if fwhm_res is None or q0_res is None:
                            continue
                        q0 = q0_res['value']
                        fwhm = fwhm_res['value']

                        # half-max level: local background + half peak height
                        bg = 0.0
                        m_res = self.results.get('{}_m'.format(fit_name))
                        b_res = self.results.get('{}_b'.format(fit_name))
                        if m_res is not None and b_res is not None:
                            bg = m_res['value'] * q0 + b_res['value']
                        height = pref_res['value'] if pref_res is not None else (yf - yi)
                        y_half = bg + height / 2.0

                        self.ax.annotate('', xy=(q0 - fwhm / 2.0, y_half),
                                         xytext=(q0 + fwhm / 2.0, y_half),
                                         arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
                        s = r'$\mathrm{{FWHM}}_{{ {:d} }} = \, {:.4f} \, \mathrm{{\AA}}^{{-1}}$'.format(i + 1, fwhm)
                        self.ax.text(xi, yf - v_spacing * (i + 1), s, size=15, color='green',
                                     verticalalignment='top', horizontalalignment='left')
                    self.ax.axis([xi, xf, yi, yf])
                except Exception as e:
                    print('  FWHM annotation skipped: {}'.format(e))

        lines.__class__ = DataLines_fwhm
        return lines

    ######################### Carly


# Experimental parameters
########################################

if False:
    # PhotonicSciences CCD
    from SciAnalysis.XSAnalysis.DataRQconv import *
    calibration = CalibrationRQconv(wavelength_A=0.9184) # 13.5 keV
    calibration.set_image_size(1042) # psccd Photonic Sciences CCD
    calibration.set_pixel_size(pixel_size_um=101.7)
    calibration.set_distance(0.232) # Bigger number moves theory rings outwards (larger spacing)
    calibration.set_beam_position(22.0, 1042-22.0)
    calibration.set_angles(det_orient=45, det_tilt=-21, det_phi=0, incident_angle=0., sample_normal=0.)
    print('ratio Dw = {:.3f}'.format(calibration.get_ratioDw()))

    #mask_dir = SciAnalysis_PATH + '/SciAnalysis/XSAnalysis/masks/'
    #mask = Mask(mask_dir+'CCD/psccd_generic-mask.png')
    
else:
    # Custom Dectris Pilatus 800k (lower-left modules removed)
    calibration = Calibration(wavelength_A=0.7294) # 17 keV
    
    #calibration = Calibration(wavelength_A=0.9184) # 13.5 keV
    calibration.set_image_size(981, height=1043) # Pilatus800k
    calibration.set_pixel_size(pixel_size_um=172.0)
    
    # Scan 63335
    #calibration.set_beam_position(461, 1043-400)
    #calibration.set_distance(0.259) 
    
    # Scan 71857
    #calibration.set_beam_position(457, 1043-383) # 71857
    # calibration.set_beam_position(472, 1043-412) # 71857
    #calibration.set_distance(0.256)
    calibration.set_beam_position(255, 1043-272) # 71857
    calibration.set_distance(0.256)

    mask_dir = SciAnalysis_PATH + '/SciAnalysis/SciAnalysis/XSAnalysis/masks/'
    mask = Mask(mask_dir+'Dectris/Pilatus800k_gaps-mask.png')
    mask.load('/Users/carlyzincone/Desktop/RESEARCH/Local Computer Beamline Data/cms data/20251210_CMS_SSMD/1_GISAXS_static/waxs/analysis/mask3.png')





# Files to analyze
########################################
# source_dir = '../stitched/'
source_dir = '/Users/carlyzincone/Desktop/RESEARCH/Local Computer Beamline Data/cms data/20251210_CMS_SSMD/1_GISAXS_static/waxs/raw/AlCuNiAl'
output_dir = '/Users/carlyzincone/Desktop/RESEARCH/Local Computer Beamline Data/cms data/20251210_CMS_SSMD/1_GISAXS_static/waxs/analysis'

#pattern = '*flaton*'
#pattern = 'Ag*'
pattern = '*cc68*'
#pattern = '*71857*'

infiles = glob.glob(os.path.join(source_dir, pattern +'.tiff'))
infiles.sort()


# Analysis to perform
########################################

load_args = { 'calibration' : calibration,
             'mask' : mask,
             #'rot180' : False,
             #'flip' : False, # PSCCD
             }
run_args = { 'verbosity' : 3,
            'save_results' : ['xml', 'plots', 'txt', 'hdf5'],
             }



#qp1, dqp1 = 2.83, 0.04 #V peak4
qp1, dqp1 = 2.2, 0.03 #Al peak
qp1, dqp1 = 1.8, 0.04 # Cu SS peak

qp1, dqp1 = 3.58, 0.07 # Ni3Al peak
qp1, dqp1 = 3.1, 0.07 # Cu4Al9 peak to Ni or Ni3Al
qp1, dqp1 = 3.114, 0.06 # CuAL intermetallics --> SS --> Ni or Ni3Al
qp1, dqp1 = 3.113, 0.13   # 2.983 to 3.243; center on real peak, give wide peaks room

process = Protocols.ProcessorXS(load_args=load_args, run_args=run_args)
# Examples:
#protocols = [ Protocols.circular_average_q2I(plot_range=[0, 0.2, 0, None]) ]
#protocols = [ Protocols.linecut_angle(q0=0.01687, dq=0.00455*1.5, show_region=False) ]
#protocols = [ Protocols.q_image(blur=1.0, bins_relative=0.5, plot_range=[-0.1, 3.0, 0, 3.0], _xticks=[0, 1.0, 2.0, 3.0], ztrim=[0.2, 0.01]) ]
#protocols = [ Protocols.qr_image(blur=1.0, bins_relative=0.5, plot_range=[-0.1, 3.0, 0, 3.0], _xticks=[0, 1.0, 2.0, 3.0], zmin=1010., ztrim=[None, 0.01]) ]
#protocols = [ Protocols.qr_image(blur=None, bins_relative=0.8, plot_range=[-0.1, 3.0, 0, 3.0], _xticks=[0, 1.0, 2.0, 3.0], ztrim=[0.38, 0.002], dezing_fill=True) ]
#protocols = [ Protocols.q_phi_image(bins_relative=0.25, plot_range=[0, 3.0, 0, +90]) ]
# Protocols.sector_average(angle=-70, dangle=25, show_region=False)
# Protocols.qr_image(blur=None, colorbar=True, save_data=False, transparent=False, label_filename=True)
# Protocols.linecut_q(chi0= 90+70, dq= .5, gridlines=True, label_filename=True, save_results = [ 'hdf5' ] )
# Protocols.HDF5(  save_results = [ 'hdf5' ] )
# Protocols.metadata_extract()

protocols = [
    #Protocols.HDF5(save_results=['hdf5'])
    #Protocols.calibration_check(show=False, AgBH=True, q0=1.076, dq=0.01, num_rings=10, ztrim=[0.2, 0.01], dpi=300) ,
    #Protocols.circular_average(ylog=False, plot_range=[0.5, 4, 0, None], dezing= False) ,
    # Protocols.thumbnails(crop=None, resize=0.5, cmap=cmap_vge, ztrim=[0.06, 0.001], zmin=1000.0) , # PSCCD
    #Protocols.thumbnails(crop=None, resize=1, cmap=cmap_vge, ztrim=[0.02, 0.0001]) , # Pilatus800k
    #Protocols.q_image(blur=None, bins_relative=0.5, plot_range=[-0.1, 3.0, 0, 3.0], _xticks=[0, 1.0, 2.0, 3.0], ztrim=[0.2, 0.01]) ,
    #Protocols.qr_image(blur=None, bins_relative=0.5, plot_range=[-1, 2.5, -.1, 3], ztrim=[0.2, 0.01]) ,
    # # Protocols.sector_average(name = 'qr_int', angle=75, dangle=30, plot_range=[0, 3.5, 0, None],show_region=False) ,
    # # Protocols.sector_average(name = 'qz_int', angle=0, dangle=30, plot_range=[0, 3.5, 0, None],show_region=False) ,
    #Protocols.qr_image(name='qr_images2', blur=None, bins_relative=0.5, plot_range=[-1, 2.5, -.1, 3], zmin=10, zmax=1000, save_results=['npz']) ,
    #Protocols.circular_average_q2I_fit(name='3.1 peakchange',plot_range=[3.0, 3.35, 0, None], q0 = qp1, fit_range=[qp1-dqp1, qp1+dqp1])
    ###circular_average_q2I_fit_custom('circular_average_q2I_fit', plot_range=[1, 4.5, 0, None], q0=qp1, fit_range=[qp1 - dqp1, qp1 + dqp1], num_curves=1), ### sometimes create Nan results and will be skipped by gpcam; we used Scipy to generate reasonable number
    #### But scipy always gives u value even if fitting sucks
    #circular_average_q2I_fit_sorted('circular_average_q2I_fit_sorted', plot_range=[3.3,3.7, 0, None], q0=qp1, fit_range=[qp1 - dqp1, qp1 + dqp1], num_curves=1), # c
    ####### gives us enough data ; if we have less3 data points then we should use custom (Scipy)
    circular_average_q2I_fit_FWHM('circular_average_q2I_fit_FWHM', plot_range=[3.0, 3.35, 0, None], q0=qp1, fit_range=[qp1-dqp1, qp1+dqp1], num_curves=1),
]

# To stitch files:
# 1) run stitch.py to stitch 0
# into .TIFF
# 2) run runStitched.py to generate thumbnails etc


# Run
########################################
print('Processing {} infiles...'.format(len(infiles)))
process.run(infiles, protocols, output_dir=output_dir, force=False)


# Loop
########################################
# This is typically only used at the beamline (it loops forever, watching for new files).
#process.monitor_loop(source_dir=source_dir, pattern='*.tiff', protocols=protocols, output_dir=output_dir, force=False)
