`timescale 1ns/1ps
module or_xor_gate (
    input  wire a,
    input  wire b,
    output wire y_or,
    output wire y_xor
);
    assign y_or  = a | b;
    assign y_xor = a ^ b;
endmodule
