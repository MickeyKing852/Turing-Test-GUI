import tkinter as tk
from PIL import Image

p1 = None
p2 = None
selection = None
question = ''


def mouse_R_click(event):
    global selection

    if selection != None:
        Test_area.delete(selection)

def mouse_L_click(event):
    global p1
    p1 = event.x,event.y

def mouse_move(event):
    global p1
    global p2
    global selection

    p2 = event.x,event.y
    if p1  != None:
        if p2 != None:
            if selection != None:
                Test_area.delete(selection)
            selection = Test_area.create_rectangle(p1, p2,outline='red', width = 3)


Image.open('/root/Pictures/Turing_Test/gura_test_image.jpg').save('/root/Pictures/Turing_Test/gura_test_image.png')
im = Image.open('/root/Pictures/Turing_Test/gura_test_image.png')
width, height = im.size

root = tk.Tk()
root.title('Turing Test GUI')
root.geometry(  str(width+30)+'x'+str(height+50))

question = 'I am question'
title = tk.Label(root, text = ''+question)
title.pack(side = tk.TOP)

Test_area = tk.Canvas(root, width = width, height = height)
Test_area.bind("<Button-1>", mouse_L_click)
Test_area.bind('<B1-Motion>', mouse_move)
Test_area.bind('<Button-3>', mouse_R_click)
Test_area.pack(side = tk.TOP, anchor = tk.CENTER)

test_img = tk.PhotoImage(file = '/root/Pictures/Turing_Test/gura_test_image.png')
Test_area.create_image(1, 1, anchor= tk.NW, image=test_img)

ok_button = tk.Button(root, text='OK')
ok_button.pack(side = tk.RIGHT, anchor = tk.W)

root.mainloop()
