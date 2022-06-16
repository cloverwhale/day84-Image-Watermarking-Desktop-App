from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import colorchooser
from tkinter.ttk import Combobox

from PIL import ImageTk, Image, ImageFont, ImageDraw

# Image types for file dialogs
img_types = (("jpg files", "*.jpg"), ("png files", "*.png"))
# Watermark transparent setting
alpha = [50]
# Default watermark start position
start_position = (100, 100)
# Keep ImageTk.PhotoImage for canvas widget
images = []
# PIL image objects
img_origin = None
img_watermark = None
# Font style and color default setting
bold = -1
italic = -1
hex_color = "#FFF"
rgb_color = (255, 255, 255)
# Keep mouse position
lastx, lasty = 0, 0


def toggle_bold(event):
    global bold
    bold = bold * -1
    if bold > 0:
        lb_bold.config(fg="#635666", bg="#AEDBCE")
    else:
        lb_bold.config(bg="#CCC", fg="#999")


def toggle_italic(event):
    global italic
    italic = italic * -1
    if italic > 0:
        lb_italic.config(fg="#635666", bg="#AEDBCE")
    else:
        lb_italic.config(bg="#CCC", fg="#999")


def set_font_color(event):
    global hex_color
    global rgb_color
    color = colorchooser.askcolor(color="#FFF")
    rgb_color = color[0]
    hex_color = color[1]
    lb_color.config(bg=hex_color)


def lb_display_size(val):
    lb_size.config(text=val)


def get_watermark_setting():
    global bold
    global italic
    global rgb_color
    font_size = int(lb_size.cget("text"))
    font_name = com_font.get()
    font_family = f"{font_name}.ttf"
    if bold > 0 and italic > 0:
        font_family = f"{font_name} Bold Italic.ttf"
    elif bold > 0:
        font_family = f"{font_name} Bold.ttf"
    elif italic > 0:
        font_family = f"{font_name} Italic.ttf"
    font_color = rgb_color + tuple(alpha)
    watermark_text = txt_watermark.get()
    return font_family, font_size, font_color, watermark_text


def xy(event):
    global lastx, lasty
    lastx, lasty = canvas.canvasx(event.x), canvas.canvasy(event.y)


def open_file():
    global images
    global img_origin

    # clear existing contents
    if images is not None:
        canvas.delete("origin")
        canvas.delete("watermark")
        images = []
        # reset button status
        btn_stamp.config(state="active")

    root.filename = filedialog.askopenfilename(initialdir="./", title="Open an image", filetypes=img_types)
    if root.filename != "":
        img_origin = Image.open(root.filename).convert("RGBA")
        images.append(ImageTk.PhotoImage(img_origin))
        canvas.create_image(0, 0, image=images[0], anchor='nw', tags="origin")
        canvas.config(scrollregion=(0, 0, images[0].width(), images[0].height()))
        canvas.bind('<Button-1>', xy)
        canvas.bind("<B1-Motion>", move_watermark)
        canvas.bind("<Double-Button-1>", delete_watermark)
        btn_save.config(state="active")


def save_file():
    global img_origin
    global img_watermark

    root.filename = filedialog.asksaveasfilename(initialdir="./", title="Save file", filetypes=img_types)

    # real image to save
    if root.filename != "":
        canvas_position = canvas.coords("watermark")
        img_watermark = Image.new("RGBA", img_origin.size)
        img_text = ImageDraw.Draw(img_watermark)
        watermark_text = get_watermark_setting()
        font_family_and_size = ImageFont.truetype(font=watermark_text[0], size=watermark_text[1])
        img_text.text((start_position[0] + canvas_position[0], start_position[1] + canvas_position[1]),
                      text=watermark_text[3], fill=watermark_text[2], font=font_family_and_size)
        final = Image.alpha_composite(img_origin, img_watermark)
        final.convert("RGB").save(root.filename)
        messagebox.showinfo(message="Image is saved.")


def create_watermark():
    global images
    global img_watermark

    if img_origin is not None:
        img_watermark = Image.new("RGBA", img_origin.size)
        img_text = ImageDraw.Draw(img_watermark)
        watermark_text = get_watermark_setting()
        font_family_and_size = ImageFont.truetype(font=watermark_text[0], size=watermark_text[1])
        img_text.text(start_position, text=watermark_text[3], font=font_family_and_size, fill=watermark_text[2])
        images.append(ImageTk.PhotoImage(img_watermark))
        canvas.create_image(0, 0, image=images[1], anchor='nw', tags="watermark")
    if canvas.find_withtag("watermark"):
        btn_stamp.config(state="disabled")


def move_watermark(event):
    global lastx, lasty
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    canvas.move("watermark", x - lastx, y - lasty)
    lastx, lasty = x, y


def delete_watermark(event):
    if len(images) == 2:
        canvas.delete("watermark")
        images.pop(1)
        btn_stamp.config(state="active")


# UI set up ---------------------------------------------------------------- #
root = Tk()
root.geometry("720x600")
root.title("Add Watermark")

frame_1 = Frame(root)
frame_1.grid(row=0, column=0, columnspan=2, sticky="nw", padx=10, pady=10)
btn_open = Button(frame_1, text="Open...",
                  padx=2, pady=2, border=0, highlightthickness=0,
                  command=open_file)
btn_open.grid(row=0, column=0, sticky="ew")
btn_save = Button(frame_1, text="Save", state="disabled",
                  padx=2, pady=2, border=0, highlightthickness=0,
                  command=save_file)
btn_save.grid(row=1, column=0, sticky="ew", pady=5)

frame_2 = Frame(root)
frame_2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

frame_2a = Frame(frame_2)
frame_2a.grid(row=0, column=0)

txt_watermark = Entry(frame_2a, fg="#5E454B", bg="#F3F0D7")
txt_watermark.grid(row=0, column=0, sticky="nw", padx=5)
txt_watermark.insert(0, "Enter watermark text here")

size_var = StringVar()
sc_size = Scale(frame_2a, orient=HORIZONTAL, length=200, from_=12, to=250, variable=size_var, showvalue=False,
                command=lb_display_size)
sc_size.grid(row=0, column=1, sticky="w", padx=2)
lb_size = Label(frame_2a, textvariable=size_var, width=3, anchor="w")
lb_size.grid(row=0, column=2, sticky="w", padx=2)

frame_2b = Frame(frame_2)
frame_2b.grid(row=1, column=0, sticky="ew")

font_var = StringVar()
com_font = Combobox(frame_2b, textvariable=font_var, width=15)
com_font.grid(row=0, column=0, sticky="nw", padx=5)
com_font['values'] = ('Arial', 'Courier New', 'Georgia', 'Trebuchet MS', 'Verdana')
com_font.current(0)

lb_bold = Label(frame_2b, text="B", padx=1, pady=1, width=2, height=1, fg="#999", bg="#CCC")
lb_bold.grid(row=0, column=1, padx=5)
lb_bold.bind('<Button-1>', toggle_bold)

lb_italic = Label(frame_2b, text="I", padx=1, pady=1, width=2, height=1, fg="#999", bg="#CCC")
lb_italic.grid(row=0, column=2, padx=5)
lb_italic.bind('<Button-1>', toggle_italic)

lb_color = Label(frame_2b, text="Color", padx=2, pady=1, height=1, fg="#000", bg="#FFF")
lb_color.grid(row=0, column=3, padx=5)
lb_color.bind('<Button-1>', set_font_color)

frame_3 = Frame(root)
frame_3.grid(row=0, column=2, padx=10, pady=10)

btn_stamp = Button(frame_3, text="Add watermark",
                   padx=2, pady=2, border=0, highlightthickness=0,
                   command=create_watermark)
btn_stamp.grid(row=1, column=0, sticky="s")

canvas = Canvas(root, scrollregion=(0, 0, 600, 480), width=640, height=480)
h = Scrollbar(root, orient=HORIZONTAL, command=canvas.xview)
v = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
canvas.config(yscrollcommand=v.set, xscrollcommand=h.set)
canvas.grid(row=2, column=0, columnspan=3, sticky="nwe")
h.grid(row=3, column=0, columnspan=3, sticky="we")
v.grid(row=2, column=3, sticky="ns")

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.mainloop()
