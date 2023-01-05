from numpy import meshgrid, arange, column_stack
from xml.etree.ElementTree import parse
from tkinter import Tk, LabelFrame, Button, filedialog, Entry, messagebox, Label, Frame, IntVar, Checkbutton
from tkinter.ttk import Progressbar
from os.path import basename, dirname, join
from threading import Thread
from math import isclose

TEXT_1 = """<?xml version="1.0" encoding="UTF-8"?>
                    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
                    <Document>
                        <name>TestPath.kml</name>
                        <StyleMap id="m_ylw-pushpin">
                            <Pair>
                                <key>normal</key>
                                <styleUrl>#s_ylw-pushpin</styleUrl>
                            </Pair>
                            <Pair>
                                <key>highlight</key>
                                <styleUrl>#s_ylw-pushpin_hl</styleUrl>
                            </Pair>
                        </StyleMap>
                        <Style id="s_ylw-pushpin">
                            <IconStyle>
                                <scale>1.1</scale>
                                <Icon>
                                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                                </Icon>
                                <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
                            </IconStyle>
                            <LineStyle>
                                <color>ffffaa00</color>
                            </LineStyle>
                        </Style>
                        <Style id="s_ylw-pushpin_hl">
                            <IconStyle>
                                <scale>1.3</scale>
                                <Icon>
                                    <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
                                </Icon>
                                <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
                            </IconStyle>
                            <LineStyle>
                                <color>ffffaa00</color>
                            </LineStyle>
                        </Style>
                        <Placemark>
                            <name>TestPath</name>
                            <styleUrl>#m_ylw-pushpin</styleUrl>
                            <LineString>
                                <tessellate>1</tessellate>
                                <coordinates>
"""
TEXT_2 = """                                </coordinates>
                        </LineString>
                        </Placemark>
                    </Document>
                    </kml>
"""


class GenPoints:
    selected_file = None
    final_file = None
    lat_list = []
    lon_list = []
    _split_at = 50000
    _is_running = False

    def __init__(self):
        # Creating tkinter window
        self.window = Tk()
        self.w_width = int(self.window.winfo_vrootwidth() / 2)
        self.w_height = int(self.window.winfo_vrootheight() / 1.5)
        self.window.wm_resizable(True, True)
        self.set_default_window_size()
        self.window.title('GeneratePoints')
        self.window.protocol("WM_DELETE_WINDOW", self._quit)

        # select file pane
        self.select_file = LabelFrame(self.window, text='Select *.kml file:')
        self.select_file.grid(row=0, column=0, sticky='w', padx=(10, 0))

        # select file window
        self.sf_label = Entry(self.select_file, width=int(self.w_width / 10))
        self.sf_label.pack(side='left', padx=(10, 10), pady=(10, 10))

        # select file button
        sf_button = Button(self.select_file, text='Select file', command=self.select_file_command)
        sf_button.pack(side='left', padx=(0, 10))

        # spacing pane
        self.spacing_pane = LabelFrame(self.window, text='Enter point spacing')
        self.spacing_pane.grid(row=1, column=0, sticky='w', padx=(10, 0))

        # select file window
        self.sp_label = Entry(self.spacing_pane, width=int(self.w_width / 30))
        self.sp_label.pack(side='left', padx=(10, 10), pady=(10, 10))
        self.sp_label.insert(0, '0.002')

        Label(self.spacing_pane, text='in degrees (Smaller value will generate more points)').pack(side='left')

        chk_btn_pane = Frame(self.window)
        chk_btn_pane.grid(row=2, column=0, sticky='w')
        self._separate = IntVar()
        self._separate.initialize(1)
        self.file_control = Checkbutton(chk_btn_pane,
                                        text="Separate files at 50,000 points (The generated kml file will split at "
                                             "every 50000 points if it is checked)",
                                        variable=self._separate,
                                        onvalue=1,
                                        offvalue=0)
        self.file_control.pack(side='left', pady=(10, 10))

        self.below_chk_btn = Frame(self.window)
        self.below_chk_btn.grid(row=3, column=0, sticky='w')

        self.below_label = Label(self.below_chk_btn, text='New Value:')

        self.new_split_val = Entry(self.below_chk_btn, width=int(self.w_width / 30))
        self.new_split_val.insert(0, '50000')

        self.set_new_split = Button(self.below_chk_btn, text='Set', command=self.set_new_split_command)

        self.sep_setting_btn = Button(chk_btn_pane, text='Settings', command=self.change_split_number)
        self.sep_setting_btn.pack(side='left')

        # elements on the bottom
        self.final_frame = Frame(self.window)
        self.final_frame.grid(row=4, column=0, sticky='w')

        # save file pane
        self.save_file = LabelFrame(self.final_frame, text='Save points to file:')
        self.save_file.pack(fill='x', padx=(10, 0))

        # save file window
        self.saf_label = Entry(self.save_file, width=int(self.w_width / 10))
        self.saf_label.pack(side='left', padx=(10, 10), pady=(10, 10))

        # save file button
        saf_button = Button(self.save_file, text='Select save location', command=self.save_file_command)
        saf_button.pack(side='left', padx=(0, 10))

        # enclosing frame
        frame = Frame(self.final_frame)
        frame.pack(side='top')

        # Convert Button
        self.run = Button(frame, text='Convert', command=self.start_gen_points, width=int(self.w_width / 20), height=2)
        self.run.pack(side='left', padx=(10, 10), pady=(10, 10))

        # frame2
        frame2 = Frame(self.final_frame)
        frame2.pack(side='top')
        self.progress_text = Label(frame2, text='')
        self.progress_bar = Progressbar(frame2, orient='horizontal', mode='indeterminate',
                                        length=self.w_width / 5)

        self.window.mainloop()

    def set_new_split_command(self):
        try:
            split_val = int(self.new_split_val.get())
        except ValueError:
            messagebox.showerror('Error', 'Invalid spacing')
            self.progress_bar.pack_forget()
            return
        if split_val <= 0:
            messagebox.showinfo('Warning', 'Enter spacing')
            return
        self._split_at = split_val
        self.file_control.configure(text=f"Separate files at {split_val} points (The generated kml file will split at "
                                         f"every {split_val} points if it is checked)")
        self.below_label.pack_forget()
        self.new_split_val.pack_forget()
        self.set_new_split.pack_forget()

        self.final_frame.grid(row=3, column=0, sticky='w')

    def change_split_number(self):
        self.final_frame.grid_forget()
        self.below_label.pack(side='left', pady=(0, 10), padx=(10, 0))
        self.new_split_val.pack(side='left', pady=(0, 10), padx=(10, 0))
        self.set_new_split.pack(side='left', pady=(0, 10), padx=(10, 0))

    def start_gen_points(self):
        if self._is_running is True:
            return
        self._is_running = True
        t = Thread(target=self.gen_points)
        t.daemon = True

        self.progress_text.pack(side='left')
        self.progress_text.config(text='Loading...')
        self.progress_bar.pack(side='left')
        self.progress_bar.start(25)
        t.start()

    # for minimizing the window or setting the window to default pos and size
    def set_default_window_size(self):
        h = self.window.winfo_vrootheight()
        w = self.window.winfo_vrootwidth()
        self.window.geometry(f'{int(w / 2.5)}x{int(h / 2.5)}+{int(w / 4)}+{int(h / 6)}')

    def select_file_command(self):
        self.sf_label.delete(0, 'end')
        self.selected_file = filedialog.askopenfilename(title='Choose pdf files',
                                                        filetypes=(('kml file', '*.kml'), ('all file', '*.*')))
        self.sf_label.insert(0, self.selected_file)

    def save_file_command(self):
        if self.selected_file is None:
            messagebox.showerror('Warning', 'Select File First')
            return
        self.saf_label.delete(0, 'end')
        self.final_file = filedialog.asksaveasfilename(title='Choose save location',
                                                       defaultextension='*.kml',
                                                       filetypes=(('File name', '*.kml'), ('All files', '*.*')))
        self.saf_label.insert(0, self.final_file)

    def _quit(self):
        self.window.quit()
        self.window.destroy()

    def gen_points(self):
        self.progress_text.config(text='Generating points...')
        if self.selected_file is None:
            messagebox.showerror('Error', 'Select file first')
            self.progress_bar.pack_forget()
            self.progress_text.pack_forget()
            return

        elif self.final_file is None:
            messagebox.showerror('Error', 'Choose save location')
            self.progress_bar.pack_forget()
            self.progress_text.pack_forget()
            return

        else:
            pass

        try:
            spacing = float(self.sp_label.get())
        except ValueError:
            messagebox.showerror('Error', 'Invalid spacing')
            self.progress_bar.pack_forget()
            return

        if spacing <= 0:
            messagebox.showinfo('Warning', 'Enter spacing')
            return

        tree = parse(self.selected_file)
        root = tree.getroot()
        co_ords = ''
        for child in root.iter():
            if str(child.tag) == '{http://www.opengis.net/kml/2.2}coordinates':
                co_ords = child.text
                break

        co_ords_list = []
        y = 0
        for i in co_ords.split(','):
            i = i.strip('\n')
            while '\t' in i:
                i = i.strip('\t')

            if '0 ' in i:
                i = i[2:len(i) - 1]

            if y != 0:
                y = i
                if y == '':
                    break
            y = -1
            co_ords_list.append(float(i))

        co_ords_list.pop()
        co_ords_list.pop()
        polygon = [(co_ords_list[i], co_ords_list[i + 1]) for i in range(0, len(co_ords_list), 2)]

        def point_in_polygon(point, poly):
            dx, dy = point
            n = len(poly)
            inside = False
            x_inters = 0

            p1x, p1y = poly[0]
            for pt in range(n + 1):
                p2x, p2y = poly[pt % n]
                if dy > min(p1y, p2y):
                    if dy <= max(p1y, p2y):
                        if dx <= max(p1x, p2x):
                            if p1y != p2y:
                                x_inters = (dy - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if isclose(p1x,p2x, rel_tol=3*spacing) or dx <= x_inters:
                                inside = not inside
                p1x, p1y = p2x, p2y

            return inside

        def calculate_grid_points(poly, spc):
            # Get the bounds of the polygon
            minx = min(dx for dx, dy in poly)
            miny = min(dy for dx, dy in poly)
            max_x = max(dx for dx, dy in poly)
            maxy = max(dy for dx, dy in poly)

            # Generate a grid of points using NumPy
            xs, ys = meshgrid(arange(minx, max_x, spc), arange(miny, maxy, spc))
            pts = column_stack((xs.flatten(), ys.flatten()))

            # Filter out points that are outside the polygon
            pts = [point for point in pts if point_in_polygon(point, poly)]

            return pts

        points = calculate_grid_points(polygon, spacing)
        self.lat_list = [i[0] for i in points]
        self.lon_list = [i[1] for i in points]

        self.progress_text.config(text='Formatting and Writing points...')

        f = None
        if self._separate.get() == 1:
            val = self._split_at
            for i in range(len(points)):
                if i % val == 0:
                    if f is not None:
                        f.write(TEXT_2)
                        f.close()
                    name = basename(self.final_file).replace('.kml', f'_{int(i/val)}.kml')
                    filename = join(dirname(self.final_file), name)
                    f = open(filename, 'w')
                    f.write(TEXT_1)
                f.write(f'\t\t\t\t\t{points[i][0]},{points[i][1]},0\n')
        else:
            with open(self.final_file, 'w') as f:
                f.write(TEXT_1)
                for i, j in points:
                    f.write(f'\t\t\t\t\t{i},{j},0\n')
                f.write(TEXT_2)

        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_text.config(text=f'Done..\n Total Points Generated = {len(self.lat_list)}')
        self._is_running = False


if __name__ == '__main__':
    GenPoints()
