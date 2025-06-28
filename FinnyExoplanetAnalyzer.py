import lightkurve
import numpy
import matplotlib.pyplot as plot
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import matplotlib
from cycler import cycler
import datetime
import os
import time

from lightkurve import search_targetpixelfile, DesignMatrix, RegressionCorrector
from astropy.visualization import ZScaleInterval

from Exoplanet import Exoplanet
plot.style.use('seaborn-v0_8')
# new stars: https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html

class FinnyExoplanetAnalyzer:
    def __init__(self, star, auto_mode = False, auto_folder = None):
        self.star = star
        self.exoplanets = {}
        self.exoplanet_letter = 'b'

        self.mask_indices = {}
        self.masks = {}
        self.mask_dfs = {}

        self.models = {}
        self.model_dfs = {}

        self.auto_mode = auto_mode
        self.auto_folder = auto_folder

        if auto_folder is not None and not os.path.exists(f'{self.auto_folder}'):
            os.makedirs(f'{self.auto_folder}', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/light_curve_collections', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/stitched_light_curves', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/first_light_curve', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/periodograms', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/folded_light_curves', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/transit_depths', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/save_data', exist_ok = True)
            os.makedirs(f'{self.auto_folder}/single_view', exist_ok = True)

        matplotlib.rcParams['figure.figsize'] = (12, 8)
        matplotlib.rcParams['font.size'] = 14
        matplotlib.rcParams['axes.prop_cycle'] = cycler(color = ['black'] + matplotlib.rcParams['axes.prop_cycle'].by_key()['color'][1:])

    def plot_tesscut(self, save_in_auto = True):
        # plot.figure(figsize = (16, 9))
        plot.title(f'{self.star} TESScut')
        tesscut = lightkurve.search_tesscut(self.star, sector = 24)
        pixel_file = tesscut.download(cutout_size = 30)

        if pixel_file is None:
            print(f'No pixel file Found for {self.star}')
            exit()

        aperture_mask = pixel_file.create_threshold_mask(threshold = 10, reference_pixel = 'center')

        vmin, vmax = ZScaleInterval().get_limits(pixel_file.flux[0])

        image = plot.imshow(pixel_file.flux[0].value, origin = 'lower', cmap = 'cividis', vmin = vmin, vmax = vmax)
        # masked_pixels = numpy.where(aperture_mask)
        # plot.scatter(masked_pixels[1], masked_pixels[0], color = 'C1', s = 20, marker = 's', label = 'Aperture Mask')
        masked_pixels = numpy.argwhere(aperture_mask)
        for y, x in masked_pixels:
            # Draw a rectangle around each masked pixel
            rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth = 1, edgecolor = 'C1', facecolor = 'none')
            plot.gca().add_patch(rect)

            # Draw diagonal lines inside each pixel box
            plot.plot([x - 0.5, x + 0.5], [y - 0.5, y + 0.5], 'C1-', lw = 0.7)  # Bottom-left to top-right
            plot.plot([x + 0.5, x - 0.5], [y - 0.5, y + 0.5], 'C1-', lw = 0.7)  # Top-left to bottom-right

        cbar = plot.colorbar(image, fraction = 0.046, pad = 0.04)  # Adjust fraction and pad for sizing
        cbar.set_label(r'Flux (e$^{-}$s$^{-1}$)')

        plot.xlabel('X Pixels')
        plot.ylabel('Y Pixels')

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                if not os.path.exists(f'{self.auto_folder}/tesscuts'):
                    os.makedirs(f'{self.auto_folder}/tesscuts', exist_ok = True)

                plot.savefig(f'{self.auto_folder}/tesscuts/{plot.gca().get_title()} @{datetime.datetime.now()}.png', dpi = 100)

            plot.close()

        exit()

    def create_light_curve(self, limit = 5):
        self.search_result = search_targetpixelfile(self.star, mission = 'TESS', cadence = 'long', limit = limit)

        if len(self.search_result) == 0:
            return None

        self.pixel_files = self.search_result[:limit].download_all() # precaution even though there is already a limit

        self.collection = lightkurve.LightCurveCollection(None)

        if self.pixel_files is None:
            return None

        for pixel_file in self.pixel_files:
            pixel_file = pixel_file[numpy.isfinite(pixel_file.flux).all(axis = (1, 2))]
            uncorrected_lc = pixel_file.to_lightcurve(aperture_mask = pixel_file.pipeline_mask)

            self.collection.append(uncorrected_lc)

            # design_matrix = DesignMatrix(pixel_file.flux[:, ~aperture_mask]).pca(5).append_constant()
            # lc = RegressionCorrector(uncorrected_lc).correct(design_matrix)
            # collection.append(lc.flatten(niters = 20))

        self.lc = self.collection.stitch().flatten(window_length = 501, break_tolerance = 10, niters = 1, sigma = 10).remove_outliers(sigma = 10)
        self.lc.flux_err = abs(self.lc.flux_err)
        self.lc_df = self.lc.to_pandas()

        self.flux_unc = self.lc_df['flux_err'].mean()

        return self.lc

    def create_periodogram(self, log_searchsize = [0.5, 1.7, 4]):
        log_searchsize[2] = int(log_searchsize[2])
        periods = numpy.logspace(log_searchsize[0], log_searchsize[1], 10 ** log_searchsize[2], base = 10)
        durations = numpy.logspace(log_searchsize[0] - 1, log_searchsize[0] - 0.5, 10, base = 10)

        self.p = self.lc.to_periodogram(method = 'boxleastsquares', period = periods, duration = durations, frequency_factor = 10 ** 6) # the actual periodogram for plot
        self.p_df = self.p.to_table().to_pandas()

        period = self.p.period_at_max_power.value # accurate period to find duration
        durations = numpy.logspace(numpy.log10(period) - 2, numpy.log10(period) - 0.5, 10 ** 4, base = 10)
        duration_periodogram = self.lc.to_periodogram(method = 'boxleastsquares', period = [period * 0.999, period, period * 1.0001], duration = durations, frequency_factor = 10 ** 6)

        period = duration_periodogram.period_at_max_power.value # find values from these
        duration = duration_periodogram.duration_at_max_power.value

        self.final_periodogram = self.lc.to_periodogram(
            method = 'boxleastsquares',
            period = [period * 0.999, period, period * 1.0001],
            duration = [duration * 0.999, duration, duration * 1.0001],
            frequency_factor = 10 ** 6
        )

        self.period = self.final_periodogram.period_at_max_power
        self.transit_time = self.final_periodogram.transit_time_at_max_power
        self.transit_duration = self.final_periodogram.duration_at_max_power

        print(f'period: {self.period}')
        print(f'transit_time: {self.transit_time}')
        print(f'transit_duration: {self.transit_duration}')

        self.period_fwhm_indices = self.p_df['power'] > self.p_df['power'].max() / 2
        self.period_fwhm = self.p_df.loc[self.period_fwhm_indices, 'period'].max() - self.p_df.loc[self.period_fwhm_indices, 'period'].min()
        self.period_unc = self.period_fwhm / 2

        print(f'period_unc: {self.period_unc}')

        self.snr = numpy.max(self.p.power.value) / numpy.std(self.p.power.value)
        self.transit_duration_unc = 24 * self.transit_duration.value / self.snr
        self.transit_time_unc = self.transit_duration.value / self.snr # but this in days, not barycentric days

        return self.p

    def fold_light_curve(self):
        self.folded_lc = self.lc.fold(period = self.period, epoch_time = self.transit_time)
        self.folded_lc_df = self.folded_lc.to_pandas()

        return self.folded_lc

    def create_transit_model(self, letter):
        self.models[letter] = self.final_periodogram.get_transit_model( # flat bottomed approximation
            period = self.period,
            transit_time = self.transit_time,
            duration = self.transit_duration
        )

        self.folded_model = self.models[letter].fold(self.period, self.transit_time)

        self.model_dfs[letter] = self.models[letter].to_pandas()
        self.folded_model_df = self.folded_model.to_pandas()

        return self.folded_model

    def plot_first_light_curve(self, save_in_auto = True):
        plot.title(f'{self.star} First Light Curve')

        legend = [f'{self.star} first light curve']

        lc = self.collection[0]
        lc_df = lc.to_pandas()
        plot.errorbar(lc_df.index, lc_df['flux'], yerr = lc_df['flux_err'], ms = 4, elinewidth = 0.25, fmt = 'o', color = 'C0', zorder = 0)

        plot.xlabel('Time (BJD - 2457000)')
        plot.ylabel(r'Flux (e$^{-}$s$^{-1}$)')

        plot.legend(legend)

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                self.savefig('first_light_curve')

            plot.close()

        time.sleep(0.1)

    def plot_collection(self, save_in_auto = True):
        # plot.figure(figsize = (16, 9))
        plot.title(f'{self.star} Light Curve Collection')

        legend = []

        for i, lc in enumerate(self.collection):
            lc_df = lc.to_pandas()
            plot.scatter(lc_df.index, lc_df['flux'], s = 2)
            legend.append(f'{self.star} light curve #{i + 1}')

        plot.xlabel('Time (BJD - 2457000)')
        plot.ylabel(r'Flux (e$^{-}$s$^{-1}$)')

        if len(self.collection) < 10:
            plot.legend(legend)

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                self.savefig('light_curve_collections')

            plot.close()

        time.sleep(0.1)

    def plot_stitched_light_curve(self, save_in_auto = True):
        # plot.figure(figsize = (16, 9))
        plot.title(f'{self.star} Light Curve')

        plot.scatter(self.lc_df.index, self.lc_df['flux'], s = 2)

        legend = ['light curve']

        plot.xlabel('Time (BJD - 2457000)')
        plot.ylabel('Normalized Flux')

        plot.legend(legend)

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                self.savefig('stitched_light_curves')

            plot.close()

        time.sleep(0.1)

    def plot_periodogram(self, save_in_auto = True):
        # plot.figure(figsize = (16, 9))
        plot.title(f'{self.star} Periodogram')

        legend = ['power', 'max_power', 'half_max']

        plot.plot(self.p_df['period'], self.p_df['power'], linewidth = 1, color = 'C0')
        plot.plot(self.p_df['period'], numpy.linspace(self.p.max_power, self.p.max_power, len(self.p_df['period'])), linewidth = 3, color = 'C1')
        plot.plot(self.p_df.loc[self.period_fwhm_indices, 'period'], numpy.linspace(self.p.max_power / 2, self.p.max_power / 2, len(self.p_df.loc[self.period_fwhm_indices, 'period'])), linewidth = 3, color = 'C2')

        plot.xlabel('Period')
        plot.ylabel('Power')
        plot.legend(legend)

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                self.savefig('periodograms')

            plot.close()

        time.sleep(0.1)

    def plot_folded_light_curve(self, overlay_current_model = True, overlay_bin = True, save_in_auto = True):
        # plot.figure(figsize = (16, 9))
        plot.title(f'{self.star} Folded Light Curve')

        legend = ['folded light curve']

        plot.errorbar(self.folded_lc_df.index, self.folded_lc_df['flux'], yerr = self.folded_lc_df['flux_err'], ms = 2, elinewidth = 0.25, fmt = 'o', color = 'C0', zorder = 0)

        if overlay_current_model:
            plot.plot(self.folded_model_df.index, self.folded_model_df['flux'], linewidth = 3, color = 'C1')
            legend.append(f'{self.star} {self.exoplanet_letter} transit model')

        if overlay_bin:
            binned_folded_lc = self.folded_lc.bin((self.folded_lc_df.index.max() - self.folded_lc_df.index.min()) / 256)
            binned_folded_lc_df = binned_folded_lc.to_pandas()
            plot.plot(binned_folded_lc_df.index, binned_folded_lc_df['flux'], linewidth = 3, color = 'C2', linestyle = '--')
            legend.append('binned light curve')

        plot.xlabel('Phase (days)')
        plot.ylabel('Normalized Flux')
        plot.legend(legend)

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                self.savefig('folded_light_curves')

            plot.close()

        '''
        fig, ax = plot.subplots(subplot_kw = {'projection': '3d'}, figsize = (16, 9))
        print(numpy.array(self.folded_lc.time.value).flatten())
        print(numpy.array(self.folded_lc.flux.value).flatten())
        print(numpy.array(self.folded_lc.phase.value).flatten())
        ax.scatter(
            numpy.floor_divide(self.lc_df.index - self.transit_time.value.item(), self.period),
            numpy.mod(self.lc_df.index - self.transit_time.value.item(), self.period),
            self.folded_lc_df['flux'],
            cmap = 'viridis', marker = 'o', label = 'Folded Light Curve', alpha = 0.25, s = 2.5)
        plot.show(); exit()
        '''

        time.sleep(0.1)

    def plot_single_view(self, overlay_current_model = True, overlay_bin = True, save_in_auto = True):
        fig = plot.figure(figsize = (24, 8))
        grid = GridSpec(2, 2, figure = fig, width_ratios = [1, 1])
        axes = [
            fig.add_subplot(grid[:, 0]),
            fig.add_subplot(grid[0, 1]),
            fig.add_subplot(grid[1, 1])
        ]

        axes[0].set_title(f'{self.star} First Light Curve')

        legend = [f'{self.star} first light curve']

        lc = self.collection[0]
        lc_df = lc.to_pandas()
        axes[0].errorbar(lc_df.index, lc_df['flux'], yerr = lc_df['flux_err'], ms = 4, elinewidth = 0.25, fmt = 'o', color = 'C0', zorder = 0)

        axes[0].set_xlabel('Time (BJD - 2457000)')
        axes[0].set_ylabel(r'Flux (e$^{-}$s$^{-1}$)')

        axes[0].legend(legend)

        axes[1].set_title(f'{self.star} Folded Light Curve')

        legend = ['folded light curve']

        axes[1].errorbar(self.folded_lc_df.index, self.folded_lc_df['flux'], yerr = self.folded_lc_df['flux_err'], ms = 2, elinewidth = 0.25, fmt = 'o', color = 'C0', zorder = 0)

        if overlay_current_model:
            axes[1].plot(self.folded_model_df.index, self.folded_model_df['flux'], linewidth = 3, color = 'C1')
            legend.append(f'{self.star} {self.exoplanet_letter} transit model')

        if overlay_bin:
            binned_folded_lc = self.folded_lc.bin((self.folded_lc_df.index.max() - self.folded_lc_df.index.min()) / 256)
            binned_folded_lc_df = binned_folded_lc.to_pandas()
            axes[1].plot(binned_folded_lc_df.index, binned_folded_lc_df['flux'], linewidth = 3, color = 'C2', linestyle = '--')
            legend.append('binned light curve')

        axes[1].set_xlabel('Phase (days)')
        axes[1].set_ylabel('Normalized Flux')
        axes[1].legend(legend)

        axes[2].set_title(f'{self.star} Zoomed Folded Light Curve')

        legend = ['folded light curve']

        axes[2].errorbar(self.folded_lc_df.index, self.folded_lc_df['flux'], yerr = self.folded_lc_df['flux_err'], ms = 2, elinewidth = 0.25, fmt = 'o', color = 'C0', zorder = 0)

        if overlay_current_model:
            axes[2].plot(self.folded_model_df.index, self.folded_model_df['flux'], linewidth = 3, color = 'C1')
            legend.append(f'{self.star} {self.exoplanet_letter} transit model')

        if overlay_bin:
            binned_folded_lc = self.folded_lc.bin((self.folded_lc_df.index.max() - self.folded_lc_df.index.min()) / 256)
            binned_folded_lc_df = binned_folded_lc.to_pandas()
            axes[2].plot(binned_folded_lc_df.index, binned_folded_lc_df['flux'], linewidth = 3, color = 'C2', linestyle = '--')
            legend.append('binned light curve')

        axes[2].set_xlabel('Phase (days)')
        axes[2].set_ylabel('Normalized Flux')
        axes[2].set_xlim(-2 * self.transit_duration.value, 2 * self.transit_duration.value)
        axes[2].legend(legend)

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                self.savefig('single_view', title = f'{self.star} Single View')

            plot.close()

        time.sleep(0.1)

    def get_transit_depth(self):
        # FINDS MINIMUM BINNED (GET MIDDLE VS. NOISE), WITHIN THE PERIOD / TRANSIT (NOT NOISE)
        self.binned_folded_lc = self.folded_lc.bin((self.folded_lc_df.index.max() - self.folded_lc_df.index.min()) / 256)
        self.bflc_df = self.binned_folded_lc.to_pandas()

        self.transit_indices = abs(self.bflc_df.index) <= 0.5 * self.transit_duration
        self.transit_depth = 1 - self.bflc_df.loc[self.transit_indices, 'flux'].min()

        self.transit_depth_unc = self.flux_unc + self.bflc_df['flux'].std() / (numpy.sqrt(len(self.transit_indices)))

        print(f'transit_depth: {self.transit_depth}')
        print(f'transit_depth_unc: {self.transit_depth_unc}')

        return self.transit_depth

    def plot_transit_depth(self, save_in_auto = True):
        # plot.figure(figsize = (16, 9))
        plot.title(f'{self.star} {self.exoplanet_letter} Transit Depth')

        plot.scatter(self.folded_lc_df.index, self.folded_lc_df['flux'], s = 2.5, color = 'C0')
        plot.plot(self.bflc_df.index, self.bflc_df['flux'], color = 'C1')

        legend = ['baseline light curve', 'binned light curve']
        plot.plot(self.bflc_df.index, numpy.linspace(1 - self.transit_depth, 1 - self.transit_depth, len(self.bflc_df.index)), linewidth = 3, color = 'C2')

        legend.extend(['transit flux depth'])

        plot.xlabel('Phase (days)')
        plot.ylabel('Normalized Flux')
        plot.legend(legend)

        if not self.auto_mode:
            plot.show()

        else:
            if save_in_auto:
                self.savefig('transit_depths')

            plot.close()

        time.sleep(0.1)

    def is_exoplanet(self):
        exoplanet = Exoplanet(
            self.star,
            self.exoplanet_letter
        )

        exoplanet.add_periodogram_details(
            self.period,
            self.transit_time,
            self.transit_duration * 24,
        )

        exoplanet.add_transit_depth(self.transit_depth)

        kwargs = {
            'period_fwhm': self.period_fwhm,
            'period_unc': self.period_unc,
            'transit_depth_unc': self.transit_depth_unc,
            'flux_unc': self.flux_unc,
            'signal_to_noise_ratio': self.snr,
            'transit_duration_unc': self.transit_duration_unc,
            'transit_time_unc': self.transit_time_unc,
            'exoplanet_num': len(self.exoplanets) + 1,
        }

        exoplanet.add(**kwargs)

        self.exoplanets[self.exoplanet_letter] = exoplanet

        self.previous_exoplanet_letter = self.exoplanet_letter
        self.exoplanet_letter = chr(ord(self.exoplanet_letter) + 1)

    def mask_exoplanet(self, letter):
        self.mask_indices[letter] = self.p.get_transit_mask(
            period = self.period,
            transit_time = self.transit_time,
            duration = self.transit_duration
        )

        self.masks[letter] = self.lc[self.mask_indices[letter]]
        self.mask_dfs[letter] = self.masks[letter].to_pandas()

        self.lc = self.lc[~self.mask_indices[letter]]
        self.lc_df = self.lc.to_pandas()

        return self.masks[letter]

    def get_exoplanet(self, letter):
        return self.exoplanets[letter]

    def save(self, base_folder = None):
        folder = base_folder or self.star

        if not os.path.exists(f'{folder}'):
            os.mkdir(f'{folder}')

        if not os.path.exists(f'{folder}/save_data'):
            os.mkdir(f'{folder}/save_data')

        save_paths = []
        for letter in self.exoplanets.keys():
            savefile = f'{folder}/save_data/{self.star} {letter} @ {datetime.datetime.now().strftime('%Y-%B-%d %I:%M:%S %p')}.json'

            exoplanet = self.exoplanets[letter]
            exoplanet.to_json(savefile)
            save_paths.append(savefile)

        return save_paths

    def savefig(self, subfolder, title = None):
        if title is None:
            title = plot.gca().get_title()

        plot.tight_layout(pad = 0.25)
        plot.savefig(f'{self.auto_folder}/{subfolder}/{title} @ {datetime.datetime.now().strftime('%B %d, %Y %I:%M:%S %p')}.png', dpi = 150)