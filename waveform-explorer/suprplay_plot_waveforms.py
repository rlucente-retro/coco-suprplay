import math
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, List, Tuple

import numpy as np
import sounddevice as sd
from graphics import GraphWin, Point, Rectangle, Text, update

# Constants
PLOT_WIDTH = 256
PLOT_HEIGHT = 192
PLOT_SEPARATOR = 10
SAMPLE_RATE = 44100
MIDDLE_C_FREQ = 261.63
AUDIO_DURATION = 2.0
FPS = 30

@dataclass
class Waveform:
    """Represents a waveform with its generation function and metadata."""
    func: Callable[[float], float]
    label: str
    index: int

class AudioEngine:
    """Handles audio generation and playback."""
    
    @staticmethod
    def play(waveform_func: Callable[[float], float], 
             duration: float = AUDIO_DURATION, 
             freq: float = MIDDLE_C_FREQ):
        """Generates and plays a sound based on the waveform function."""
        # Vectorize the waveform function for performance
        v_wf = np.vectorize(waveform_func)
        
        # Create time array and map it to theta [0, 2*pi] for each cycle
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
        # Wrap phase to [0, 2*pi] to match the visual plot
        theta = (2 * np.pi * freq * t) % (2 * np.pi)
        
        # Generate samples
        samples = v_wf(theta)
        
        # Normalize: remove DC offset and scale to [-1, 1]
        samples = samples - np.mean(samples)
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples / max_val
        
        # Apply a quick fade-out to prevent audio pops/clicks
        fade_len = int(0.02 * SAMPLE_RATE)
        samples[-fade_len:] *= np.linspace(1, 0, fade_len)
        
        sd.play(samples, SAMPLE_RATE)

class WaveformExplorer:
    """Main application for visualizing and playing waveforms."""
    
    def __init__(self):
        self.waveforms = self._initialize_waveforms()
        self.num_columns = math.ceil(math.sqrt(len(self.waveforms)))
        self.num_rows = math.ceil(len(self.waveforms) / self.num_columns)
        
        self.window_width = self.num_columns * (PLOT_WIDTH + PLOT_SEPARATOR) + PLOT_SEPARATOR
        self.window_height = self.num_rows * (PLOT_HEIGHT + PLOT_SEPARATOR) + PLOT_SEPARATOR
        
        self.win = GraphWin('SUPRPLAY Waveform Explorer', self.window_width, self.window_height, autoflush=False)
        self.win.setBackground('black')
        
        self.plot_regions: List[Tuple[Tuple[int, int, int, int], Waveform]] = []

    def _initialize_waveforms(self) -> List[Waveform]:
        """Defines the waveforms from the original BASIC program."""
        
        # Maps to BASIC line numbers for reference
        definitions = [
            (lambda x: math.cos(x)*88 + math.cos(x*2)*44 + math.sin(x*3)*22 + math.cos(x*4)*11 + 95, "490"),
            (lambda x: math.sin(x)*64 + math.sin(x*2)*32 + math.sin(x*3)*16 + math.sin(x*4)*8 + math.sin(x*8)*8 + 128, "500"),
            (lambda x: 80 * math.atan(math.sin(5*x) + math.tan(0.2*x) + math.cos(3*x)) + 128, "510"),
            (lambda x: math.sin(x)*32 + math.cos(x*2)*32 + math.sin(x*3)*32 + math.cos(x*4)*32 + 128, "520"),
            (lambda x: 20 * math.tan(math.sin(x) + math.cos(x)) + 128, "530"),
            (lambda x: math.sin(x*x)*63 + math.cos(x*x)*63 + 128, "540"),
            (lambda x: math.cos(x/2)*127 + 128, "550"),
            (lambda x: math.cos(x/2)*32 + math.sin(x)*96 + 128, "560"),
            (lambda x: math.sin(x)*127 + 128, "570"),
            (lambda x: 114 * math.atan(math.cos(4*x) + math.sin(3*x)) + 127, "580"),
            (lambda x: 230 * math.tan(math.sin(x) * math.cos(x)) + 128, "590"),
            (lambda x: 210 * math.tan(math.sin(x*0.99) * math.cos(x*1.01)) + 133, "600"),
            (lambda x: 127 * math.log(x + 0.01) * math.sin(x) * math.cos(x) + 127, "610"),
            (lambda x: 100 * math.atan(math.cos(4*x) * math.sin(x)) + 118, "620"),
        ]
        
        return [Waveform(func=f, label=l, index=i) for i, (f, l) in enumerate(definitions)]

    def plot_waveform(self, wf: Waveform, x_offset: int, y_offset: int):
        """Plots a single waveform and its metadata."""
        # Calculate point values for one cycle (0 to 2*pi)
        vals = [wf.func(math.pi * theta / 128) for theta in range(256)]
        
        # Draw the curve
        for x_rel, y_val in enumerate(vals):
            p = Point(x_offset + x_rel, y_val / 2 + y_offset)
            p.setFill('green')
            p.draw(self.win)
            
        # Draw bounding box
        rect = Rectangle(Point(x_offset, y_offset), Point(x_offset + 255, y_offset + 191))
        rect.setOutline("white")
        rect.draw(self.win)
        
        # Draw label and stats
        min_y, max_y = int(min(vals)), int(max(vals))
        stats_text = f"BASIC Line: {wf.label}\nmin_y = {min_y}\nmax_y = {max_y}"
        label = Text(Point(x_offset + 128, y_offset + 96), stats_text)
        label.setFill('white')
        label.draw(self.win)
        
        # Register click region
        self.plot_regions.append(((x_offset, y_offset, x_offset + 255, y_offset + 191), wf))

    def render(self):
        """Renders the entire grid of waveforms."""
        for idx, wf in enumerate(self.waveforms):
            row = idx // self.num_columns
            col = idx % self.num_columns
            
            x_off = col * (PLOT_WIDTH + PLOT_SEPARATOR) + PLOT_SEPARATOR
            y_off = row * (PLOT_HEIGHT + PLOT_SEPARATOR) + PLOT_SEPARATOR
            
            self.plot_waveform(wf, x_off, y_off)

    def run(self):
        """Main application loop."""
        self.render()
        
        while not self.win.isClosed():
            try:
                click = self.win.checkMouse()
                if click:
                    self._handle_click(click.getX(), click.getY())
                update(FPS)
            except (tk.TclError, KeyboardInterrupt):
                # Handle window closure or interrupt gracefully
                break

    def _handle_click(self, cx: int, cy: int):
        """Checks if a click occurred within a waveform region and plays sound."""
        for (x1, y1, x2, y2), wf in self.plot_regions:
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                AudioEngine.play(wf.func)
                break

if __name__ == "__main__":
    app = WaveformExplorer()
    app.run()
