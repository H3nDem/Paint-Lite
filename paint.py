from tkinter import PhotoImage, Tk, Canvas, Frame, Menu, filedialog, messagebox
from PIL import ImageGrab, Image, ImageTk

WIN_HEIGHT = 684
WIN_WIDTH = 912
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
COLORS = ['black', 'gray', '#9e5700', 'brown', 'red', '#fcba03', 'yellow', '#5fb53e', 'green','#4287f5', 'blue', '#5632a8', 'purple', 'pink', 'white']
THICKNESS = [5, 10, 15, 20]
BRUSHES = ['line', 'rectangle', 'oval']
STROKE_BUFFER_SIZE = 20


class Paint(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.brush = BRUSHES[0] # brush style
        self.color = COLORS[0]
        self.thickness = THICKNESS[0]
        self.modified = 0 # Used to confirm before closing the app if we've update our drawing
        self.config(background="lightgray")
        self.image_title = 'Untitled'
        self.image_path = None
        self.init_app_menu()
        self.init_canvas()
        self.init_color_palette()
        self.init_thickness_palette()
        self.init_brush_palette()
        self.bind_keys()


    def init_app_menu(self):
        self.main_menu = Menu(self)
        self.main_menu.add_command(label='New', command=self.clear_canvas)
        self.main_menu.add_command(label='Open', command=self.open_image)
        self.main_menu.add_command(label='Save', command=self.save_image)
        self.main_menu.add_command(label='Save as', command=self.save_image_as)
        self.main_menu.add_command(label="Exit", command=self.quit_app)
        self.config(menu=self.main_menu)

    def init_canvas(self):
        self.canvas_frame = Frame(self)
        self.canvas_frame.place(x=WIN_WIDTH*0.05, y=WIN_HEIGHT*0.10)
        self.canvas = Canvas(self.canvas_frame, bg='white', width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

    def init_color_palette(self):
        self.color_palette_frame = Frame(self)
        self.color_palette_frame.place(x=WIN_WIDTH*0.05, y=WIN_HEIGHT*0.03)
        self.color_palette = Canvas(self.color_palette_frame, bg='white', width=527, height=37)
        self.color_palette.pack()
        self.color_palette.create_rectangle((5, 5, 35, 35), fill=COLORS[0], tags=('color_palette', 'color_'+str(COLORS[0]), 'selected_color')) # by default, black is the selected color
        for i in range(1,len(COLORS)):
            color = COLORS[i]
            self.color_palette.create_rectangle((5+(35*i), 5, 35+(35*i), 35), fill=color, tags=('color_palette', 'color_'+str(color)))
        self.color_palette.itemconfigure('color_palette', width=5, outline='white') # all items in the palette canvas with the tag 'palette' will be modified, that is, the width on the outline, to emulate the selected effect
        self.color_palette.itemconfigure('color_white', width=1, outline='black')
        self.color_palette.itemconfigure('selected_color', outline='lightgray')

    def init_thickness_palette(self):
        self.thickness_palette_frame = Frame(self)
        self.thickness_palette_frame.place(x=WIN_WIDTH*0.636, y=WIN_HEIGHT*0.03)
        self.thickness_palette = Canvas(self.thickness_palette_frame, bg='white', width=140, height=37)
        self.thickness_palette.pack()
        x0=15; y0=17; x1=20; y1=22
        self.thickness_palette.create_oval((x0, y0, x1, y1), fill='black', tags=('thickness_palette', 'thickness_'+str(5), 'selected_thickness')) # thickness 5, also the selected one by default
        for i in range(1, len(THICKNESS)):
            thickness = THICKNESS[i]
            x0+=15+thickness; y0-=2; x1+=20+thickness; y1+=3
            self.thickness_palette.create_oval((x0, y0, x1, y1), fill='black', tags=('thickness_palette', 'thickness_'+str(thickness)))
        self.thickness_palette.itemconfigure('thickness_palette', width=3, outline='black')
        self.thickness_palette.itemconfigure('selected_thickness', outline='gray')

    def init_brush_palette(self):
        self.brush_palette_frame = Frame(self)
        self.brush_palette_frame.place(x=WIN_WIDTH*0.796, y=WIN_HEIGHT*0.03)
        self.brush_palette = Canvas(self.brush_palette_frame, bg='white', width=120, height=37)
        self.brush_palette.pack()
        self.brush_palette.create_line((5, 5, 35, 35), fill='black', tags=('brush_palette', 'brush_'+str(BRUSHES[0]), 'selected_brush'))
        self.brush_palette.create_rectangle((45, 7, 75, 35), fill='black', tags=('brush_palette', 'brush_'+str(BRUSHES[1])))
        self.brush_palette.create_oval((85, 5, 115, 35), fill='black', tags=('brush_palette', 'brush_'+str(BRUSHES[2])))
        #points = [120, 5, 140, 25, 150, 20]
        #self.brush_palette.create_polygon(points, fill='black', tags=('brush_palette', 'brush_'+str(BRUSHES[3])))
        self.brush_palette.itemconfigure('brush_palette', fill='black', width=2)
        self.brush_palette.itemconfigure('selected_brush', fill='gray', width=2)

    def bind_keys(self):
        # controls on the canvas
        self.canvas.bind('<Button-1>', self.get_mouse_pos)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<B1-ButtonRelease>', self.release_stroke)
        self.canvas.bind('<Button-3>', self.undo)
        # controls color, thickness and brushes palette
        for i in range(len(COLORS)):
            self.color_palette.tag_bind(i+1, "<Button-1>", lambda x, i=i: self.set_color(COLORS[i])) # when we click on a color, we we change the stroke color, tag id start at 1, not 0, that's why 1st arg is i+1
        for i in range(len(THICKNESS)):
            self.thickness_palette.tag_bind(i+1, "<Button-1>", lambda x, i=i: self.set_thickness(THICKNESS[i]))
        for i in range(len(BRUSHES)):
            self.brush_palette.tag_bind(i+1, "<Button-1>", lambda x, i=i: self.set_brush(BRUSHES[i]))


    def get_mouse_pos(self, event):
        self.lastx, self.lasty = event.x, event.y

    def draw(self, event):
        match self.brush:
            case 'line': 
                self.canvas.create_line(self.lastx, self.lasty, event.x, event.y, fill=self.color, width=self.thickness, tags='current_stroke')
            case 'rectangle':
                self.canvas.create_rectangle(self.lastx, self.lasty, event.x, event.y, fill=self.color, outline=self.color, width=self.thickness, tags='current_stroke')
            case 'oval':
                self.canvas.create_oval(self.lastx, self.lasty, min(self.lastx+10,event.x), min(self.lasty+10,event.y), fill=self.color, outline=self.color, width=self.thickness, tags='current_stroke')
            case 'shape':
                points = [self.lastx+50, self.lasty+84, self.lastx+20, self.lasty+20, self.lastx-30, self.lasty-30, self.lastx+60, self.lasty+60]
                self.canvas.create_polygon(points, fill=self.color, outline=self.color, width=self.thickness, tags='current_stroke')
        self.lastx, self.lasty = event.x, event.y
        
    def release_stroke(self, event):
        self.canvas_modified(1)
        # We're doing a rotation where only the STROKE_BUFFER_SIZE last stroke will be remembered
        self.canvas.dtag('previous_stroke_%s'%STROKE_BUFFER_SIZE, 'previous_stroke_%s'%STROKE_BUFFER_SIZE)        # We remove to the prev_10 tagged their own tag, meaning that the 11th stoke won't be remember to be erase, you'll have to erase it manually
        for i in range(STROKE_BUFFER_SIZE, 1, -1):
            self.canvas.addtag('previous_stroke_%s'%str(i), 'withtag', 'previous_stroke_%s'%str(i-1))   # add to 'prev_9' tagged the 'prev_10' tag
            self.canvas.dtag('previous_stroke_%s'%str(i), 'previous_stroke_%s'%str(i-1))                # then remove to 'prev_10' tagged the 'prev_9' tag
        self.canvas.addtag('previous_stroke_1', 'withtag', 'current_stroke')                            # add to 'current' tagged the 'prev_1' tag
        self.canvas.dtag('previous_stroke_1', 'current_stroke')                                         # then remove to 'current' tagged the 'prev_1' tag
        
    def undo(self, event):
        self.canvas_modified(1)
        self.canvas.delete('previous_stroke_1')
        for i in range(1, STROKE_BUFFER_SIZE):
            self.canvas.addtag('previous_stroke_%s'%str(i), 'withtag', 'previous_stroke_%s'%str(i+1)) # add to 'prev_4' tagged the 'prev_5' tag
            self.canvas.dtag('previous_stroke_%s'%str(i), 'previous_stroke_%s'%str(i+1))

    def canvas_modified(self, state):
        self.modified = state
        if state:
            self.title("*%s - Paint"%self.image_title)
        else:
            self.title("%s - Paint"%self.image_title)


    def set_color(self, color):
        self.color = color
        self.color_palette.dtag('selected_color', 'selected_color') # delete the 'selected' tag in every item having the 'selected' tag
        self.color_palette.addtag('selected_color', 'withtag', 'color_%s' % self.color) # add to item with the 'palette%s' tag, the tag 'selected'
        self.color_palette.itemconfigure('color_palette', outline='white')
        self.color_palette.itemconfigure('color_white', width=1, outline='black')
        self.color_palette.itemconfigure('selected_color', width=5, outline='lightgray')
        
    def set_thickness(self, thickness):
        self.thickness = thickness
        self.thickness_palette.dtag('selected_thickness', 'selected_thickness') # delete the 'selected' tag in every item having the 'selected' tag
        self.thickness_palette.addtag('selected_thickness', 'withtag', 'thickness_%s' % str(self.thickness)) # add to item with the 'palette%s' tag, the tag 'selected'
        self.thickness_palette.itemconfigure('thickness_palette', outline='black')
        self.thickness_palette.itemconfigure('selected_thickness', width=2, outline='gray')

    def set_brush(self, brush): 
        self.brush = brush
        self.brush_palette.dtag('selected_brush', 'selected_brush') # delete the 'selected' tag in every item having the 'selected' tag
        self.brush_palette.addtag('selected_brush', 'withtag', 'brush_%s' % str(self.brush)) # add to item with the 'palette%s' tag, the tag 'selected'
        self.brush_palette.itemconfigure('brush_palette', fill='black', width=2)
        self.brush_palette.itemconfigure('selected_brush', fill='gray', width=2)


    def clear_canvas(self):
        if messagebox.askokcancel('Clear canvas',"Are you sure you want to clear ?"):
            self.canvas.delete('all')
            self.image_title = 'Untitled'
            self.image_path = None
            self.canvas_modified(0)

    def save_image(self):
        if (self.image_path != None):
            self.attributes('-fullscreen', True)
            self.after(250, self.update())
            x0 = self.winfo_rootx() + self.canvas.winfo_rootx() + 10
            y0 = self.winfo_rooty() + self.canvas.winfo_rooty() + 1
            x1 = x0 + self.canvas.winfo_width() + self.canvas.winfo_rootx() + 158
            y1 = y0 + self.canvas.winfo_height() + self.canvas.winfo_rooty() + 65
            image = ImageGrab.grab(bbox=(x0,y0,x1,y1))
            image.save(self.image_path.split('/')[-1])
            self.canvas_modified(0)
            self.attributes('-fullscreen', False)
        else:
            self.save_image_as()

    def save_image_as(self):
        self.attributes('-fullscreen', True)
        self.update()
        path = filedialog.asksaveasfile(defaultextension=".png", filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")])
        if path:
            x0 = self.winfo_rootx() + self.canvas.winfo_rootx() + 10
            y0 = self.winfo_rooty() + self.canvas.winfo_rooty() + 1
            x1 = x0 + self.canvas.winfo_width() + self.canvas.winfo_rootx() + 158
            y1 = y0 + self.canvas.winfo_height() + self.canvas.winfo_rooty() + 65
            image = ImageGrab.grab(bbox=(x0,y0,x1,y1))
            self.image_path = path.name
            self.image_title = self.image_path.split('/')[-1]
            image.save(self.image_path)
            self.canvas_modified(0)
        self.attributes('-fullscreen', False)
        
    def open_image(self):
        path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")])
        if path:
            self.image = ImageTk.PhotoImage(Image.open(path).resize((CANVAS_WIDTH+4,CANVAS_HEIGHT+4), Image.LANCZOS))
            self.canvas.create_image(0, 0, anchor='nw', image=self.image)
            self.image_path = path
            self.image_title = self.image_path.split('/')[-1] # Get only the name of the file and not the full path
            self.canvas_modified(0)

    def quit_app(self):
        if self.modified:
            if messagebox.askokcancel("Quit", "Close the app without saving ?"):
                self.destroy()
        else:
            self.destroy()


def main():
    app = Paint()
    app.title("Untitled - Paint")
    app.geometry(str(WIN_WIDTH) + 'x' + str(WIN_HEIGHT))
    icon = ImageTk.PhotoImage(Image.open("res/paint_icon.ico"))
    app.iconphoto(False, icon)
    app.protocol("WM_DELETE_WINDOW", app.quit_app)
    app.mainloop()
