from numpy import meshgrid, arange, column_stack
from matplotlib.pyplot import scatter, show
from xml.etree.ElementTree import parse
from tkinter import Tk, LabelFrame, Button, filedialog, Entry, messagebox, Label, Frame
from tkinter.ttk import Progressbar
from os.path import basename, dirname, join
from threading import Thread


class GenPoints:
    selected_file = None
    final_file = None
    lat_list = []
    lon_list = []

    def __init__(self):
        # Creating tkinter window
        self.window = Tk()
        self.w_width = int(self.window.winfo_vrootwidth() / 2)
        self.w_height = int(self.window.winfo_vrootheight() / 1.5)
        # self.window.wm_maxsize(self.window.winfo_screenwidth(), self.window.winfo_screenheight())
        # self.window.wm_resizable(False, False)
        self.set_default_window_size()
        self.window.title('GeneratePoints')
        self.window.protocol("WM_DELETE_WINDOW", self._quit)

        # select file pane
        self.select_file = LabelFrame(self.window, text='Select *.kml file:')
        self.select_file.pack(fill='x')

        # select file window
        self.sf_label = Entry(self.select_file, width=int(self.w_width / 10))
        self.sf_label.pack(side='left', padx=(10, 10), pady=(10, 10))

        # select file button
        sf_button = Button(self.select_file, text='Select file', command=self.select_file_command)
        sf_button.pack(side='left')

        # spacing pane
        self.spacing_pane = LabelFrame(self.window, text='Enter point spacing')
        self.spacing_pane.pack(fill='x')

        # select file window
        self.sp_label = Entry(self.spacing_pane, width=int(self.w_width / 30))
        self.sp_label.pack(side='left', padx=(10, 10), pady=(10, 10))
        self.sp_label.insert(0, '0.002')

        Label(self.spacing_pane, text='in degrees (Smaller value will generate more points)').pack(side='left')

        # save file pane
        self.save_file = LabelFrame(self.window, text='Save points to file:')
        self.save_file.pack(fill='x')

        # save file window
        self.saf_label = Entry(self.save_file, width=int(self.w_width / 10))
        self.saf_label.pack(side='left', padx=(10, 10), pady=(10, 10))

        # save file button
        saf_button = Button(self.save_file, text='Select save location', command=self.save_file_command)
        saf_button.pack(side='left')

        # enclosing frame
        frame = Frame(self.window)
        frame.pack()

        # Convert Button
        self.run = Button(frame, text='Convert', command=self.start_gen_points, width=int(self.w_width / 20), height=2)
        self.run.pack(side='left', padx=(10, 10), pady=(10, 10))

        # Preview Button
        self.pb = Button(frame, text='Show in Graph', command=self.plot_graph, width=int(self.w_width / 20),
                         height=2)

        self.progress_text = Label(self.window, text='')
        self.progress_bar = Progressbar(self.window, orient='horizontal', mode='indeterminate', length=self.w_width/5)

        self.window.mainloop()

    def start_gen_points(self):
        t = Thread(target=self.gen_points)
        t.daemon = True
        self.progress_text.pack(side='left')
        self.progress_text.config(text='Loading...')
        self.progress_bar.pack(side='left')
        self.progress_bar.start(25)
        t.start()

    def plot_graph(self):
        if self.lat_list == [] or self.lon_list == []:
            return
        scatter(self.lat_list, self.lon_list)
        show()

    # for minimizing the window or setting the window to default pos and size
    def set_default_window_size(self):
        h = self.window.winfo_vrootheight()
        w = self.window.winfo_vrootwidth()
        self.window.geometry(f'{int(w / 2)}x{int(h / 3)}+{int(w / 4)}+{int(h / 6)}')

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

        if spacing == 0:
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
        x = 0
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
                y = 0
            else:
                x = i
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
            for j in range(n + 1):
                p2x, p2y = poly[j % n]
                if dy > min(p1y, p2y):
                    if dy <= max(p1y, p2y):
                        if dx <= max(p1x, p2x):
                            if p1y != p2y:
                                x_inters = (dy - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or dx <= x_inters:
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

        def save_file(n):
            name = basename(self.final_file).replace('.kml', f'_{n}.kml')
            filename = join(dirname(self.final_file), name)
            f = open(filename, 'w')
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
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
                    {text}
                                </coordinates>
                        </LineString>
                        </Placemark>
                    </Document>
                    </kml>
                    """)
            f.close()

        text = ''
        for i in range(len(points)):
            t = i % 50000
            if t == 0 and i != 0:
                text += f'\t\t\t\t\t{self.lat_list[i]},{self.lon_list[i]},0'
                save_file(int(i/50000))
                text = ''
            elif i == len(points) - 1:
                text += f'\t\t\t\t\t{self.lat_list[i]},{self.lon_list[i]},0'
                save_file(int(i/50000)+1)
                break
            else:
                pass
            text += f'\t\t\t\t\t{self.lat_list[i]},{self.lon_list[i]},0\n'

        self.pb.pack(side='left')
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_text.config(text=f'Done.. Total Points Generated = {len(self.lat_list)}')


if __name__ == '__main__':
    GenPoints()
