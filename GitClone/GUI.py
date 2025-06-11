import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import platform
from PIL import Image, ImageTk  # Required for image handling
import uploader

class PrinterControlGUI:
    def __init__(self, root):
        self.filePath = ''
        self.root = root
        self.root.title("CeraTech")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f0f0')  # Main window background
        
        # Platform detection
        self.is_mac = platform.system() == 'Darwin'
        self.is_windows = platform.system() == 'Windows'
        
        # Custom window decorations (cross-platform compatible)
        if not self.is_mac:  # Only remove decorations on Windows/Linux
            self.root.overrideredirect(True)
            self.setup_window_dragging()
        else:
            # On macOS, keep native window controls for better UX
            self.root.resizable(True, True)
        
        # ===== TOP BAR (LOGO + DRAG AREA + CLOSE BUTTON) =====
        self.top_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.top_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Logo handling with cross-platform path
        self.setup_logo()
        
        # Close button (only show on non-Mac systems when overrideredirect is used)
        if not self.is_mac:
            self.setup_close_button()
        
        # Variables
        self.current_file = tk.StringVar(value="No file selected")
        self.printer_status = tk.StringVar(value="Ready")
        self.print_progress = tk.DoubleVar(value=0)
        
        self.setup_ui()
        
    def setup_logo(self):
        """Setup logo with cross-platform file handling"""
        logo_paths = [
            "CeraTech.png",
            os.path.join("assets", "CeraTech.png"),
            os.path.join("images", "CeraTech.png"),
            os.path.join(os.path.dirname(__file__), "CeraTech.png")
        ]
        
        logo_loaded = False
        for logo_path in logo_paths:
            try:
                if os.path.exists(logo_path):
                    self.logo_img = Image.open(logo_path).convert("RGBA")
                    self.logo_img = self.logo_img.resize((300, 150), Image.LANCZOS)
                    self.logo_tk = ImageTk.PhotoImage(self.logo_img)
                    self.logo_label = tk.Label(
                        self.top_frame, 
                        image=self.logo_tk, 
                        bg='#f0f0f0'
                    )
                    self.logo_label.image = self.logo_tk  # Keep reference
                    self.logo_label.pack(side=tk.LEFT, padx=10)
                    logo_loaded = True
                    break
            except Exception as e:
                print(f"Failed to load logo from {logo_path}: {e}")
                continue
        
        if not logo_loaded:
            # Fallback text logo
            tk.Label(
                self.top_frame, 
                text="CeraTech", 
                font=self.get_font('Arial', 16, 'bold'),
                bg='#f0f0f0',
                fg='#333333'
            ).pack(side=tk.LEFT, padx=10)
    
    def setup_close_button(self):
        """Setup close button for custom window decorations"""
        close_symbol = "✕" if not self.is_windows else "×"  # Different symbols for different OS
        
        self.close_btn = tk.Button(
            self.top_frame,
            text=close_symbol,
            font=self.get_font('Arial', 12),
            bg='#f0f0f0',
            fg='#333333',
            bd=0,
            relief=tk.FLAT,
            activebackground='#ff4444',
            activeforeground='white',
            command=self.close_application,
            width=3,
            height=1
        )
        self.close_btn.pack(side=tk.RIGHT, padx=10)
    
    def setup_window_dragging(self):
        """Enable window dragging for custom titlebar"""
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag_window)
        self.top_frame.bind('<Button-1>', self.start_drag)
        self.top_frame.bind('<B1-Motion>', self.drag_window)
        
    def select_all_text(self, event):
        """Select all text in an entry when it receives focus"""
        entry = event.widget
        entry.select_range(0, tk.END)  # Select all text
        entry.icursor(tk.END)  # Move cursor to the end (better UX)
    
    def start_drag(self, event):
        """Start window drag operation"""
        self.x = event.x
        self.y = event.y
    
    def drag_window(self, event):
        """Handle window dragging"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def get_font(self, family, size, weight=None):
        """Get appropriate font for the platform"""
        if self.is_mac:
            # macOS prefers system fonts
            font_family = 'SF Pro Display' if family == 'Arial' else family
        else:
            font_family = family
        
        if weight:
            return (font_family, size, weight)
        else:
            return (font_family, size)
    
    def close_application(self):
        """Properly close the application"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        finally:
            sys.exit(0)
        
    def setup_ui(self):
        # Main title
        title_label = tk.Label(
            self.root, 
            text="3D Printer Control Panel", 
            font=self.get_font('Arial', 16, 'bold'), 
            bg='#f0f0f0', 
            fg='#333'
        )
        title_label.pack(pady=10)
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="File Management", padding="10")
        file_frame.pack(fill='x', padx=20, pady=10)
        
        # Current file display
        tk.Label(
            file_frame, 
            text="Selected File:", 
            font=self.get_font('Arial', 10, 'bold')
        ).pack(anchor='w')
        
        file_display = tk.Label(
            file_frame, 
            textvariable=self.current_file, 
            font=self.get_font('Arial', 9), 
            fg='#666', 
            wraplength=500
        )
        file_display.pack(anchor='w', pady=(0, 10))
        
        # Upload button with platform-appropriate emoji and macOS color fix
        upload_text = "📁 Upload G-Code File" if not self.is_windows else "Upload G-Code File"
        upload_btn = tk.Button(
            file_frame, 
            text=upload_text,
            command=self.upload_file, 
            bg='#4CAF50', 
            fg='black',
            font=self.get_font('Arial', 10, 'bold'), 
            relief='flat' if self.is_mac else 'raised',
            activebackground='#45a049',
            cursor='hand2' if self.is_windows else 'pointinghand',
            highlightbackground='#4CAF50' if self.is_mac else '#4CAF50',  # macOS fix
            borderwidth=0 if self.is_mac else 1,
            pady=8 if self.is_mac else 0
        )
        upload_btn.pack(pady=5)
        
        # Printer control frame
        control_frame = ttk.LabelFrame(self.root, text="Printer Control", padding="10")
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Status display
        status_frame = tk.Frame(control_frame, bg='white')
        status_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            status_frame, 
            text="Status:", 
            font=self.get_font('Arial', 10, 'bold'), 
            bg='white'
        ).pack(side='left')
        
        status_label = tk.Label(
            status_frame, 
            textvariable=self.printer_status, 
            font=self.get_font('Arial', 10), 
            fg='#2196F3', 
            bg='white'
        )
        status_label.pack(side='left', padx=(5, 0))
        
        # Progress bar
        tk.Label(
            control_frame, 
            text="Print Progress:", 
            font=self.get_font('Arial', 10, 'bold')
        ).pack(anchor='w')
        
        progress_bar = ttk.Progressbar(
            control_frame, 
            variable=self.print_progress, 
            maximum=100, 
            length=400
        )
        progress_bar.pack(pady=(5, 10), fill='x')
        
        # Control buttons frame
        buttons_frame = tk.Frame(control_frame)
        buttons_frame.pack(fill='x')
        
        # Button configurations for different platforms
        base_button_config = {
            'font': self.get_font('Arial', 12, 'bold'),
            'width': 15,
            'cursor': 'hand2' if self.is_windows else 'pointinghand'
        }
        
        # macOS-specific button styling
        if self.is_mac:
            mac_button_style = {
                'relief': 'flat',
                'borderwidth': 0,
                'pady': 8
            }
            base_button_config.update(mac_button_style)
        else:
            base_button_config['relief'] = 'raised'
        
        # Start print button
        start_text = "▶️ Start Print" if not self.is_windows else "Start Print"
        start_btn = tk.Button(
            buttons_frame, 
            text=start_text,
            command=self.start_print, 
            bg='#2196F3', 
            fg='black',
            activebackground='#1976D2',
            highlightbackground='#2196F3' if self.is_mac else '#2196F3',
            **base_button_config
        )
        start_btn.pack(side='left', padx=(0, 10))
        
        # Pause button
        pause_text = "⏸️ Pause" if not self.is_windows else "Pause"
        pause_btn = tk.Button(
            buttons_frame, 
            text=pause_text,
            command=self.pause_print, 
            bg='#FF9800', 
            fg='black',
            activebackground='#F57C00',
            highlightbackground='#FF9800' if self.is_mac else '#FF9800',
            **base_button_config
        )
        pause_btn.pack(side='left', padx=(0, 10))
        
        # Stop button
        stop_text = "⏹️ Stop" if not self.is_windows else "Stop"
        stop_btn = tk.Button(
            buttons_frame, 
            text=stop_text,
            command=self.stop_print, 
            bg='#F44336', 
            fg='black',
            activebackground='#D32F2F',
            highlightbackground='#F44336' if self.is_mac else '#F44336',
            **base_button_config
        )
        stop_btn.pack(side='left')
        
                # ===== NEW: COORDINATE CONTROL FRAME =====
        coord_frame = ttk.LabelFrame(self.root, text="Manual Position Control", padding="10")
        coord_frame.pack(fill='x', padx=20, pady=10)

        # Variables for XYZ inputs (keep "0" as default but make it selectable)
        self.x_offset = tk.StringVar(value="0")
        self.y_offset = tk.StringVar(value="0")
        self.z_offset = tk.StringVar(value="0")

        # Grid layout for labels and entries
        ttk.Label(coord_frame, text="X Offset:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        x_entry = ttk.Entry(coord_frame, textvariable=self.x_offset, width=8)
        x_entry.grid(row=0, column=1, padx=5, pady=5)
        x_entry.bind("<FocusIn>", self.select_all_text)  # NEW: Auto-select on focus

        ttk.Label(coord_frame, text="Y Offset:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        y_entry = ttk.Entry(coord_frame, textvariable=self.y_offset, width=8)
        y_entry.grid(row=1, column=1, padx=5, pady=5)
        y_entry.bind("<FocusIn>", self.select_all_text)  # NEW: Auto-select on focus

        ttk.Label(coord_frame, text="Z Offset:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        z_entry = ttk.Entry(coord_frame, textvariable=self.z_offset, width=8)
        z_entry.grid(row=2, column=1, padx=5, pady=5)
        z_entry.bind("<FocusIn>", self.select_all_text)  # NEW: Auto-select on focus
            
            # Move button (styled to match your UI)
        move_btn = tk.Button(
            coord_frame,
            text="Move",
            command=self.execute_relative_move,
            bg='#4CAF50',
            fg='black',
            font=self.get_font('Arial', 10, 'bold'),
            relief='flat' if self.is_mac else 'raised',
            activebackground='#45a049',
            cursor='hand2' if self.is_windows else 'pointinghand',
            highlightbackground='#4CAF50' if self.is_mac else '#4CAF50',
            borderwidth=0 if self.is_mac else 1,
            pady=8 if self.is_mac else 0,
            width=8
        )
        move_btn.grid(row=3, columnspan=2, pady=(10, 5))


# --------------
# Functions that actually do stuff
# --------------
        
    def upload_file(self):
        """Handle file upload - accepts .txt, .gcode files"""
        file_types = [
            ("G-Code files", "*.gcode"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        # Platform-specific file dialog options
        dialog_options = {
            'title': "Select G-Code or Text File",
            'filetypes': file_types
        }
        
        # Add initial directory for better UX
        if self.is_mac:
            dialog_options['initialdir'] = os.path.expanduser('~/Desktop')
        else:
            dialog_options['initialdir'] = os.path.expanduser('~')
        
        filename = filedialog.askopenfilename(**dialog_options)
        
        if filename:
            # Cross-platform file path handling
            file_basename = os.path.basename(filename)
            self.current_file.set(file_basename)
            
            # Store full path for actual use
            self.filePath = filename
            
            messagebox.showinfo(
                "File Uploaded", 
                f"Successfully loaded: {file_basename}"
            )
    
   
    def start_print(self):
        """Start the print job"""
        if self.current_file.get() == "No file selected":
            messagebox.showwarning("No File", "Please upload a file first!")
            return
            
        if self.printer_status.get() == "Printing":
            messagebox.showinfo("Already Printing", "Print job is already in progress!")
            return
            
        self.printer_status.set("Printing")
        self.print_progress.set(0)
        messagebox.showinfo("Print Started", "Print job has been started!")
        
        try:
            # Gets the uploader to start sending the file
            uploader.start_print(self.filePath)
        except Exception as e:
            print(f"Error starting print: {e}")
            messagebox.showerror("Print Error", f"Failed to start print: {str(e)}")
            self.printer_status.set("Ready")
            return
            
        # Simulate print progress
        self.simulate_print_progress()
        
    def pause_print(self):
        """Pause the current print"""
        if self.printer_status.get() == "Printing":
            uploader.pause_print()
            self.printer_status.set("Paused")
            messagebox.showinfo("Print Paused", "Print job has been paused.")
        elif self.printer_status.get() == "Paused":
            uploader.resume_print()
            self.printer_status.set("Printing")
            messagebox.showinfo("Print Resumed", "Print job has been resumed.")
            self.simulate_print_progress()  # Resume progress simulation
            
    def stop_print(self):
        """Stop the current print"""
        if self.printer_status.get() in ["Printing", "Paused"]:
            result = messagebox.askyesno("Confirm Stop", "Are you sure you want to stop the print job?")
            if result:
                uploader.stop_print()
                self.printer_status.set("Ready")
                self.print_progress.set(0)
                messagebox.showinfo("Print Stopped", "Print job has been stopped.")
    
    def execute_relative_move(self):
        """ Send relative movement command based on entered offsets"""
        try:
            x = float(self.x_offset.get())
            y = float(self.y_offset.get())
            z = float(self.z_offset.get())
            
            # Example: Send G-code for relative movement
            gcode = f"G91\nG1 X{x} Y{y} Z{z}\nG90"  # Switch to relative, move, then back to absolute
            gcode = gcode.splitlines
            for line in gcode:
                uploader.send_gcode(line)
            print(f"Sending G-code: {gcode}")  # Replace with your actual serial comms
            
            # Optional: Update status
            self.printer_status.set(f"Moved: X{x} Y{y} Z{z}")
        except ValueError:
            messagebox.showerror("Error", "Invalid offset values (must be numbers)")
        
                    
    def simulate_print_progress(self):
        """Simulate print progress for demo purposes"""
        if self.printer_status.get() == "Printing" and self.print_progress.get() < 100:
            current_progress = self.print_progress.get()
            self.print_progress.set(current_progress + 1)
            if current_progress + 1 >= 100:
                self.printer_status.set("Complete")
                messagebox.showinfo("Print Complete", "Print job finished successfully!")
            else:
                # Continue progress simulation
                self.root.after(1000, self.simulate_print_progress)

def main():
    root = tk.Tk()
    
    # Platform-specific window setup
    if platform.system() == 'Darwin':  # macOS
        # macOS-specific optimizations
        root.createcommand('::tk::mac::Quit', root.quit)
    
    app = PrinterControlGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    main()