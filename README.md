# SuperPlay: Waveform Synthesis for TRS-80 Color Computer

This project explores and documents "SuperPlay," a clever modification for the TRS-80 Color Computer (CoCo) Extended BASIC interpreter. Originally published in the June 1988 issue of *The Rainbow* magazine by Jeremy Spiller, this software patches the built-in `PLAY` command to support custom waveforms using Direct Digital Synthesis (DDS).

## How it Works

The standard `PLAY` command in the CoCo's Extended BASIC is limited to simple 6-bit DAC output, typically producing square or triangle-like tones. SuperPlay enhances this by:

1.  **RAM Patching:** It copies the Extended BASIC ROM into the upper 32K RAM bank (using the CoCo's SAM TY register). This allows the program to modify the "read-only" interpreter code.
2.  **Command Extension:** It patches the `PLAY` command parser to recognize a new `W` (Waveform) command. Users can switch between waveforms by adding `W1`, `W2`, or `W3` to their music strings.
3.  **DDS Engine:** It replaces the standard sound generation loop with a high-speed DDS engine. Instead of simple toggling, it steps through a 256-byte waveform table at a frequency determined by a high-resolution pitch table.
4.  **Custom Waveforms:** The software supports user-defined waveforms. The provided BASIC loader generates these using mathematical formulas (e.g., Sine, Tangent, and complex additive synthesis).

## Project Structure

### Core Files
*   **[SuperPlay-Rainbow-June-1988.pdf](SuperPlay-Rainbow-June-1988.pdf):** The original magazine article detailing the project.
*   **[suprplay.bas](suprplay.bas):** The original Extended BASIC program. It loads the machine language patch, generates the pitch/waveform tables, and demonstrates the new sound capabilities.
*   **[suprplay_complete.asm](suprplay_complete.asm):** A fully annotated 6809 assembly disassembly of the machine language patch. This file explains exactly how the ROM is hijacked and how the DDS loop is implemented.

### Tools
*   **[waveform-explorer/](waveform-explorer/):** A modern Python-based tool to visualize and audition the waveforms defined in the BASIC program.

#### Running the Waveform Explorer
To run the explorer on a modern system (Windows, macOS, or Linux):
1.  Ensure you have Python 3 installed.
2.  Install the required dependencies:
    ```bash
    pip install -r waveform-explorer/requirements.txt
    ```
3.  Run the application:
    ```bash
    python waveform-explorer/suprplay_plot_waveforms.py
    ```
4.  **Usage:** The app will plot all mathematical waveforms from the original article. Click anywhere within a waveform's bounding box to hear a 2-second audio sample of that waveform at Middle C.

## Usage on a TRS-80 Color Computer
To run this on an original CoCo or emulator:
1. Load and run `suprplay.bas`.
2. The program will POKE the machine code into memory above BASIC.
3. It will then `EXEC &H7B7D` to install the patches and switch the system to the RAM-based ROM bank.
4. Subsequent `PLAY` commands will support the `W` parameter (e.g., `PLAY "W2 T4 O3 CDE G"`).

## Technical Details
*   **Memory Bank Switching:** The CoCo's SAM registers at `$FFDE` (ROM mode) and `$FFDF` (RAM mode) are used to toggle between the original BASIC and the patched version.
*   **Phase Accumulation:** The DDS loop uses a 16-bit phase accumulator to provide accurate pitch across multiple octaves.
*   **Volume Scaling:** Volume (`V0`-`V31`) is handled by multiplying the 8-bit waveform samples by a 5-bit volume scalar before outputting to the 6-bit DAC at `$FF20`.
