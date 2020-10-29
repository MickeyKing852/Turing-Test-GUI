import tkinter as tk
from PIL import Image
import json,os

p1 = None
p2 = None
selected_area = None
question = ''
data = {}
data['result'] = []

def summit():
    global p1, p2, img_name

    data['result'].append({
        'Image-name:':str(img_name)+' ',
        'vertex-1: ': str(p1)+' ',
        'vertex-2:': str(p2)
    })
    with open('/root/Documents/Github/Turing-Test-GUI/Turing-Test-GUI/Test-Result.json', 'w') as outfile:
        json.dump(data,outfile)
    outfile.close()

    Test_area.delete(selection)
    #test_img = tk.PhotoImage(file=''+img_path)
    #Test_area.create_image(1, 1, anchor=tk.NW, image=test_img)

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
    global selected_area

    p2 = event.x,event.y
    if p1  != None:
        if p2 != None:
            if selected_area != None:
                Test_area.delete(selected_area)
            selected_area = Test_area.create_rectangle(p1, p2,outline='red', width = 3)


Image.open('/root/Pictures/Turing_Test/gura_test_image.jpg').save('/root/Pictures/Turing_Test/gura_test_image.png')
im = Image.open('/root/Pictures/Turing_Test/gura_test_image.png')
width, height = im.size
img_name = im.filename

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

ok_button = tk.Button(root, text='OK', command = summit)
ok_button.pack(side = tk.RIGHT, anchor = tk.W)

root.mainloop()
