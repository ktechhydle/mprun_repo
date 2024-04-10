from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main import *
from PIL import Image, ImageTk
from customtkinter import *
import tkinter as tk
import webbrowser
import sys

class Dialog(CTk):
    def __init__(self):
        super().__init__()

        self.title('MPRUN - Main Window')
        self.geometry("1080x600+100+75")
        self.resizable(False, False)
        self.iconbitmap('logos and icons/MPRUN_icon.ico')

        self.create_ui()

    def create_ui(self):
        # Fonts
        web_link_font = CTkFont(family="Arial", size=10, weight="bold", underline=True)

        # App image and label
        iog = Image.open('logos and icons/MPRUN_icon.png')
        ir = iog.resize((80, 76))
        image = ImageTk.PhotoImage(ir)
        mprun_img_label = CTkLabel(self, image=image, text='')
        mprun_img_label.image = image
        mprun_img_label.place(x=20, y=20)

        # Welcome label
        welcome_label = CTkLabel(self, text='MPRUN Community Edition', font=('Arial', 20), text_color='lightgray')
        welcome_label.place(x=110, y=50)

        # Copyright label
        copyright_label = CTkLabel(self, text='Copyright © K-TECH Industries 2024, All Rights Reserved.', font=('Arial', 10), text_color='lightgray')
        copyright_label.place(x=110, y=80)

        # Labels with links
        link1 = CTkLabel(self, text="Read the acknowledgements", font=web_link_font, cursor="hand2")
        link1.place(x=368, y=79)
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

        template_img_7 = Image.open('logos and icons/create_custom_icon.png').resize((115, 150))
        template_img_7n = ImageTk.PhotoImage(template_img_7)
        custom_size_btn = CTkButton(frame2, text='Create a Custom Template',
                                    image=template_img_7n,
                                    compound='top',
                                    text_color='white',
                                    fg_color='#2B2B2B',
                                    hover_color='#3d3d3d',
                                    command=self.open_create_template_dialog)

        # Add widgets
        custom_size_btn.pack(pady=5, side='left')
        letter_size_btn.pack(pady=5, side='left')
        post_card_size_btn.pack(pady=5, side='left')
        phone_size_btn.pack(pady=5, side='left')
        tablet_size_btn.pack(pady=5, side='left')
        letter_sizeD_btn.pack(pady=5, side='left')
        post_card_sizeD_btn.pack(pady=5, side='left')
        
        
    def launch_project(self):
        self.app = MPRUN()
        self.app.show()
        self.set_attr()

    def set_attr(self):
        selected_template = self.template_combo.get()
        selected_value = self.values[selected_template]
        self.app.set_template(selected_value)

    def open_link(self, url):
        webbrowser.open_new(url)

    def open_create_template_dialog(self):
        a = CreateTemplateDialog()
        a.mainloop()

class CreateTemplateDialog(CTk):
    def __init__(self):
        super().__init__()

        self.title('Create Template')
        self.iconbitmap('logos and icons/MPRUN_icon.ico')
        self.geometry('220x500+200+200')
        self.resizable(False, False)

        self.checks = tk.IntVar(value=0)

        self.create_ui()

    def create_ui(self):
        # Labels
        welcome_label = CTkLabel(self, text='Template Attributes', font=('Arial', 20))
        width_label = CTkLabel(self, text='Width')
        height_label = CTkLabel(self, text='Height')

        # Checkboxes
        self.check1 = CTkCheckBox(self, checkbox_width=15, checkbox_height=15, text='', textvariable=self.checks)

        # Entries
        self.x_size_entry = CTkEntry(self, placeholder_text='X width (in px)', width=200)
        self.y_size_entry = CTkEntry(self, placeholder_text='Y width (in px)', width=200)
        self.default_text_entry = CTkTextbox(self, width=180, height=50)

        create_project_btn = CTkButton(self, text='Create Project', text_color='white', fg_color='#525252', hover_color='gray', command=self.create_project)

        # Place widgets
        welcome_label.place(x=10, y=5)
        width_label.place(x=10, y=40)
        self.x_size_entry.place(x=10, y=65)
        height_label.place(x=10, y=100)
        self.y_size_entry.place(x=10, y=125)
        self.check1.place(x=10, y=170)
        self.default_text_entry.place(x=30, y=170)

        create_project_btn.place(x=10, y=235)

        # Insert default values
        self.x_size_entry.insert('end', '1920')
        self.y_size_entry.insert('end', '1080')
        self.default_text_entry.insert('0.0', 'This is an Editable Text Block that will be placed on the canvas during creation')

    def create_project(self):
        self.app = MPRUN()
        self.app.show()
        self.set_attr()
        self.destroy()

    def set_attr(self):
        if self.check1.get() == 1:
            self.app.custom_template(int(self.x_size_entry.get()), int(self.y_size_entry.get()), self.default_text_entry.get('0.0', 'end-1c'), 10)

        else:
            self.app.custom_template(int(self.x_size_entry.get()), int(self.y_size_entry.get()), '', 10)


if __name__ == '__main__':
    win = QApplication([])
    app = Dialog()
    app.mainloop()
    sys.exit(win.exec_())
