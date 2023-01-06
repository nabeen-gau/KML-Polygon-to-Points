from numpy import meshgrid, arange, column_stack, array, append
from matplotlib.pyplot import scatter, show
from matplotlib.path import Path
from xml.etree.ElementTree import parse
from tkinter import Tk, LabelFrame, Button, filedialog, Entry, messagebox, Label, Frame, IntVar, Checkbutton
from tkinter.ttk import Progressbar
from os.path import basename, dirname, join
from threading import Thread
from kml_format import TEXT_1, TEXT_2, TEXT_3, TEXT_4
from time import sleep


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

        # Preview Button
        self.pb = Button(frame, text='Show in Graph', command=self.plot_graph, width=int(self.w_width / 20),
                         height=2)

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

        self.pb.pack_forget()
        self.progress_text.pack(side='left')
        self.progress_text.config(text='Loading...')
        self.progress_bar.pack(side='left')
        self.progress_bar.start(25)
        t.start()

    def plot_graph(self):
        if self.lat_list.size == 0 or self.lon_list.size == 0:
            return
        scatter(self.lat_list, self.lon_list)
        show()

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
        if self.selected_file is None or self.selected_file == '':
            messagebox.showerror('Error', 'Select file first')
            self.progress_bar.pack_forget()
            self.progress_text.pack_forget()
            return

        elif self.final_file is None or self.final_file == '':
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

        co_ords_list = array([])
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
            co_ords_list = append(co_ords_list, float(i))

        co_ords_list = co_ords_list[0:co_ords_list.size - 2]
        polygon = co_ords_list.reshape(int(co_ords_list.size / 2), 2)

        self.progress_text.config(text='Generating Points...')
        # Get the bounds of the polygon
        min_cords = polygon.min(axis=0)
        max_cords = polygon.max(axis=0)

        # Generate a grid of points using NumPy
        xs, ys = meshgrid(arange(min_cords[0], max_cords[0], spacing), arange(min_cords[1], max_cords[1], spacing))
        pts = column_stack((xs.flatten(), ys.flatten()))

        if pts.size > 3000000:
            query = messagebox.askyesno('Do you want to continue?', 'The no. of points generated is more than 3 '
                                                                    'million and will take some time to complete '
                                                                    'processing. Do you still want to continue? '
                                                                    'The program may freeze for a while. '
                                                                    'You can cancel and change spacing if you want by '
                                                                    'saying No.')
            if not query:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self._is_running = False
                self.progress_text.config(text='')
                return

        self.progress_text.config(text='Filtering Points...(The program may not respond for a while)')
        sleep(0.1)
        # Filter out points that are outside the polygon
        path = Path(polygon)
        pts_cond = path.contains_points(pts)
        points = []
        for pt in range(int(pts.size / 2)):
            if pts_cond[pt]:
                points.append(pts[pt])

        points = array(points)
        self.lat_list, self.lon_list = points.T
        self.progress_text.config(text='Writing points...')

        f = None
        if self._separate.get() == 1:
            val = self._split_at
            for i in range(points.size):
                if i % val == 0:
                    if f is not None:
                        f.write(TEXT_4)
                        f.close()
                    name = basename(self.final_file).replace('.kml', f'_{int(i / val)}.kml')
                    filename = join(dirname(self.final_file), name)
                    f = open(filename, 'w')
                    f.write(TEXT_1 + name + TEXT_2 + name + TEXT_3)
                f.write(f'\t\t\t\t\t{points[i][0]},{points[i][1]},0\n')
            f.write(TEXT_4)
        else:
            with open(self.final_file, 'w') as f:
                f.write(TEXT_1 + basename(self.final_file) + TEXT_2 + basename(self.final_file) + TEXT_3)
                for i, j in points:
                    f.write(f'\t\t\t\t\t{i},{j},0\n')
                f.write(TEXT_4)

        self.pb.pack(side='left')
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_text.config(text=f'Done..\n Total Points Generated = {self.lat_list.size}')
        self._is_running = False


if __name__ == '__main__':
    GenPoints()
