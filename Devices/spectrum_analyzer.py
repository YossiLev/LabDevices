import time
import numpy as np
import pyvisa


class YokogawaAQ6370B:
    """Python interface for Yokogawa AQ6370B Optical Spectrum Analyzer."""

    def __init__(self, resource_name: str, timeout_ms: int = 20000):
        """Initialize connection to the instrument.

        :param resource_name: VISA address (e.g., 'TCPIP0::192.168.1.100::inst0::INSTR' or 'GPIB0::28::INSTR')
        :param timeout_ms: Timeout in milliseconds (sweeps can take time, so default is 20s).
        """
        self.rm = pyvisa.ResourceManager()
        self.resource_name = resource_name
        self.instr = None
        self.timeout = timeout_ms

    def connect(self):
        """Open the VISA connection to the OSA."""
        self.instr = self.rm.open_resource(self.resource_name)
        self.instr.timeout = self.timeout
        self.instr.read_termination = '\n'
        self.instr.write_termination = '\n'
        print(f"Connected to: {self.get_idn()}")

    def get_idn(self) -> str:
        """Query instrument identification string."""
        return self.instr.query("*IDN?").strip()

    def single_sweep(self, wait_until_done: bool = True):
        """Trigger a single sweep.

        :param wait_until_done: If True, blocks until the sweep completes.
        """
        self.instr.write(":INITiate:IMMediate")
        if wait_until_done:
            # Poll status register until sweep is complete (*OPC?)
            self.instr.query("*OPC?")

    def get_trace_data(self, trace: str = "TRA") -> tuple[np.ndarray, np.ndarray]:
        """Fetch x-axis (wavelength in nm) and y-axis (power in dBm/W) data for a given trace.

        :param trace: Trace identifier ('TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG')
        :return: Tuple of numpy arrays (wavelengths_nm, powers)
        """
        trace = trace.upper()

        # Query X-axis (Wavelengths in meters, convert to nanometers)
        raw_x = self.instr.query(f":TRACe:X? {trace}")
        wavelengths_nm = np.fromstring(raw_x, sep=",") * 1e9

        # Query Y-axis (Power levels)
        raw_y = self.instr.query(f":TRACe:Y? {trace}")
        powers = np.fromstring(raw_y, sep=",")

        return wavelengths_nm, powers

    def get_wavelength_span(self) -> tuple[float, float]:
        """Get the start and stop wavelength settings in nanometers."""
        start = float(self.instr.query(":SENSe:WAVelength:STARt?")) * 1e9
        stop = float(self.instr.query(":SENSe:WAVelength:STOP?")) * 1e9
        return start, stop

    def set_wavelength_span(self, start_nm: float, stop_nm: float):
        """Set the start and stop wavelength settings in nanometers."""
        self.instr.write(f":SENSe:WAVelength:STARt {start_nm}NM")
        self.instr.write(f":SENSe:WAVelength:STOP {stop_nm}NM")

    def close(self):
        """Close connection to instrument."""
        if self.instr:
            self.instr.close()
            print("Connection closed.")


# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # Replace with your actual VISA address:
    # - Ethernet: 'TCPIP0::192.168.1.100::inst0::INSTR'
    # - GPIB:     'GPIB0::1::INSTR'
    VISA_ADDRESS = "TCPIP0::192.168.1.100::inst0::INSTR"

    osa = YokogawaAQ6370B(resource_name=VISA_ADDRESS)

    try:
        osa.connect()

        # 1. Trigger a single sweep
        print("Sweeping...")
        osa.single_sweep(wait_until_done=True)

        # 2. Retrieve spectrum trace data
        wl_nm, power = osa.get_trace_data(trace="TRA")

        print(f"Acquired {len(wl_nm)} points.")
        print(f"Wavelength range: {wl_nm[0]:.2f} nm to {wl_nm[-1]:.2f} nm")
        print(f"Peak Power: {np.max(power):.2f} dBm at {wl_nm[np.argmax(power)]:.2f} nm")

    finally:
        osa.close()