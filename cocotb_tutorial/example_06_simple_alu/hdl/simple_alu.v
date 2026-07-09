`timescale 1ns/1ps
module simple_alu (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire [1:0] op, // 00=ADD, 01=SUB, 10=AND, 11=OR
    output reg  [3:0] result,
    output reg        carry_out
);
    always @(*) begin
        carry_out = 1'b0;
        case (op)
            2'b00: {carry_out, result} = a + b;
            2'b01: {carry_out, result} = a - b;
            2'b10: result = a & b;
            2'b11: result = a | b;
            default: result = 4'b0000;
        endcase
    end
endmodule
