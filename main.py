# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from math import sqrt
from astropy.io import fits
from pulsar_xray_source_catalog import xray_source_catalog
import matplotlib.pyplot as plt
import numpy as np

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


class pulsar:
    # read pulsar properties from HEASARC tables and return a list of properties
    # built to provide input to the pulsar_accuracy calculator
    def __init__(self,name):
        self.name = name
        #read in table values for the other necessary parameters
        #table downloaded from Xamin manually https://heasarc.gsfc.nasa.gov/xamin/xamin.jsp

        # with fits.open('HEASARC pulsars.fits') as heasarc_pulsar_catalogue:
        #     matched = False
        #     for psr in heasarc_pulsar_catalogue[1].data:
        #         if psr[0].find(name) or psr[9].find(name):
        #             print(f"Found match for {name} as {psr[0]}")
        #             matched = True
        #         elif psr[9].find(name):
        #             print(f'Found match for {name} as {psr[9]}')
        #             matched = True
        #         if matched:
        target_name = self.name
        found_entry = None

        for entry in xray_source_catalog:
            if entry['name'] == target_name:
                found_entry = entry
                break

        if found_entry is not None:
            # print("Entry found:")
            # print(found_entry)
            self.period = entry['p']  # period in seconds
            self.duty_cycle = entry['w'] / self.period
            # self.flux
            self.photon_flux = entry['f_xray']
            self.pulsed_fraction = entry['pulsed_frac']
            self.background_flux = 3e-11 # erg cm^-2 s^-1
            self.background_flux_photon = self.background_flux / (10e3 * 1.6e-12)
            # self.background_flux_photon = 0.005  ### HARD CODED BACKGROUND FLUX IN photons cm^-2 s^-1
        else:
            print("Entry not found.")

        # B1937+21
        # p = 1.55e-3
        # d = 0.02 # duty cycle of the pulse
        # Fx = 4.1e-13 # Flux 2-10 keV (erg cm^-2 s^-1)
        # Fx_photon = Fx/(10e3 * 1.6e-12) # 10 keV photons have energy E = h*nu, where 1 ev = 1.6e-12 erg
        # pf = 0.86 # pulsed fraction of the flux
        # Bx_photon = 0.005 #photons cm^-2 s^-1


def pulsar_accuracy(style,name,area,tObs,sigma_range):
    psr = pulsar(name)
    p_width = psr.duty_cycle * psr.period

    if style == "range":
        snr = psr.photon_flux * psr.pulsed_fraction * area * tObs / sqrt((psr.background_flux_photon + psr.photon_flux * (1 - psr.pulsed_fraction)) * area * tObs * psr.duty_cycle + psr.photon_flux * psr.pulsed_fraction * area * tObs)
        sigma_range = 3e8 * p_width / (2 * snr)
        return sigma_range
    elif style == "area":
        # sigma_range = 10000 # 10 km accuracy goal
        area_reduced_snr = psr.photon_flux * psr.pulsed_fraction * tObs / sqrt((psr.background_flux_photon + psr.photon_flux * (1 - psr.pulsed_fraction)) * tObs * psr.duty_cycle + psr.photon_flux * psr.pulsed_fraction * tObs)
        area = (3e8 * p_width / (2 * sigma_range * area_reduced_snr))**2
        return area
    elif style == "time":
        # sigma_range = 10000  # 10 km accuracy goal
        time_reduced_snr = psr.photon_flux * psr.pulsed_fraction * area / sqrt((psr.background_flux_photon + psr.photon_flux * (1 - psr.pulsed_fraction)) * area * psr.duty_cycle + psr.photon_flux * psr.pulsed_fraction * area)
        time = (3e8 * p_width / (2 * sigma_range * time_reduced_snr))**2
        return time

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Jacob')
    study_parameter = 'range'
    pulsar_name = 'B1821-24'
    area=100
    tObs=86400/3 #
    sigma_range=10000 # 10 km
    print(f'The {study_parameter} possible for {pulsar_name} is {round(pulsar_accuracy(study_parameter,pulsar_name,area,tObs,sigma_range),2)}.')

    time = np.logspace(0,6.5,100)
    range_accuracy = list()
    for t in time:
        range_accuracy.append(pulsar_accuracy(study_parameter,pulsar_name,area,t,sigma_range))

    # Create log-log plot
    plt.loglog(time, range_accuracy)

    # Set labels and title
    plt.xlabel('Time')
    plt.ylabel('Pulsar Accuracy')
    plt.title('Pulsar Accuracy vs. Time')

    # Show the plot
    plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
