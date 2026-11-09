# Overview
The student will design and build a web-based learning tool with three linked panes. The first is a C source editor. The second shows the RISC-V assembly produced by compiling that source. The third shows the binary and hexadecimal machine encoding of each instruction. When the user clicks or hovers over a line of C, the tool highlights the assembly instructions and encoded words generated from that line.
The purpose is to make the path from high-level code to machine code visible and interactive. Students often find this translation a difficult part of the course. The work will take place from late September through early December 2026. Compilation will use a RISC-V cross-compiler (GCC or Clang), either in the browser or on a small backend server. 


# How Is This Honors Work?
Regular coursework asks students to hand-translate small C fragments into RISC-V and to encode individual instructions on paper. This project covers this same topic at a much broader and deeper level, as the student must learn material outside the syllabus: compiler toolchains, object file structure, debug metadata, and how optimization levels (-O0 vs. -O2) change the generated code. Additionally, integrating these pieces into a correct, usable application requires software design, testing, and attention to pedagogy.


# Deliverables
* A working, publicly accessible (or easily installed) three-pane tool with line-level highlighting.
* A color-coded field breakdown of each encoding (opcode, rd, funct3, rs1, rs2, funct7, immediate).
* A source code repository with documentation and a test suite comparing the custom encoder to reference output.
* A 3-4 page technical report covering design decisions, limitations, and lessons learned.
* A set of three to five example C programs with suggested exploration exercises for future students.


The tool and example exercises will be made available to future sections of the course. The student may also present at undergraduate research, or honors showcase at their discretion. 


Timetable
Biweekly meetings with the instructor throughout the semester.
* October 16th: Design document, architecture, toolchain choice completed.
* November 6: Web tool scaffolding, demo compiler pipeline, and encoder tests completed.
* November 20: Line-mapping and highlighting features completed.
* December 4: Final tool, repository, report, and sample exercises submitted.


Evaluation criteria: 
* Compiles valid C to RISC-V (40%)
* Displays correct assembly and encodings correctly for RV32I (20%)
* Report is thorough and technically detailed (20%)
* Line-level highlighting works across all three panes (10%)
* Sample problems cover a range of compiler behaviors (e.g., loops, function calls, arrays, optimization levels) (10%)
