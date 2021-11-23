# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting


DATA_COMMANDS = {0x00: "Write",
                 0x01: "Read"}

CONTROL_COMMANDS = {}




# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # List of settings that a user can set for this High Level Analyzer.
    my_choices_setting = ChoicesSetting(choices=('Reading', 'Writing','all'))

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'mytype': {
            'format': 'Output type: {{type}}, Input type: {{data.input_type}}'
        }
    }

    def __init__(self):


        self._start_time = None
        self._address_bytes = 3
        self._address_format = "{:0" + str(2*int(self._address_bytes)) + "x}"

        self._miso_data = None
        self._mosi_data = None
        self._empty_result_count = 0

        # These are for quad decoding. The input will be a SimpleParallel analyzer
        # with the correct clock edge. CS is inferred from a gap in time.
        self._last_cs = 1
        self._last_time = None
        self._transaction = 0
        self._clock_count = 0
        self._mosi_out = 0
        self._miso_in = 0
        self._continuous = False
        self._dummy = 0

        self._fastest_cs = 2000000

        self.data=[]
        self.identificato=-1



    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''


        if frame.type =="enable":
            print("\n----------SPI _transaction--------\n")

        if frame.type =="result":

            if self.identificato == 1:
                if len(self.data) == 1:
                    self.data.append(frame.data["mosi"])
                else:
                    self.data.append(frame.data["miso"])


            if self.identificato == 0:
                self.data.append(frame.data["mosi"])

            if self.identificato == -1 and frame.data["mosi"]==b"\x01":
                self.identificato=1
                self.data.append(frame.data["mosi"])
            if self.identificato == -1 and frame.data["mosi"]==b"\x00":
                self.identificato=0
                self.data.append(frame.data["mosi"])

        if frame.type=="disable":
            if self.identificato == 1 and self.my_choices_setting!="Writing":
                print("Reading:  ",self.data[0])
                print("Address: ",self.data[1])
                print("Data: ",self.data[2:])

            if self.identificato == 0 and self.my_choices_setting!="Reading":
                print("Writing:  ",self.data[0])
                print("Address: ",self.data[1])
                print("Data: ",self.data[2:])

            self.data=[]
            self.identificato=-1
            print("\n----------SPI _transaction end--------\n")


        # Return the data frame itself
        return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
            'input_type': frame.type
        })
