import tkinter as tk
from PIL import Image
import csv, os, traceback

TOP_L_X: int = 0
TOP_L_Y: int = 0
BOT_R_X: int = 0
BOT_R_Y: int = 0

SELECTED_AREA = {}
SELECTED_AREA['rectangle'] = []

INFO = {}
INFO['img_info'] = []
INFO['result'] = []

QUESTION: str = ''
TEST_IMG: object = ''

WIDTH: int = 842
HEIGHT: int = 595
COUNTER: int = 0


def image_file_load() -> None:
    global WIDTH, HEIGHT

    default_path = '/root/Pictures/Turing_Test/'
    convert_need_formmat = ['.jpg', 'tif', 'tiff', '.bmp', '.jpeg', '.gif']
    try:
        while True:
            for r, d, f in os.walk(default_path):

                for file in f:
                    for extension in convert_need_formmat:
                        if extension in file.lower():
                            im = Image.open(default_path + file)
                            im.save(default_path + file.lower().replace(extension, '.png'))
                            os.remove(default_path + file)

            for r, d, f in os.walk(default_path):
                for file in f:
                    if '.png' in file:
                        im = Image.open(default_path + file)
                        width, height = im.size

                    if (width, height) != (WIDTH, HEIGHT):
                        im = im.resize((WIDTH, HEIGHT))
                        os.system('rm ' + default_path + file)
                        im.save(default_path + file)
                    INFO['img_info'].append({
                        'path': default_path + file,
                        'image name': file
                    })
            yield None
    except Exception as e:
        alert = tk.Tk()
        alert.title('Error!!!')
        alert.geometry('800x200')
        formatted_lines = traceback.format_exc().splitlines()
        error_label = tk.Label(alert,
                               text=f'  {formatted_lines[-1]}: {e}\n{formatted_lines[1]}\n{formatted_lines[2]}').pack()
        exit_b = tk.Button(alert, text='close', command=lambda: alert.destroy()).pack(side=tk.BOTTOM)
        alert.mainloop()


def convas_setup() -> None:
    global TEST_IMG, INFO, COUNTER
    next(img_load)
    TEST_IMG = tk.PhotoImage(file=INFO['img_info'][COUNTER]['path'])
    COUNTER += 1


def submit() -> None:
    global TEST_IMG
    try:
        default_path = '/root/Documents/Github/Turing-Test-GUI/Test-Result.csv'
        fieldnames = ['image-name', 'rectengle id', 'Top-left-x', 'Top-left-y', 'Bottom-right-x', 'Bottom-right-y']
        if os.path.exists(default_path):
            out_file = open(default_path, 'r')
            in_file = open(default_path, 'a')
            reader = csv.DictReader(out_file, fieldnames)
            writer = csv.DictWriter(in_file, fieldnames)

            for row in reader:
                if row['image-name'] is not str(INFO['img_info'][COUNTER - 1]['image name']):
                    for i in INFO['result']:
                        i = str(i).split(',')
                        writer.writerow(
                            {'image-name': i[0], 'rectengle id': i[1], 'Top-left-x': i[2], 'Top-left-y': i[3],
                             'Bottom-right-x': i[4], 'Bottom-right-y': i[5]})
                    else:
                        raise RuntimeError

            in_file.close()
            out_file.close()
        else:
            in_file = open(default_path, 'w')
            wirter = csv.DictWriter(in_file, fieldnames)
            for i in INFO['result']:
                i = i.split(',')
                wirter.writerow(
                    {'image-name': i[0], 'rectengle id': i[1], 'Top-left-x': i[2], 'Top-left-y': i[3],
                     'Bottom-right-x': i[4], 'Bottom-right-y': i[5]})
            in_file.close()

        for i in SELECTED_AREA['rectangle']:
            test_area.delete(i)
        convas_setup()
        test_area.itemconfig(image, image=TEST_IMG)


    except IndexError:
        popup = tk.Tk()
        popup.title('Test Finish')
        label = tk.Label(popup, text='You finished the Turing Test').pack(side=tk.TOP, anchor=tk.CENTER)
        close_b = tk.Button(popup, text='Exit', command=lambda: popup.destroy()).pack(side=tk.BOTTOM, anchor=tk.CENTER)

        root.destroy()
        popup.mainloop()

    except RuntimeError:
        for i in SELECTED_AREA['rectangle']:
            test_area.delete(i)
        convas_setup()
        test_area.itemconfig(image, image=TEST_IMG)

    except Exception as e:
        alert = tk.Tk()
        alert.title('Error!!!')
        alert.geometry('800x200')
        formatted_lines = traceback.format_exc().splitlines()
        error_label = tk.Label(alert, text=f'  {formatted_lines[-1]}:\n{e}\n{formatted_lines[1]}\n{formatted_lines[2]}').pack()
        exit_b = tk.Button(alert, text='close', command=lambda: alert.destroy()).pack(side=tk.BOTTOM)
        alert.mainloop()


def reset_canvas() -> None:
    global SELECTED_AREA

    while True:
        counter = len(SELECTED_AREA['rectangle'])
        if counter < 1:
            pass
        else:
            test_area.delete(SELECTED_AREA['rectangle'][counter - 1])
            SELECTED_AREA['rectangle'].remove(SELECTED_AREA['rectangle'][counter - 1])
            INFO['img_info'].remove(INFO['img_info'][counter - 1])

        yield None


def get_top_left_coordinate(x: int, y: int) -> None:
    global TOP_L_X, TOP_L_Y

    while True:
        TOP_L_X = x
        TOP_L_Y = y
        SELECTED_AREA['rectangle'].append(
            test_area.create_rectangle(TOP_L_X, TOP_L_Y, TOP_L_X, TOP_L_Y, outline='red', width=3))
        yield None


def sub_get_top_left_coordinate(event) -> None:
    run = get_top_left_coordinate(event.x, event.y)
    next(run)


def get_bottom_right_coordinate(event) -> None:
    global TOP_L_Y, TOP_L_X, BOT_R_X, BOT_R_Y

    counter = len(SELECTED_AREA['rectangle'])
    BOT_R_X, BOT_R_Y = event.x, event.y

    test_area.coords(SELECTED_AREA['rectangle'][counter - 1], BOT_R_X, BOT_R_Y, TOP_L_X, TOP_L_Y)


def sub_get_bottom_right_coordinate(event) -> None:
    counter = len(SELECTED_AREA['rectangle'])
    INFO['result'].append(
        f"{INFO['img_info'][COUNTER - 1]['image name']},R{counter - 1},{TOP_L_X},{TOP_L_Y},{BOT_R_X},{BOT_R_Y}")


root = tk.Tk()
root.title('Turing Test GUI')
window_size: tuple = (WIDTH + 30, HEIGHT + 50)
root.geometry(str(WIDTH + 30) + 'x' + str(HEIGHT + 50))

QUESTION = 'I am question'
title = tk.Label(root, text=QUESTION)
title.pack(side=tk.TOP)

test_area = tk.Canvas(root, width=WIDTH, height=HEIGHT)
test_area.bind("<Button-1>", sub_get_top_left_coordinate)
test_area.bind('<B1-Motion>', get_bottom_right_coordinate)
test_area.bind('<ButtonRelease-1>', sub_get_bottom_right_coordinate)
reset = reset_canvas()
test_area.bind('<Button-3>', lambda value: next(reset))
test_area.pack(side=tk.TOP, anchor=tk.CENTER)
img_load = image_file_load()
convas_setup()
image = test_area.create_image(1, 1, anchor=tk.NW, image=TEST_IMG)
ok_button = tk.Button(root, text='OK', command=submit)
ok_button.pack(side=tk.RIGHT, anchor=tk.W)

root.mainloop()
