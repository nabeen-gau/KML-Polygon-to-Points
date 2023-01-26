from tkinter import Tk, Canvas, Button
from time import sleep
from threading import Thread
from math import sqrt, sin, cos, pi

def distance(x1, y1, x2, y2):
    return sqrt((x2-x1)**2+(y2-y1)**2)

def midpoint(x1, y1, x2, y2):
    return (x1+x2)/2, (y1+y2)/2

def slope(x1, y1, x2, y2):
    if x1 == x2:
        return None
    else:
        return (y2-y1)/(x2-x1)

def get_label_pos(x1, y1, x2, y2, offset=20):
    xm ,ym = midpoint(x1, y1, x2, y2)
    m = slope(x1, y1, x2, y2)
    if m is None:
        return xm+offset, ym
    else:
        return xm-offset*sin(m), ym+offset*cos(m)

class GridView(Canvas):
    spacing = 50
    grid_lines_x = []
    grid_lines_y = []
    elements = []
    _zoom_increment = 10
    _zoom_decrement = 10
    _btn_click_pos = [0, 0]
    _drag_mouse_pos = [0, 0]
    _offset_movement = [0, 0]
    _orig_btn_click_pos = [0, 0]
    _prev_move = {}
    _limit_zoom = False
    _current_scale = 1.0
    _draw = True
    _drawing_line = None
    _scan_drag_pos = (200, 750)
    _dragging = False
    _move_start_pos = (0, 0)
    _move_end_pos = (0, 0)
    _total_drag_x = 0
    _total_drag_y = 0
    _drawing_scale_correction = (0, 0)
    _zoom_correction_applied = True
    _snap_condition = True
    _snap_interval_x = 100
    _snap_interval_y = 100

    _unit_snap_number_x = 10
    _unit_snap_number_y = 10

    _snap_list_x = []
    _snap_list_y = []

    _draw_event_running = False
    _drag_and_draw_trigger = False

    _draw_session_start = True

    drawn_lines = []
    drawn_labels = []

    hide_label_from_scale = 1
    _line_labels_shown = True

    decimal_precision = 3
    _line_label = None
    _unit_distance = 100
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_grid_x(y_limits=(-2000, 2000), length=2000, spacing=50, end=True, start_x = -2000)
        self.create_grid_y(x_limits=(-2000, 2000), length=2000, spacing=50, end=True, start_y = -2000)

        self.create_grid_x_label(-2000, 2000, spacing=50, label_spacing=1)
        self.create_grid_y_label(-2000, 2000, spacing=50, label_spacing=1)

        self.scale("all", 0, 0, 2, 2)
        self._current_scale = self._current_scale*2
        self.scan_dragto(self._scan_drag_pos[0], self._scan_drag_pos[1], gain=1)

        self.bind("<MouseWheel>", self.on_mousewheel)
        self.bind("<Button-1>", self.on_mouse_click)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.master.bind("<Escape>", lambda e:self.draw_stop(change_session = False))
        self.master.bind("<Return>", lambda e:self.draw_stop(change_session = False))

        # Button(self, text="draw_start", command=self.draw_start).pack()
        # Button(self, text="draw_stop", command=self.draw_stop).pack()
        # Button(self, text="hide_labels", command=self.hide_line_labels).pack()
        # Button(self, text="show_labels", command=self.show_line_labels).pack()
    
    
    def draw_start(self):
        self._draw_session_start = True

    def draw_stop(self, change_session=True):
        self.unbind("<Motion>")
        if self._drawing_line is not None:
            self.delete(self._drawing_line, self._line_label)
        self._draw_session_start = False
        if not change_session:
            self.draw_start()

    def start_drawing_line(self, x, y):
        drawing_thread = Thread(target=self.draw_line_start, args=[x,y])
        self._drag_and_draw_trigger = False
        drawing_thread.start()

    def draw_line_start(self, x, y):
        sleep(0.2)
        if self._draw is False:
            return
        self.unbind("<Motion>")
        self.bind("<Motion>", lambda event: self.draw_line(x,y, event.x, event.y))
        self._draw_event_running = not self._draw_event_running

    def draw_line(self, x1, y1, x2, y2):
        if self._draw is False:
            self.unbind("<Motion>")
            return
        
        if not self._zoom_correction_applied:
            draw_x1, draw_y1= self.coords(self._drawing_line)[0:2]
        else:
            draw_x1 = x1-self._scan_drag_pos[0]-self._total_drag_x
            draw_y1 = y1-self._scan_drag_pos[1]-self._total_drag_y
        
        if self._drawing_line is not None:
            if self._draw_event_running:
                self.delete(self._drawing_line)
                self.delete(self._line_label)
            else:
                coords = self.coords(self._drawing_line)
                if coords!=[]:
                    self.coords(self._line_label, *get_label_pos(*coords))
                    self.drawn_lines.append(self._drawing_line)
                    self.drawn_labels.append(self._line_label)
                self._draw_event_running = not self._draw_event_running
            
        draw_x2 = x2-self._scan_drag_pos[0]-self._total_drag_x
        draw_y2 = y2-self._scan_drag_pos[1]-self._total_drag_y

        if self._snap_condition:
            draw_x1, draw_y1, draw_x2, draw_y2 = self.get_snapped_coords_from_grid(draw_x1, draw_y1, draw_x2, draw_y2)
          
        self._drawing_line = self.create_line(draw_x1, draw_y1, draw_x2, draw_y2)
        h_dist = round((draw_x2 - draw_x1)/self._snap_interval_x/self._current_scale*2, self.decimal_precision)
        v_dist = -round((draw_y2 - draw_y1)/self._snap_interval_y/self._current_scale*2, self.decimal_precision)
        if v_dist == 0:
            slope_val = "inf"
        else:
            slope_val = round(h_dist/v_dist, 1)
        self._line_label = self.create_text(draw_x2+25, draw_y2-30,
                                            text=f"H:{h_dist}\nV:{v_dist}\n1V:{slope_val}H",
                                            fill="green")

    def get_snapped_coords(self, x1, y1, x2, y2):
        if not self._zoom_correction_applied:
            snap_scale_x = self._snap_interval_x*self._current_scale/2
            snap_scale_y = self._snap_interval_y*self._current_scale/2

        else:
            snap_scale_x = self._snap_interval_x
            snap_scale_y = self._snap_interval_y
        return (round(x1/snap_scale_x)*snap_scale_x,
               round(y1/snap_scale_y)*snap_scale_y,
               round(x2/snap_scale_x)*snap_scale_x,
               round(y2/snap_scale_y)*snap_scale_y)

    def _update_snapped_coords_list(self):
        self._snap_list_x = []
        self._snap_list_y = []
        for i in self.grid_lines_x:
            y = self.coords(i)[1]
            for k in range(self._unit_snap_number_y):
                self._snap_list_y.append(y+k*self._snap_interval_y/self._unit_snap_number_y*self._current_scale/2)
        for j in self.grid_lines_y:
            x = self.coords(j)[0]
            for k in range(self._unit_snap_number_x):
                self._snap_list_x.append(x+k*self._snap_interval_x/self._unit_snap_number_x*self._current_scale/2)
    
    def get_snapped_coords_from_grid(self, x1, y1, x2, y2):
        self._update_snapped_coords_list()
        return (min(self._snap_list_x, key=lambda x:abs(x-x1)),
                min(self._snap_list_y, key=lambda x:abs(x-y1)),
                min(self._snap_list_x, key=lambda x:abs(x-x2)),
                min(self._snap_list_y, key=lambda x:abs(x-y2)))

    def on_mouse_click(self, event):
        self._draw = True
        self._zoom_correction_applied = True
        self._btn_click_pos = [event.x, event.y]
        self.bind("<Motion>", self.on_mouse_drag)
        if self._offset_movement == [0, 0]:
            self._offset_movement = self._scan_drag_pos
        if self._draw_session_start:
            self.start_drawing_line(event.x, event.y)


    def on_mouse_drag(self, event):
        self._draw = False
        
        move_x = event.x-self._btn_click_pos[0]+self._offset_movement[0]
        move_y = event.y-self._btn_click_pos[1]+self._offset_movement[1]
        self.scan_dragto(move_x, move_y, gain=1)
        self.scan_mark(move_x, move_y)
        if not self._dragging:
            self._move_start_pos = event.x, event.y
            self._dragging = True
            

    def on_mouse_release(self, event):
        self.unbind("<Motion>")
        if self._dragging:
            self._dragging = False
            self._move_end_pos = event.x, event.y
            self._total_drag_x += self._move_end_pos[0]-self._move_start_pos[0]
            self._total_drag_y += self._move_end_pos[1]-self._move_start_pos[1]

        self._offset_movement = [event.x, event.y]
        self.scan_mark(event.x, event.y)

    def create_grid_x(self, y_limits=(0, 0), x=0, length=1000, spacing=50, end=True, start_x = 0):
        self._orig_y_limits = y_limits
        self.spacing = spacing
        for i in range(y_limits[0], y_limits[1]+1, spacing):
            for k in range(self._unit_snap_number_y):
                self._snap_list_y.append(i+k*self._snap_interval_y/self._unit_snap_number_y)
            
            if i == (y_limits[0]+y_limits[1])/2:
                line = self.create_line(start_x, i, length, i)
            else:
                line = self.create_line(start_x ,i ,length, i, fill="grey", dash=(1,1))
            if end:
                self.grid_lines_x.append(line)
            else:
                self.grid_lines_x = [line] + self.grid_lines_x
    
    def create_grid_y(self, x_limits=(0,0), y=0, length=1000, spacing=50, end=True, start_y = 0):
        self._orig_x_limits = x_limits
        self.spacing = spacing
        for i in range(x_limits[0], x_limits[1]+1, spacing):
            for k in range(self._unit_snap_number_x):
                self._snap_list_x.append(i+k*self._snap_interval_x/self._unit_snap_number_x)
            
            if i == (x_limits[0]+x_limits[1])/2:
                line = self.create_line(i, start_y, i, length)
            else:
                line = self.create_line(i, start_y, i, length, fill="grey", dash=(1,1))
            if end:
                self.grid_lines_y.append(line)
            else:
                self.grid_lines_y = [line] + self.grid_lines_y

    def create_grid_x_label(self, left_lim, right_lim, spacing=10, label_spacing=1):
        for i in range(left_lim, right_lim, spacing):
            self.create_text(i+5, 5, text=f"{int(i/spacing*label_spacing)}")

    def create_grid_y_label(self, up_lim, down_lim, spacing=10, label_spacing=1):
        for i in range(up_lim, down_lim, spacing):
            self.create_text(5, i+5, text=f"{int(-i/spacing*label_spacing)}")

    def get_mouse_position_on_window(self):
        ptr_x, ptr_y = self.winfo_pointerxy()
        win_x = self.master.winfo_x()
        win_y = self.master.winfo_y()
        return ptr_x-win_x, ptr_y-win_y

    def get_mouse_pos_on_grid(self):
        x_cond, y_cond = self.get_mouse_position_on_window()

        x_var = len(self.grid_lines_y)
        y_var = len(self.grid_lines_x)
        for nbr in range(len(self.grid_lines_x)):
            if self.coords(self.grid_lines_x[nbr])[1] > y_cond:
                y_var = nbr
                break

        for nbr in range(len(self.grid_lines_y)):
            if self.coords(self.grid_lines_y[nbr])[0] > x_cond:
                x_var = nbr
                break

        return x_var, y_var

    def on_mousewheel(self, event):
        self._zoom_correction_applied = False
        x, y = self.get_mouse_position_on_window()
        x -= self._scan_drag_pos[0]+self._total_drag_x
        y -= self._scan_drag_pos[1]+self._total_drag_y
        
        if event.delta > 0:
            self.scale("all", x, y, 1.3, 1.3)
            self._current_scale = self._current_scale*1.3
        else:
            self.scale("all", x, y, 1/1.3, 1/1.3)
            self._current_scale = self._current_scale/1.3
        
        if self._current_scale < self.hide_label_from_scale and self._line_labels_shown:
            self.hide_line_labels()
            self._line_labels_shown = False
        if self._current_scale > self.hide_label_from_scale and not self._line_labels_shown:
            self.show_line_labels()
            self._line_labels_shown = True


    def adjust_grid_lines(self):
        xw1, yw1 = self.get_window_size()

        for i in self.grid_lines_x:
            x1, y1, x2, y2 = self.coords(i)
            self.coords(i, 0, y1, xw1, y2)

        for j in self.grid_lines_y:
            x1, y1, x2, y2 = self.coords(j)
            self.coords(j, x1, 0, x2, yw1)


    def clear_grid(self):
        for i in self.grid_lines_x:
            self.delete(i)
        for j in self.grid_lines_y:
            self.delete(j)

    def get_window_size(self):
        return self.winfo_screenwidth(), self.winfo_screenheight()
    
    def hide_line_labels(self):
        for i in self.drawn_labels:
            self.itemconfig(i, state='hidden')
    
    def show_line_labels(self):
        for i in self.drawn_labels:
            self.itemconfig(i, state='normal')



if __name__ == '__main__':
    window = Tk()
    window.wm_state('zoomed')
    fr = GridView(window)
    fr.pack(fill='both', expand=True)
    window.mainloop()

