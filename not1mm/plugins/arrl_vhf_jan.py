"""ARRL Jan VHF"""

# Status:	Active
# Geographic Focus:	United States/Canada
# Participation:	Worldwide
# Mode:	Any
# Bands:	50 MHz and up
# Classes:	Single Op All Band (All Modes/Analog Modes)(Low/High)
# Single Op Portable (All Modes/Analog Modes)
# Single Op 3-Band (All Modes/Analog Modes)
# Single Op FM
# Rover
# Limited Rover
# Unlimited Rover
# Multi-Op
# Limited Multi-Op
# Max power:	(see rules)
# Exchange:	4-character grid square
# Work stations:	Once per band
# QSO Points:	1 point per 50 or 144 MHz QSO
# 2 points per 222 or 432 MHz QSO
# 4 points per 902 or 1296 MHz QSO
# 8 points per 2.3 GHz or higher QSO
# Multipliers:	Grid squares once per band
# Rovers: grid squares operated from once regardless of band
# Score Calculation:	Total score = total QSO points x total mults
# E-mail logs to:	(none)
# Upload log at:	http://contest-log-submission.arrl.org
# Mail logs to:	January VHF
# ARRL
# 225 Main St.
# Newington, CT 06111
# USA
# Find rules at:	http://www.arrl.org/january-vhf
# Cabrillo name:	ARRL-VHF-JAN
# Cabrillo name aliases:	ARRL-VHF

# pylint: disable=invalid-name, unused-argument, unused-variable, c-extension-no-member

import datetime
import logging

from pathlib import Path
from PyQt6 import QtWidgets

from not1mm.lib.ham_utility import get_logged_band
from not1mm.lib.plugin_common import gen_adif, get_points
from not1mm.lib.version import __version__

logger = logging.getLogger(__name__)

ALTEREGO = None
EXCHANGE_HINT = "4-character grid square"

name = "ARRL VHF JAN"
mode = "BOTH"  # CW SSB BOTH RTTY
cabrillo_name = "ARRL-VHF-JAN"

columns = [
    "YYYY-MM-DD HH:MM:SS",
    "Call",
    "Freq",
    "Mode",
    "SentNr",
    "RcvNr",
    "PTS",
]

advance_on_space = [True, True, True, True, True]

# 1 once per contest, 2 work each band, 3 each band/mode, 4 no dupe checking
dupe_type = 2


def init_contest(self):
    """setup plugin"""
    set_tab_next(self)
    set_tab_prev(self)
    interface(self)
    self.next_field = self.other_2


def interface(self):
    """Setup user interface"""
    self.field1.show()
    self.field2.show()
    self.field3.show()
    self.field4.show()
    self.snt_label.setText("SNT")
    self.field1.setAccessibleName("RST Sent")
    label = self.field3.findChild(QtWidgets.QLabel)
    label.setText("SentNR")
    self.field3.setAccessibleName("Sent Grid")
    label = self.field4.findChild(QtWidgets.QLabel)
    label.setText("Grid")
    self.field4.setAccessibleName("Gridsquare")


def reset_label(self):
    """reset label after field cleared"""


def set_tab_next(self):
    """Set TAB Advances"""
    self.tab_next = {
        self.callsign: self.field1.findChild(QtWidgets.QLineEdit),
        self.field1.findChild(QtWidgets.QLineEdit): self.field2.findChild(
            QtWidgets.QLineEdit
        ),
        self.field2.findChild(QtWidgets.QLineEdit): self.field3.findChild(
            QtWidgets.QLineEdit
        ),
        self.field3.findChild(QtWidgets.QLineEdit): self.field4.findChild(
            QtWidgets.QLineEdit
        ),
        self.field4.findChild(QtWidgets.QLineEdit): self.callsign,
    }


def set_tab_prev(self):
    """Set TAB Advances"""
    self.tab_prev = {
        self.callsign: self.field4.findChild(QtWidgets.QLineEdit),
        self.field1.findChild(QtWidgets.QLineEdit): self.callsign,
        self.field2.findChild(QtWidgets.QLineEdit): self.field1.findChild(
            QtWidgets.QLineEdit
        ),
        self.field3.findChild(QtWidgets.QLineEdit): self.field2.findChild(
            QtWidgets.QLineEdit
        ),
        self.field4.findChild(QtWidgets.QLineEdit): self.field3.findChild(
            QtWidgets.QLineEdit
        ),
    }


def validate(self):
    """doc"""
    # exchange = self.other_2.text().upper().split()
    # if len(exchange) == 3:
    #     if exchange[0].isalpha() and exchange[1].isdigit() and exchange[2].isalpha():
    #         return True
    # return False
    return True


def set_contact_vars(self):
    """Contest Specific"""
    self.contact["SNT"] = self.sent.text()
    self.contact["RCV"] = self.receive.text()
    self.contact["NR"] = self.other_2.text().upper()
    self.contact["SentNr"] = self.other_1.text()


def predupe(self):
    """called after callsign entered"""


def prefill(self):
    """Fill sentnr"""
    result = self.database.get_serial()
    serial_nr = str(result.get("serial_nr", "1")).zfill(3)
    if serial_nr == "None":
        serial_nr = "001"

    exchange = self.contest_settings.get("SentExchange", "").replace("#", serial_nr)
    field = self.field3.findChild(QtWidgets.QLineEdit)
    if len(field.text()) == 0:
        field.setText(exchange)


def points(self):
    """Calc point"""

    # QSO Points:	1 point per 50 or 144 MHz QSO
    # 2 points per 222 or 432 MHz QSO
    # 4 points per 902 or 1296 MHz QSO
    # 8 points per 2.3 GHz or higher QSO

    _band = self.contact.get("Band", "")
    if _band in ["50", "144"]:
        return 1
    if _band in ["222", "432"]:
        return 2
    if _band in ["902", "1296"]:
        return 4
    if _band in ["2300+"]:
        return 8
    return 0


def show_mults(self):
    """Return display string for mults"""
    # Multipliers:	Grid squares once per band

    dx = 0

    sql = (
        "select count(DISTINCT(NR || ':' || Band)) as mult_count "
        f"from dxlog where ContestNR = {self.database.current_contest} and typeof(NR) = 'text';"
    )
    result = self.database.exec_sql(sql)

    if result:
        dx = result.get("mult_count", 0)

    return dx


def show_qso(self):
    """Return qso count"""
    result = self.database.fetch_qso_count()
    if result:
        return int(result.get("qsos", 0))
    return 0


def calc_score(self):
    """Return calculated score"""
    # Multipliers: Each US State + DC once per mode
    _points = get_points(self)
    _mults = show_mults(self)
    _power_mult = 1
    # if self.contest_settings.get("PowerCategory", "") == "QRP":
    #     _power_mult = 2
    return _points * _power_mult * _mults


def adif(self):
    """Call the generate ADIF function"""
    gen_adif(self, cabrillo_name)


def output_cabrillo_line(line_to_output, ending, file_descriptor, file_encoding):
    """"""
    print(
        line_to_output.encode(file_encoding, errors="ignore").decode(),
        end=ending,
        file=file_descriptor,
    )


def cabrillo(self, file_encoding):
    """Generates Cabrillo file. Maybe."""
    # https://www.cqwpx.com/cabrillo.htm
    logger.debug("******Cabrillo*****")
    logger.debug("Station: %s", f"{self.station}")
    logger.debug("Contest: %s", f"{self.contest_settings}")
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = (
        str(Path.home())
        + "/"
        + f"{self.station.get('Call', '').upper()}_{cabrillo_name}_{date_time}.log"
    )
    logger.debug("%s", filename)
    log = self.database.fetch_all_contacts_asc()
    try:
        with open(filename, "w", encoding=file_encoding) as file_descriptor:
            output_cabrillo_line(
                "START-OF-LOG: 3.0",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CREATED-BY: Not1MM v{__version__}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CONTEST: {cabrillo_name}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            if self.station.get("Club", ""):
                output_cabrillo_line(
                    f"CLUB: {self.station.get('Club', '').upper()}",
                    "\r\n",
                    file_descriptor,
                    file_encoding,
                )
            output_cabrillo_line(
                f"CALLSIGN: {self.station.get('Call','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"LOCATION: {self.station.get('ARRLSection', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CATEGORY-OPERATOR: {self.contest_settings.get('OperatorCategory','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CATEGORY-ASSISTED: {self.contest_settings.get('AssistedCategory','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CATEGORY-BAND: {self.contest_settings.get('BandCategory','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CATEGORY-MODE: {self.contest_settings.get('ModeCategory','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CATEGORY-TRANSMITTER: {self.contest_settings.get('TransmitterCategory','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            if self.contest_settings.get("OverlayCategory", "") != "N/A":
                output_cabrillo_line(
                    f"CATEGORY-OVERLAY: {self.contest_settings.get('OverlayCategory','')}",
                    "\r\n",
                    file_descriptor,
                    file_encoding,
                )
            output_cabrillo_line(
                f"GRID-LOCATOR: {self.station.get('GridSquare','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"CATEGORY-POWER: {self.contest_settings.get('PowerCategory','')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )

            output_cabrillo_line(
                f"CLAIMED-SCORE: {calc_score(self)}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            ops = f"@{self.station.get('Call','')}"
            list_of_ops = self.database.get_ops()
            for op in list_of_ops:
                ops += f", {op.get('Operator', '')}"
            output_cabrillo_line(
                f"OPERATORS: {ops}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"NAME: {self.station.get('Name', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"ADDRESS: {self.station.get('Street1', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"ADDRESS-CITY: {self.station.get('City', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"ADDRESS-STATE-PROVINCE: {self.station.get('State', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"ADDRESS-POSTALCODE: {self.station.get('Zip', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"ADDRESS-COUNTRY: {self.station.get('Country', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            output_cabrillo_line(
                f"EMAIL: {self.station.get('Email', '')}",
                "\r\n",
                file_descriptor,
                file_encoding,
            )
            for contact in log:
                the_date_and_time = contact.get("TS", "")
                themode = contact.get("Mode", "")

                if themode in ("LSB", "USB", "AM"):
                    themode = "PH"
                if themode in (
                    "FT8",
                    "FT4",
                    "RTTY",
                    "PSK31",
                    "FSK441",
                    "MSK144",
                    "JT65",
                    "JT9",
                    "Q65",
                ):
                    themode = "DG"
                freq = int(contact.get("Freq", "0")) / 1000

                frequency = str(int(freq)).rjust(4)

                loggeddate = the_date_and_time[:10]
                loggedtime = the_date_and_time[11:13] + the_date_and_time[14:16]
                output_cabrillo_line(
                    f"QSO: {frequency} {themode} {loggeddate} {loggedtime} "
                    f"{contact.get('StationPrefix', '').ljust(13)} "
                    # f"{str(contact.get('SNT', '')).ljust(3)} "
                    f"{str(contact.get('SentNr', '')).ljust(6)} "
                    f"{contact.get('Call', '').ljust(13)} "
                    # f"{str(contact.get('RCV', '')).ljust(3)} "
                    f"{str(contact.get('NR', '')).ljust(6)}",
                    "\r\n",
                    file_descriptor,
                    file_encoding,
                )
            output_cabrillo_line("END-OF-LOG:", "\r\n", file_descriptor, file_encoding)
        self.show_message_box(f"Cabrillo saved to: {filename}")
    except IOError as exception:
        logger.critical("cabrillo: IO error: %s, writing to %s", exception, filename)
        self.show_message_box(f"Error saving Cabrillo: {exception} {filename}")
        return


def recalculate_mults(self):
    """Recalculates multipliers after change in logged qso."""


def set_self(the_outie):
    """..."""
    globals()["ALTEREGO"] = the_outie


def ft8_handler(the_packet: dict):
    """Process FT8 QSO packets
    FT8
    {
        'CALL': 'KE0OG',
        'GRIDSQUARE': 'DM10AT',
        'MODE': 'FT8',
        'RST_SENT': '',
        'RST_RCVD': '',
        'QSO_DATE': '20210329',
        'TIME_ON': '183213',
        'QSO_DATE_OFF': '20210329',
        'TIME_OFF': '183213',
        'BAND': '20M',
        'FREQ': '14.074754',
        'STATION_CALLSIGN': 'K6GTE',
        'MY_GRIDSQUARE': 'DM13AT',
        'CONTEST_ID': 'ARRL-FIELD-DAY',
        'SRX_STRING': '1D UT',
        'CLASS': '1D',
        'ARRL_SECT': 'UT'
    }
    FlDigi
    {
        'FREQ': '7.029500',
        'CALL': 'DL2DSL',
        'MODE': 'RTTY',
        'NAME': 'BOB',
        'QSO_DATE': '20240904',
        'QSO_DATE_OFF': '20240904',
        'TIME_OFF': '212825',
        'TIME_ON': '212800',
        'RST_RCVD': '599',
        'RST_SENT': '599',
        'BAND': '40M',
        'COUNTRY': 'FED. REP. OF GERMANY',
        'CQZ': '14',
        'STX': '000',
        'STX_STRING': '1D ORG',
        'CLASS': '1D',
        'ARRL_SECT': 'DX',
        'TX_PWR': '0',
        'OPERATOR': 'K6GTE',
        'STATION_CALLSIGN': 'K6GTE',
        'MY_GRIDSQUARE': 'DM13AT',
        'MY_CITY': 'ANAHEIM, CA',
        'MY_STATE': 'CA'
    }

    """
    # print(f"\n{the_packet=}\n")
    if ALTEREGO is not None:
        ALTEREGO.callsign.setText(the_packet.get("CALL"))
        ALTEREGO.contact["Call"] = the_packet.get("CALL", "")
        ALTEREGO.contact["SNT"] = ALTEREGO.sent.text()
        ALTEREGO.contact["RCV"] = ALTEREGO.receive.text()
        my_grid = the_packet.get("MY_GRIDSQUARE", "")
        if my_grid:
            if len(my_grid) > 4:
                my_grid = my_grid[:4]
        their_grid = the_packet.get("GRIDSQUARE", "")
        if their_grid:
            if len(their_grid) > 4:
                their_grid = their_grid[:4]
        ALTEREGO.contact["NR"] = their_grid
        if the_packet.get("SUBMODE"):
            ALTEREGO.contact["Mode"] = the_packet.get("SUBMODE", "ERR")
        else:
            ALTEREGO.contact["Mode"] = the_packet.get("MODE", "ERR")
        ALTEREGO.contact["Freq"] = round(float(the_packet.get("FREQ", "0.0")) * 1000, 2)
        ALTEREGO.contact["QSXFreq"] = round(
            float(the_packet.get("FREQ", "0.0")) * 1000, 2
        )
        ALTEREGO.contact["Band"] = get_logged_band(
            str(int(float(the_packet.get("FREQ", "0.0")) * 1000000))
        )
        # print(f"\n{ALTEREGO.contact=}\n")
        ALTEREGO.other_1.setText(my_grid)
        ALTEREGO.other_2.setText(their_grid)
        ALTEREGO.save_contact()


def check_call_history(self):
    """"""
    result = self.database.fetch_call_history(self.callsign.text())
    print(f"{result=}")
    if result:
        self.history_info.setText(f"{result.get('UserText','')}")
        if self.other_2.text() == "":
            self.other_2.setText(f"{result.get('Loc1', '')}")
