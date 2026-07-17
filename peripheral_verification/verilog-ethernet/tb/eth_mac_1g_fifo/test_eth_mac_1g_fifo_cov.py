import itertools
import random

import cocotb
import vsc
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotbext.axi import AxiStreamBus, AxiStreamSink, AxiStreamSource
from cocotbext.eth import GmiiFrame, GmiiSink, GmiiSource


TX_DIRECTION = 0
RX_DIRECTION = 1


def make_payload(pattern, length):
    """Create deterministic Ethernet payload data."""

    if pattern == 0:
        return bytes([0x00] * length)

    if pattern == 1:
        return bytes([0xFF] * length)

    if pattern == 2:
        return bytes(index & 0xFF for index in range(length))

    if pattern == 3:
        return bytes(
            0xAA if index % 2 == 0 else 0x55
            for index in range(length)
        )

    rng = random.Random(0x5EED + length)
    return bytes(rng.randrange(256) for _ in range(length))


@vsc.covergroup
class EthernetMacCoverage:
    """Functional coverage for Ethernet MAC TX and RX paths."""

    def __init__(self):
        self.with_sample(
            dict(
                direction=vsc.bit_t(1),
                length_class=vsc.bit_t(3),
                pattern=vsc.bit_t(3),
                stalled=vsc.bit_t(1),
            )
        )

        self.cp_direction = vsc.coverpoint(
            self.direction,
            bins={
                "tx": vsc.bin(TX_DIRECTION),
                "rx": vsc.bin(RX_DIRECTION),
            },
        )

        self.cp_length = vsc.coverpoint(
            self.length_class,
            bins={
                "minimum_60": vsc.bin(0),
                "short_64": vsc.bin(1),
                "medium_128": vsc.bin(2),
                "large_512": vsc.bin(3),
                "maximum_1514": vsc.bin(4),
            },
        )

        self.cp_pattern = vsc.coverpoint(
            self.pattern,
            bins={
                "all_zero": vsc.bin(0),
                "all_one": vsc.bin(1),
                "incrementing": vsc.bin(2),
                "alternating": vsc.bin(3),
                "random": vsc.bin(4),
            },
        )

        self.cp_stalled = vsc.coverpoint(
            self.stalled,
            bins={
                "continuous": vsc.bin(0),
                "backpressure": vsc.bin(1),
            },
        )

        self.cp_direction_x_length = vsc.cross(
            [self.cp_direction, self.cp_length]
        )


class TB:
    """Cocotb Ethernet MAC test environment."""

    def __init__(self, dut):
        self.dut = dut

        cocotb.start_soon(
            Clock(dut.logic_clk, 8, unit="ns").start()
        )
        cocotb.start_soon(
            Clock(dut.rx_clk, 8, unit="ns").start()
        )
        cocotb.start_soon(
            Clock(dut.tx_clk, 8, unit="ns").start()
        )

        self.gmii_source = GmiiSource(
            dut.gmii_rxd,
            dut.gmii_rx_er,
            dut.gmii_rx_dv,
            dut.rx_clk,
            dut.rx_rst,
            dut.rx_clk_enable,
            dut.rx_mii_select,
        )

        self.gmii_sink = GmiiSink(
            dut.gmii_txd,
            dut.gmii_tx_er,
            dut.gmii_tx_en,
            dut.tx_clk,
            dut.tx_rst,
            dut.tx_clk_enable,
            dut.tx_mii_select,
        )

        self.axis_source = AxiStreamSource(
            AxiStreamBus.from_prefix(dut, "tx_axis"),
            dut.logic_clk,
            dut.logic_rst,
        )

        self.axis_sink = AxiStreamSink(
            AxiStreamBus.from_prefix(dut, "rx_axis"),
            dut.logic_clk,
            dut.logic_rst,
        )

        dut.rx_clk_enable.value = 1
        dut.tx_clk_enable.value = 1

        dut.rx_mii_select.value = 0
        dut.tx_mii_select.value = 0

        dut.cfg_ifg.value = 12
        dut.cfg_tx_enable.value = 1
        dut.cfg_rx_enable.value = 1

    async def reset(self):
        """Apply reset to all MAC clock domains."""

        self.dut.logic_rst.value = 0
        self.dut.rx_rst.value = 0
        self.dut.tx_rst.value = 0

        for _ in range(4):
            await RisingEdge(self.dut.logic_clk)

        self.dut.logic_rst.value = 1
        self.dut.rx_rst.value = 1
        self.dut.tx_rst.value = 1

        for _ in range(4):
            await RisingEdge(self.dut.logic_clk)

        self.dut.logic_rst.value = 0
        self.dut.rx_rst.value = 0
        self.dut.tx_rst.value = 0

        for _ in range(8):
            await RisingEdge(self.dut.logic_clk)


@cocotb.test()
async def ethernet_mac_functional_coverage_test(dut):
    """Verify Ethernet MAC TX/RX paths and generate cov.xml."""

    tb = TB(dut)
    coverage = EthernetMacCoverage()

    await tb.reset()

    test_cases = [
        (60, 0),
        (64, 1),
        (128, 2),
        (512, 3),
        (1514, 4),
    ]

    # ---------------------------------------------------------
    # TX path: AXI-stream input to GMII output
    # ---------------------------------------------------------

    for length_class, test_case in enumerate(test_cases):
        length, pattern = test_case
        payload = make_payload(pattern, length)

        # Apply AXI-stream backpressure to the 512-byte test.
        stalled = int(length_class == 3)

        if stalled:
            tb.axis_source.set_pause_generator(
                itertools.cycle([0, 0, 1, 0])
            )

        await tb.axis_source.send(payload)
        frame = await tb.gmii_sink.recv()

        tb.axis_source.set_pause_generator(None)

        received_payload = bytes(frame.get_payload())

        assert received_payload == payload, (
            f"TX payload mismatch for length {length}: "
            f"expected={payload.hex()} "
            f"received={received_payload.hex()}"
        )

        assert frame.check_fcs(), (
            f"TX FCS check failed for length {length}"
        )

        assert frame.error is None, (
            f"TX frame error for length {length}: {frame.error}"
        )

        coverage.sample(
            TX_DIRECTION,
            length_class,
            pattern,
            stalled,
        )

        dut._log.info(
            "TX PASS: length=%d pattern=%d stalled=%d",
            length,
            pattern,
            stalled,
        )

    # ---------------------------------------------------------
    # RX path: GMII input to AXI-stream output
    # ---------------------------------------------------------

    for length_class, test_case in enumerate(test_cases):
        length, pattern = test_case
        payload = make_payload(pattern, length)

        # Apply AXI-stream backpressure to the 512-byte test.
        stalled = int(length_class == 3)

        if stalled:
            tb.axis_sink.set_pause_generator(
                itertools.cycle([0, 0, 1, 0])
            )

        gmii_frame = GmiiFrame.from_payload(payload)

        await tb.gmii_source.send(gmii_frame)
        frame = await tb.axis_sink.recv()

        tb.axis_sink.set_pause_generator(None)

        received_payload = bytes(frame.tdata)

        assert received_payload == payload, (
            f"RX payload mismatch for length {length}: "
            f"expected={payload.hex()} "
            f"received={received_payload.hex()}"
        )

        assert int(frame.tuser) == 0, (
            f"RX frame reported an error for length {length}"
        )

        coverage.sample(
            RX_DIRECTION,
            length_class,
            pattern,
            stalled,
        )

        dut._log.info(
            "RX PASS: length=%d pattern=%d stalled=%d",
            length,
            pattern,
            stalled,
        )

    # Make sure all queued frames were processed.
    assert tb.axis_source.empty()
    assert tb.axis_sink.empty()
    assert tb.gmii_source.empty()
    assert tb.gmii_sink.empty()

    # Generate the functional coverage XML database.
    vsc.write_coverage_db("cov.xml", fmt="xml")

    dut._log.info("Functional coverage written to cov.xml")
    dut._log.info("ETHERNET MAC FUNCTIONAL COVERAGE TEST PASSED")
