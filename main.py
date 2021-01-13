import tkinter as tk
from os.path import expanduser

from PIL import Image
import json, os

class Test_GUI():
    def __init__(self):
        self.p1 = None
        self.p2 = None
        self.selected_area = None
        self.home = expanduser("~")
        self.question = ''
        self.test_img = ''
        self.default_width, default_height = 842, 595
        self.counter = 0
        self.data = {}
        self.info = {}
        self.data['result'] = []
        self.data['img_info'] = []

        root = tk.Tk()
        root.title('Turing Test GUI')
        root.geometry(str(self.default_width + 30) + 'x' + str(self.default_height + 50))

        question = 'I am question'
        title = tk.Label(root, text='' + question)
        title.pack(side=tk.TOP)

        Test_area = tk.Canvas(root, width=self.default_width, height=self.default_height)
        Test_area.bind("<Button-1>", self.mouse_L_click)
        Test_area.bind('<B1-Motion>', self.mouse_move)
        Test_area.bind('<Button-3>', self.mouse_R_click)
        Test_area.pack(side=tk.TOP, anchor=tk.CENTER)

        self.image_file_load()
        self.convas_setup()
        image = Test_area.create_image(1, 1, anchor=tk.NW, image=self.test_img)

        ok_button = tk.Button(root, text='OK', command=self.summit)
        ok_button.pack(side=tk.RIGHT, anchor=tk.W)

        root.mainloop()

    def image_file_load(self):

        default_path = f'{self.home}/Pictures/Turing_Test/'
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

                    if (width, height) != (self.default_width, self.default_height):
                        im = im.resize((self.default_width, self.default_height))
                        os.system('rm ' + default_path + file)
                        im.save(default_path + file)
                    self.data['img_info'].append({
                        'path': default_path + file,
                        'image name': file
                    })


    def convas_setup(self):

        self.test_img = tk.PhotoImage(file=self.data['img_info'][self.counter]['path'])
        self.counter += 1


    def summit(self):

        default_path = f'{self.home}/Documents/Turing-Test-GUI/Test-Result.json'

        try:
            self.data['result'].append({
                'Image-name:': str(self.data['img_info'][self.counter]['image name']) + ' ',
                'vertex-1: ': str(self.p1) + ' ',
                'vertex-2:': str(self.p2)
            })

            with open(f'{self.home}/Documents/Turing-Test-GUI/Test-Result.json', 'w') as outfile:
                json.dump(self.data['result'], outfile)
            outfile.close()

            self.Test_area.delete(selected_area)
            self.convas_setup()
            self.Test_area.itemconfig(self.image, image=self.test_img)

        except IndexError:
            popup = tk.Tk()
            popup.title('Test Finish')
            label = tk.Label(popup, text='You finished the Turing Test').pack(side=tk.TOP, anchor=tk.CENTER)
            close_b = tk.Button(popup, text='Exit', command=lambda: popup.destroy()).pack(side=tk.BOTTOM, anchor=tk.CENTER)

            # root.destroy()
            popup.mainloop()


    def mouse_R_click(self,event):
        global selected_area
        if selected_area != None:
            self.Test_area.delete(selected_area)


    def mouse_L_click(self,event):

        self.p1 = event.x, event.y


    def mouse_move(self,event):
        self.p2 = event.x, event.y
        if self.p1 != None:
            if self.p2 != None:
                if self.selected_area != None:
                    self.Test_area.delete(selected_area)
                self.selected_area = self.Test_area.create_rectangle(self.p1, self.p2, outline='red', width=3)

app = Test_GUI()