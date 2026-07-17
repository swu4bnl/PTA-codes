# this the collection of all hardware controls for the PTA, including

# Laser, USB camera x2, Newport motors x3, sync motion for Newport motors. 


# TODO consider if this is better than using EpicsSignal with different read /
# write PVs
class PairSP(Device):
    """
    Hold a pair of PVs as a set-point / readback pair

    set forwards to the set point.
    """

    sp = Cpt(EpicsSignal, "-SP", kind="normal")
    rb = Cpt(EpicsSignalRO, "-RB", kind="hinted")

    def set(self, value, **kwargs):
        return self.sp.set(value, **kwargs)


class PairSEL(Device):
    """
    Hold a pair of PVs as bool / readback pair

    set forwards to the Select
    """

    sel = Cpt(EpicsSignal, "-Sel", kind="normal")
    rb = Cpt(EpicsSignalRO, "-RB", kind="hinted", string=True, auto_monitor=True)

    def set(self, value, **kwargs):
        return self.sel.set(value, **kwargs)


class PairCMD(Device):
    """
    Hold a pair of PVs as CMD / readback pair

    set forwards to the CMD
    """

    cmd = Cpt(EpicsSignal, "-CMD", kind="omitted")
    rb = Cpt(EpicsSignalRO, "-RB", kind="hinted")

    def set(self, value, **kwargs):
        return self.cmd.set(value, **kwargs)


class Laser(Device):
    """
    Class to represent the PTA laser as controlled by the beckoff I/O
    """

    # Set pulse width for output
    # Milliseconds units
    width = Cpt(PairSP, "OutWidthSet:1")
    # Set delay between input trigger and output trigger
    # Milliseconds units
    delay = Cpt(PairSP, "OutDelaySet:1")
    # Set number of discrete pulses per trigger event
    pulses = Cpt(PairSP, "OutPulsesSet:1")

    # Read inputs
    # 1 = PV trigger, 2 = physical trigger
    input1 = Cpt(EpicsSignalRO, "Input:1-RB")
    input2 = Cpt(EpicsSignalRO, "Input:2-RB")

    # Enable/disable trigger inputs
    # 1 = PV trigger, 2 = physical trigger
    pv_bitmask = Cpt(PairSEL, "InMaskBit:1")
    physical_bitmank = Cpt(PairSEL, "InMaskBit:2")

    # PV Trigger
    pv_trigger = Cpt(PairCMD, "Trigger:PV")

    # Enable/disable output trigger mode
    trigger_mode = Cpt(PairSEL, "OutMaskBit:1")

    # Output override and output readback
    # Override only works when trigger disabled
    manual_button = Cpt(PairSEL, 'Output:1')
    # manual_button = Cpt(PairSEL, "Output:1-Sel")

    def manual_mode(self):
        yield from bps.mv(self.trigger, 0)

    def turn_on(self):
        # TODO check if we are in manual mode
        yield from bps.mv(self.manual_button, 1)

    def turn_off(self):
        # TODO check if we are in manual mode
        yield from bps.mv(self.manual_button, 0)


laser = Laser("XF:11BM-CT{BIOME-MTO:1}", name="laser")


'''
turn on laser:

RE(bps.mv(laser.manual_button, 1))

turn off laser:

RE(bps.mv(laser.manual_button, 0))


'''

# self.powerV_PV = "XF:11BM-CT{BIOME-MTO:1}LaserVoltsSet:1-SP"    #changed at 080323 by RL for the new laser control box
# self.controlTTL_PV = "XF:11BM-CT{BIOME-MTO:1}Output:1-Sel"

