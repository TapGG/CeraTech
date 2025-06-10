import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk  # Required for image handling

class PrinterControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CeraTech")
        self.root.geometry("600x400")
        self.root.configure(bg='#f0f0f0')  # Main window background
        
        # Remove default window decorations (title bar)
        self.root.overrideredirect(True)
        
        # ===== TOP BAR (LOGO + DRAG AREA + CLOSE BUTTON) =====
        self.top_frame = tk.Frame(self.root, bg='#f0f0f0')  # Match window background
        self.top_frame.pack(fill=tk.X, pady=(5, 0))  # Small padding at top
        
        # 1. Logo (left side)
        try:
            self.logo_img = Image.open("logo.png").convert("RGBA")  # Supports transparency
            self.logo_img = self.logo_img.resize((300, 100), Image.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(self.logo_img)
            self.logo_label = tk.Label(
                self.top_frame, 
                image=self.logo_tk, 
                bg='#f0f0f0'  # Match window bg
            )
            self.logo_label.image = self.logo_tk  # Keep reference
            self.logo_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Logo error: {e}")
            # Fallback text if image fails
            tk.Label(
                self.top_frame, 
                text="CeraTech", 
                font=('Arial', 12), 
                bg='#f0f0f0'
            ).pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            print(f"Could not load logo image: {e}")
            # Fallback text if image fails to load
            tk.Label(self.title_bar, text="CeraTech", bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=10)
        
        self.close_btn = tk.Button(
            self.top_frame,
            text="✕",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#333333',
            bd=0,
            relief=tk.FLAT,
            activebackground='#ff4444',
            activeforeground='white',
            command=self.root.destroy
        )
        self.close_btn.pack(side=tk.RIGHT, padx=10)
        
        # Variables
        self.current_file = tk.StringVar(value="No file selected")
        self.printer_status = tk.StringVar(value="Ready")
        self.print_progress = tk.DoubleVar(value=0)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main title
        title_label = tk.Label(self.root, text="3D Printer Control Panel", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="File Management", padding="10")
        file_frame.pack(fill='x', padx=20, pady=10)
        
        # Current file display
        tk.Label(file_frame, text="Selected File:", font=('Arial', 10, 'bold')).pack(anchor='w')
        file_display = tk.Label(file_frame, textvariable=self.current_file, 
                               font=('Arial', 9), fg='#666', wraplength=500)
        file_display.pack(anchor='w', pady=(0, 10))
        
        # Upload button
        upload_btn = tk.Button(file_frame, text="📁 Upload G-Code File", 
                              command=self.upload_file, bg='#4CAF50', fg='white',
                              font=('Arial', 10, 'bold'), relief='raised',
                              activebackground='#45a049')
        upload_btn.pack(pady=5)
        
        # Printer control frame
        control_frame = ttk.LabelFrame(self.root, text="Printer Control", padding="10")
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Status display
        status_frame = tk.Frame(control_frame, bg='white')
        status_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(status_frame, text="Status:", font=('Arial', 10, 'bold'), bg='white').pack(side='left')
        status_label = tk.Label(status_frame, textvariable=self.printer_status, 
                               font=('Arial', 10), fg='#2196F3', bg='white')
        status_label.pack(side='left', padx=(5, 0))
        
        # Progress bar
        tk.Label(control_frame, text="Print Progress:", font=('Arial', 10, 'bold')).pack(anchor='w')
        progress_bar = ttk.Progressbar(control_frame, variable=self.print_progress, 
                                      maximum=100, length=400)
        progress_bar.pack(pady=(5, 10), fill='x')
        
        # Control buttons frame
        buttons_frame = tk.Frame(control_frame)
        buttons_frame.pack(fill='x')
        
        # Start print button
        start_btn = tk.Button(buttons_frame, text="▶️ Start Print", 
                             command=self.start_print, bg='#2196F3', fg='white',
                             font=('Arial', 12, 'bold'), relief='raised',
                             activebackground='#1976D2', width=15)
        start_btn.pack(side='left', padx=(0, 10))
        
        # Pause button
        pause_btn = tk.Button(buttons_frame, text="⏸️ Pause", 
                             command=self.pause_print, bg='#FF9800', fg='white',
                             font=('Arial', 12, 'bold'), relief='raised',
                             activebackground='#F57C00', width=15)
        pause_btn.pack(side='left', padx=(0, 10))
        
        # Stop button
        stop_btn = tk.Button(buttons_frame, text="⏹️ Stop", 
                            command=self.stop_print, bg='#F44336', fg='white',
                            font=('Arial', 12, 'bold'), relief='raised',
                            activebackground='#D32F2F', width=15)
        stop_btn.pack(side='left')
        
        
    def upload_file(self):
        """Handle file upload - accepts .txt, .gcode files"""
        file_types = [
            ("G-Code files", "*.gcode"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select G-Code or Text File",
            filetypes=file_types
        )
        
        if filename:
            self.current_file.set(os.path.basename(filename))
            messagebox.showinfo("File Uploaded", f"Successfully loaded: {os.path.basename(filename)}")
            
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
        
        # Simulate print progress (in real application, this would be actual printer feedback)
        self.simulate_print_progress()
        
    def pause_print(self):
        """Pause the current print"""
        if self.printer_status.get() == "Printing":
            self.printer_status.set("Paused")
            messagebox.showinfo("Print Paused", "Print job has been paused.")
        elif self.printer_status.get() == "Paused":
            self.printer_status.set("Printing")
            messagebox.showinfo("Print Resumed", "Print job has been resumed.")
            
    def stop_print(self):
        """Stop the current print"""
        if self.printer_status.get() in ["Printing", "Paused"]:
            result = messagebox.askyesno("Confirm Stop", "Are you sure you want to stop the print job?")
            if result:
                self.printer_status.set("Ready")
                self.print_progress.set(0)
                messagebox.showinfo("Print Stopped", "Print job has been stopped.")
                
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
    app = PrinterControlGUI(root)
    root.mainloop()


main()