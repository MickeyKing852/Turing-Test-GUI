import tkinter as tk
from PIL import Image
import json, os

p1 = None
p2 = None
selected_area = None
question = ''
test_img = ''
width, height = 842, 595
counter = 0
data = {}
data['result'] = []
data['img_info'] = []

def image_file_load():
    global width, height, img_files, data

    default_path = '/root/Pictures/Turing_Test/'
    unavaiable_fomat = ['.jpg', 'tif', 'tiff', '.bmp', '.jpeg', '.gif']

    for r, d, f in os.walk(default_path):
        for file in f:
            for extension in unavaiable_fomat:
                if extension in file.lower():
                    im = Image.open(default_path + file)
                    im.save(default_path + file.lower().replace(extension, '.png'))
                    os.system('rm ' + default_path + file)

    for r, d, f in os.walk(default_path):
        for file in f:
            if '.png' in file:
                im = Image.open(default_path + file)
                width, height = im.size

                if (width, height) != (842, 595):
                    im = im.resize((842, 595))
                    os.system('rm ' + default_path + file)
                    im.save(default_path + file)
                data['img_info'].append({
                    'path': default_path + file,
                    'image name': file
                })

def convas_setup():
    global test_img, data, counter
    test_img = tk.PhotoImage(file=data['img_info'][counter]['path'])
    counter += 1

def summit():
    global p1, p2, data, counter
    try:
        data['result'].append({
            'Image-name:': str(data['img_info'][counter]['image name']) + ' ',
            'vertex-1: ': str(p1) + ' ',
            'vertex-2:': str(p2)
        })

        with open('/root/Documents/Github/Turing-Test-GUI/Turing-Test-GUI/Test-Result.json', 'w') as outfile:
            json.dump(data['result'], outfile)
        outfile.close()

        Test_area.delete(selected_area)
        convas_setup()
        Test_area.itemconfig(image, image = test_img)

    except IndexError:

        popup = tk.Tk()
        popup.title('Test Finish')
        label = tk.Label(popup, text='You finished the Turing Test').pack(side=tk.TOP, anchor=tk.CENTER)
        close_b = tk.Button(popup, text='Exit', command=lambda: popup.destroy()).pack(side=tk.BOTTOM, anchor=tk.CENTER)
        #root.destroy()
        popup.mainloop()

def mouse_R_click(event):
    global selected_area
    if selected_area != None:
        Test_area.delete(selected_area)

def mouse_L_click(event):
    global p1
    p1 = event.x, event.y

def mouse_move(event):
    global p1
    global p2
    global selected_area

    p2 = event.x, event.y
    if p1 != None:
        if p2 != None:
            if selected_area != None:
                Test_area.delete(selected_area)
            selected_area = Test_area.create_rectangle(p1, p2, outline='red', width=3)

root = tk.Tk()
root.title('Turing Test GUI')
root.geometry(str(width + 30) + 'x' + str(height + 50))

question = 'I am question'
title = tk.Label(root, text='' + question)
title.pack(side=tk.TOP)

Test_area = tk.Canvas(root, width=width, height=height)
Test_area.bind("<Button-1>", mouse_L_click)
Test_area.bind('<B1-Motion>', mouse_move)
Test_area.bind('<Button-3>', mouse_R_click)
Test_area.pack(side=tk.TOP, anchor=tk.CENTER)

image_file_load()
convas_setup()
image = Test_area.create_image(1, 1, anchor=tk.NW, image=test_img)

ok_button = tk.Button(root, text='OK', command=summit)
ok_button.pack(side=tk.RIGHT, anchor=tk.W)

root.mainloop()
