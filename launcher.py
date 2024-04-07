from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main import *
from PIL import Image, ImageTk
from customtkinter import *
import tkinter as tk
import webbrowser

class Dialog(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('MPRUN - Main Window')
        self.geometry("1080x600+100+75")
        self.resizable(False, False)

        self.create_ui()

    def create_ui(self):
        # Fonts
        web_link_font = CTkFont(family="Arial", size=10, weight="bold", underline=True)

        # App image and label
        iog = Image.open('logos and icons/MPRUN_icon.png')
        ir = iog.resize((80, 76))
        image = ImageTk.PhotoImage(ir)
        mprun_img_label = tk.Label(self, image=image)
        mprun_img_label.image = image
        mprun_img_label.place(x=20, y=20)

        # Welcome label
        welcome_label = tk.Label(self, text='MPRUN Community Edition', font=('Arial', 20), fg='lightgray')
        welcome_label.place(x=110, y=50)

        # Copyright label
        copyright_label = tk.Label(self, text='Copyright © K-TECH Industries 2024, All Rights Reserved.', font=('Arial', 10), fg='lightgray')
        copyright_label.place(x=110, y=80)

        # Labels with links
        link1 = CTkLabel(self, text="Read the acknowledgements", font=web_link_font, cursor="hand2")
        link1.place(x=390, y=75)
        link1.bind("<Button-1>", lambda e: self.open_link("https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit?usp=sharing"))

        # Frame for other widgets
        frame = CTkFrame(self, width=700, height=80)
        frame.place(x=190, y=120)

        # Frame label
        frame_label = CTkLabel(frame, text="Let's create something great...", font=('Helvetica', 20))
        frame_label.place(x=195, y=5)

        # Create new project button
        create_project_btn = CTkButton(frame, text='Create New Project', text_color='white', fg_color='#525252', hover_color='gray', command=self.launch_project)
        create_project_btn.place(x=20, y=40)

        # Template dropdown
        self.values = {'Template 1: Default (1000 x 700, [Medium Quality], 100 PPI)': 1,
                  'Template 2: Paper Size (828 x 621, [Low Quality], 72 PPI)': 2,
                  'Template 3: Detailed-Paper Size (1725 x 1293, [High Quality], 300 PPI)': 3,
                  'Template 4: Phone Size (1080 x 1920, [High Quality], 300 PPI)': 4,
                       'Template 5: Postcard Size (591 x 399, [Low Quality], 96 PPI)': 5,
                       'Template 6: Detailed-Postcard Size (1847 x 1247, [High Quality], 300 PPI)': 6,
                       'Template 7: Tablet Size (1024 × 1366, [Medium Quality], 264 PPI': 7}

        self.template_combo = CTkComboBox(frame, width=500, values=list(self.values.keys()))
        self.template_combo.place(x=180, y=40)

        # Frame 2
        frame2 = CTkScrollableFrame(self, width=690, height=300, orientation='horizontal')
        frame2.place(x=190, y=215)

        # Template select buttons
        template_img_1 = Image.open('logos and icons/letter_size_icon.png').resize((115, 150))
        template_img_1n = ImageTk.PhotoImage(template_img_1)
        letter_size_btn = CTkButton(frame2, text='Letter Size (828 x 621)',
                                  image=template_img_1n,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set('Template 2: Paper Size (828 x 621, [Low Quality], 72 PPI)'))

        template_img_2 = Image.open('logos and icons/detailed_letter_size_icon.png').resize((115, 150))
        template_img_2n = ImageTk.PhotoImage(template_img_2)
        letter_sizeD_btn = CTkButton(frame2, text='Detailed Letter Size (1725 x 1293)',
                                  image=template_img_2n,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set(
                                      'Template 3: Detailed-Paper Size (1725 x 1293, [High Quality], 300 PPI)'))

        template_img_3 = Image.open('logos and icons/phone_icon.png').resize((115, 150))
        template_img_3n = ImageTk.PhotoImage(template_img_3)
        phone_size_btn = CTkButton(frame2, text='Phone Size (1080 x 1920)',
                                  image=template_img_3n,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set(
                                      'Template 4: Phone Size (1080 x 1920, [High Quality], 300 PPI)'))

        template_img_4 = Image.open('logos and icons/post_card_icon.png').resize((115, 150))
        template_img_4n = ImageTk.PhotoImage(template_img_4)
        post_card_size_btn = CTkButton(frame2, text='Post Card Size (591 x 399)',
                                  image=template_img_4n,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set(
                                      'Template 5: Postcard Size (591 x 399, [Low Quality], 96 PPI)'))

        template_img_5 = Image.open('logos and icons/detailed_post_card_icon.png').resize((115, 150))
        template_img_5n = ImageTk.PhotoImage(template_img_5)
        post_card_sizeD_btn = CTkButton(frame2, text='Detailed Post Card Size (1847 x 1247)',
                                  image=template_img_5n,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set(
                                      'Template 6: Detailed-Postcard Size (1847 x 1247, [High Quality], 300 PPI)'))

        template_img_6 = Image.open('logos and icons/ipad_icon.png').resize((115, 150))
        template_img_6n = ImageTk.PhotoImage(template_img_6)
        tablet_size_btn = CTkButton(frame2, text='Tablet Size (1366 x 1024)',
                                        image=template_img_6n,
                                        compound='top',
                                        text_color='white',
                                        fg_color='#2B2B2B',
                                        hover_color='#3d3d3d',
                                        command=lambda: self.template_combo.set(
                                            'Template 7: Tablet Size (1024 × 1366, [Medium Quality], 264 PPI'))

        # Add widgets
        letter_size_btn.pack(pady=5, side='left')
        letter_sizeD_btn.pack(pady=5, side='left')
        post_card_size_btn.pack(pady=5, side='left')
        post_card_sizeD_btn.pack(pady=5, side='left')
        phone_size_btn.pack(pady=5, side='left')
        tablet_size_btn.pack(pady=5, side='left')


    def launch_project(self):
        win = QApplication([])
        self.app = MPRUN()
        self.app.show()
        self.set_attr()
        win.exec_()

    def set_attr(self):
        selected_template = self.template_combo.get()
        selected_value = self.values[selected_template]
        self.app.set_template(selected_value)

    def open_link(self, url):
        webbrowser.open_new(url)


if __name__ == '__main__':
    app = Dialog()
    app.mainloop()