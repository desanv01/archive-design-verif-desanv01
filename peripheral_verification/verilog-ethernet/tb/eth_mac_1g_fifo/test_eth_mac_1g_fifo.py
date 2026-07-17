#!/usr/bin/env python
"""

Copyright (c) 2020 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import itertools
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

import vsc
from cocotbext.axi import AxiStreamBus, AxiStreamSink, AxiStreamSource
from cocotbext.eth import GmiiFrame, GmiiSink, GmiiSource


DIRECTION_TX = 0
DIRECTION_RX = 1

LENGTH_TINY = 0
LENGTH_MINIMUM = 1
LENGTH_SHORT = 2
LENGTH_MEDIUM = 3
LENGTH_MAXIMUM = 4

PATTERN_ZERO = 0
PATTERN_ONES = 1
PATTERN_INCREMENTING = 2
PATTERN_ALTERNATING = 3
PATTERN_RANDOM = 4

SCENARIO_NORMAL = 0
SCENARIO_BACKPRESSURE = 1
SCENARIO_BAD_FCS = 2

ERROR_NONE = 0
ERROR_BAD_FCS = 1


@vsc.covergroup
class EthernetMacCoverage:
    def __init__(self):
        self.with_sample(
            dict(
                direction=vsc.bit_t(1),
                length_class=vsc.bit_t(3),
                pattern=vsc.bit_t(3),
                scenario=vsc.bit_t(2),
                error=vsc.bit_t(1),
            )
        )

        self.cp_direction = vsc.coverpoint(
            self.direction,
            bins={
                "tx": vsc.bin(DIRECTION_TX),
                "rx": vsc.bin(DIRECTION_RX),
            },
        )

        self.cp_length = vsc.coverpoint(
            self.length_class,
            bins={
                "tiny": vsc.bin(LENGTH_TINY),
                "minimum": vsc.bin(LENGTH_MINIMUM),
                "short": vsc.bin(LENGTH_SHORT),
                "medium": vsc.bin(LENGTH_MEDIUM),
                "maximum": vsc.bin(LENGTH_MAXIMUM),
            },
        )

        self.cp_pattern = vsc.coverpoint(
            self.pattern,
            bins={
                "zero": vsc.bin(PATTERN_ZERO),
                "ones": vsc.bin(PATTERN_ONES),
                "incrementing": vsc.bin(PATTERN_INCREMENTING),
                "alternating": vsc.bin(PATTERN_ALTERNATING),
                "random": vsc.bin(PATTERN_RANDOM),
            },
        )

        self.cp_scenario = vsc.coverpoint(
            self.scenario,
            bins={
                "normal": vsc.bin(SCENARIO_NORMAL),
                "backpressure": vsc.bin(SCENARIO_BACKPRESSURE),
                "bad_fcs": vsc.bin(SCENARIO_BAD_FCS),
            },
        )

        self.cp_error = vsc.coverpoint(
            self.error,
            bins={
                "none": vsc.bin(ERROR_NONE),
                "bad_fcs": vsc.bin(ERROR_BAD_FCS),
            },
        )

        self.cross_direction_length = vsc.cross(
            [self.cp_direction, self.cp_length]
        )


class EthernetMacTestbench:
    def __init__(self, dut):
        self.dut = dut

        dut.rx_clk_enable.value = 1
        dut.tx_clk_enable.value = 1
        dut.rx_mii_select.value = 0
        dut.tx_mii_select.value = 0

        dut.cfg_ifg.value = 12
        dut.cfg_tx_enable.value = 1
        dut.cfg_rx_enable.value = 1

        self.tx_source = AxiStreamSource(
            AxiStreamBus.from_prefix(dut, "tx_axis"),
            dut.logic_clk,
            dut.logic_rst,
        )

        self.rx_sink = AxiStreamSink(
            AxiStreamBus.from_prefix(dut, "rx_axis"),
            dut.logic_clk,
            dut.logic_rst,
        )

        self.gmii_source = GmiiSource(
            dut.gmii_rxd,
            dut.gmii_rx_er,
            dut.gmii_rx_dv,
            dut.rx_clk,
            dut.rx_rst,
            enable=dut.rx_clk_enable,
            mii_select=dut.rx_mii_select,
        )

        self.gmii_sink = GmiiSink(
            dut.gmii_txd,
            dut.gmii_tx_er,
            dut.gmii_tx_en,
            dut.tx_clk,
            dut.tx_rst,
            enable=dut.tx_clk_enable,
            mii_select=dut.tx_mii_select,
        )

    async def reset(self):
        self.dut.logic_rst.value = 0
        self.dut.tx_rst.value = 0
        self.dut.rx_rst.value = 0

        await Timer(40, unit="ns")

        self.dut.logic_rst.value = 1
        self.dut.tx_rst.value = 1
        self.dut.rx_rst.value = 1

        await Timer(80, unit="ns")

        self.dut.logic_rst.value = 0
        self.dut.tx_rst.value = 0
        self.dut.rx_rst.value = 0

        for _ in range(8):
            await RisingEdge(self.dut.logic_clk)


def make_payload(length, pattern, seed=20260717):
    if pattern == PATTERN_ZERO:
        return bytes(length)

    if pattern == PATTERN_ONES:
        return bytes([0xFF] * length)

    if pattern == PATTERN_INCREMENTING:
        return bytes(index & 0xFF for index in range(length))

    if pattern == PATTERN_ALTERNATING:
        return bytes(0x55 if index % 2 == 0 else 0xAA for index in range(length))

    generator = random.Random(seed + length)
    return bytes(generator.randrange(256) for _ in range(length))


def padded_payload(payload):
    return payload + bytes(max(0, 60 - len(payload)))


def pause_generator():
    return itertools.cycle([1, 1, 0, 0, 1, 0])


async def wait_for_pulse(signal, clock, maximum_cycles=10000):
    for _ in range(maximum_cycles):
        await RisingEdge(clock)
        if int(signal.value) == 1:
            return True
    return False


async def verify_tx(tb, payload):
    await tb.tx_source.send(payload)

    frame = await tb.gmii_sink.recv()

    assert frame.check_fcs(), "TX frame contains an invalid Ethernet FCS"

    actual = bytes(frame.get_payload())
    expected = padded_payload(payload)

    assert actual == expected, (
        f"TX payload mismatch: expected {len(expected)} bytes, "
        f"received {len(actual)} bytes"
    )


async def verify_rx(tb, payload):
    frame = GmiiFrame.from_payload(payload)

    await tb.gmii_source.send(frame)

    received = await tb.rx_sink.recv()
    actual = bytes(received.tdata)
    expected = padded_payload(payload)

    assert actual == expected, (
        f"RX payload mismatch: expected {len(expected)} bytes, "
        f"received {len(actual)} bytes"
    )


@cocotb.test()
async def test_eth_mac_1g_fifo_functional_coverage(dut):
    cocotb.start_soon(Clock(dut.logic_clk, 8, unit="ns").start())
    cocotb.start_soon(Clock(dut.tx_clk, 8, unit="ns").start())
    cocotb.start_soon(Clock(dut.rx_clk, 8, unit="ns").start())

    tb = EthernetMacTestbench(dut)
    coverage = EthernetMacCoverage()

    await tb.reset()

    directed_cases = [
        (1, LENGTH_TINY, PATTERN_ZERO),
        (60, LENGTH_MINIMUM, PATTERN_ONES),
        (128, LENGTH_SHORT, PATTERN_INCREMENTING),
        (512, LENGTH_MEDIUM, PATTERN_ALTERNATING),
        (1514, LENGTH_MAXIMUM, PATTERN_RANDOM),
    ]

    for direction in (DIRECTION_TX, DIRECTION_RX):
        for length, length_class, pattern in directed_cases:
            payload = make_payload(length, pattern)

            if direction == DIRECTION_TX:
                await verify_tx(tb, payload)
            else:
                await verify_rx(tb, payload)

            coverage.sample(
                direction,
                length_class,
                pattern,
                SCENARIO_NORMAL,
                ERROR_NONE,
            )

            dut._log.info(
                "PASS direction=%s length=%d pattern=%d",
                "TX" if direction == DIRECTION_TX else "RX",
                length,
                pattern,
            )

    tb.tx_source.set_pause_generator(pause_generator())
    tb.rx_sink.set_pause_generator(pause_generator())

    backpressure_payload = make_payload(256, PATTERN_RANDOM, seed=991)

    await verify_tx(tb, backpressure_payload)
    coverage.sample(
        DIRECTION_TX,
        LENGTH_SHORT,
        PATTERN_RANDOM,
        SCENARIO_BACKPRESSURE,
        ERROR_NONE,
    )

    await verify_rx(tb, backpressure_payload)
    coverage.sample(
        DIRECTION_RX,
        LENGTH_SHORT,
        PATTERN_RANDOM,
        SCENARIO_BACKPRESSURE,
        ERROR_NONE,
    )

    tb.tx_source.set_pause_generator(None)
    tb.rx_sink.set_pause_generator(None)

    bad_payload = make_payload(128, PATTERN_ALTERNATING)
    bad_frame = GmiiFrame.from_payload(bad_payload)
    bad_frame.data[-1] ^= 0x01

    bad_fcs_monitor = cocotb.start_soon(
        wait_for_pulse(dut.rx_error_bad_fcs, dut.logic_clk)
    )

    await tb.gmii_source.send(bad_frame)

    assert await bad_fcs_monitor, "RX bad-FCS status pulse was not observed"

    await Timer(2, unit="us")

    assert tb.rx_sink.empty(), "Bad-FCS frame was not dropped by the RX FIFO"

    coverage.sample(
        DIRECTION_RX,
        LENGTH_SHORT,
        PATTERN_ALTERNATING,
        SCENARIO_BAD_FCS,
        ERROR_BAD_FCS,
    )

    vsc.write_coverage_db("cov.xml", fmt="xml")

    assert Path("cov.xml").is_file(), "cov.xml was not generated"

    dut._log.info("PASS: functional coverage written to cov.xml")
