from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from main import *
from PIL import Image, ImageTk
from customtkinter import *
import tkinter as tk
import webbrowser
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def open_create_template_dialog():
    a = CreateTemplateDialog()
    a.mainloop()


def open_link(url):
    webbrowser.open_new(url)


class Dialog(CTk):
    def __init__(self):
        super().__init__()

        self.title('MPRUN - Main Window')
        self.geometry("1080x600+100+75")
        self.resizable(False, False)
        self.iconbitmap(resource_path('logos and icons/MPRUN_icon.ico'))

        self.create_ui()

    def create_ui(self):
        # Fonts
        web_link_font = CTkFont(family="Arial", size=10, weight="bold", underline=True)

        # App image and label
        iog = CTkImage(light_image=Image.open("logos and icons/MPRUN_logo_rounded_corners_version.png"),
                                  dark_image=Image.open("logos and icons/MPRUN_logo_rounded_corners_version.png"),
                                  size=(80, 80))
        mprun_img_label = CTkLabel(self, image=iog, text='')
        mprun_img_label.place(x=20, y=20)

        # Welcome label
        welcome_label = CTkLabel(self, text='MPRUN Community Edition', font=('Arial', 20), text_color='lightgray')
        welcome_label.place(x=110, y=55)

        # Copyright label
        copyright_label = CTkLabel(self, text='Copyright © K-TECH Industries 2024, All Rights Reserved.', font=('Arial', 10), text_color='lightgray')
        copyright_label.place(x=110, y=80)

        # Labels with links
        link1 = CTkLabel(self, text="Read the credits", font=web_link_font, cursor="hand2")
        link1.place(x=368, y=79)
        link1.bind("<Button-1>", lambda e: open_link("https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit?usp=sharing"))

        # Frame for other widgets
        frame = CTkFrame(self, width=700, height=80)
        frame.place(x=190, y=120)

        # Frame label
        frame_label = CTkLabel(frame, text="Let's create something great...", font=('Helvetica', 20))
        frame_label.place(x=195, y=5)

        # Create new project button
        create_project_btn = CTkButton(self,
                                       text='New File',
                                       text_color='white',
                                       fg_color='#1473e6',
                                       hover_color='#0d66d0',
                                       corner_radius=35,
                                       width=100,
                                       height=30,
                                       command=self.launch_project)
        create_project_btn.place(x=20, y=120)

        # Template dropdown
        self.values = {'Template 1: Default (1000 x 700, [Medium Quality])': 1,
                  'Template 2: Paper Size (828 x 621, [Low Quality])': 2,
                  'Template 3: Detailed-Paper Size (1725 x 1293, [High Quality])': 3,
                  'Template 4: Phone Size (1080 x 1920, [High Quality])': 4,
                       'Template 5: Postcard Size (591 x 399, [Low Quality])': 5,
                       'Template 6: Detailed-Postcard Size (1847 x 1247, [High Quality])': 6,
                       'Template 7: Tablet Size (1024 × 1366, [Medium Quality])': 7,
                    'Template 8: Webview size (1920 x 1080, [High Quality])': 8}

        self.template_combo = CTkComboBox(frame, width=500, values=list(self.values.keys()))
        self.template_combo.place(x=180, y=40)

        # Frame 2
        frame2 = CTkScrollableFrame(self, width=690, height=250, orientation='horizontal')
        frame2.place(x=190, y=215)

        # Template select buttons
        template_img_1 = CTkImage(light_image=Image.open("logos and icons/letter_size_icon.png"),
                                  dark_image=Image.open("logos and icons/letter_size_icon.png"),
                                  size=(115, 150))
        letter_size_btn = CTkButton(frame2, text='''Letter 
(828 x 621)''',
                                  image=template_img_1,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set('Template 2: Paper Size (828 x 621, [Low Quality])'))

        template_img_3 = CTkImage(light_image=Image.open("logos and icons/phone_icon.png"),
                                  dark_image=Image.open("logos and icons/phone_icon.png"),
                                  size=(115, 150))
        phone_size_btn = CTkButton(frame2, text='''Phone 
(1080 x 1920)''',
                                  image=template_img_3,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set(
                                      'Template 4: Phone Size (1080 x 1920, [High Quality])'))

        template_img_4 = CTkImage(light_image=Image.open("logos and icons/post_card_icon.png"),
                                  dark_image=Image.open("logos and icons/post_card_icon.png"),
                                  size=(115, 150))
        post_card_size_btn = CTkButton(frame2, text='''Post Card 
(591 x 399)''',
                                  image=template_img_4,
                                  compound='top',
                                  text_color='white',
                                  fg_color='#2B2B2B',
                                  hover_color='#3d3d3d',
                                  command=lambda: self.template_combo.set(
                                      'Template 5: Postcard Size (591 x 399, [Low Quality])'))

        template_img_6 = CTkImage(light_image=Image.open("logos and icons/ipad_icon.png"),
                                  dark_image=Image.open("logos and icons/ipad_icon.png"),
                                  size=(115, 150))
        tablet_size_btn = CTkButton(frame2, text='''Tablet 
(1366 x 1024)''',
                                        image=template_img_6,
                                        compound='top',
                                        text_color='white',
                                        fg_color='#2B2B2B',
                                        hover_color='#3d3d3d',
                                        command=lambda: self.template_combo.set(
                                            'Template 7: Tablet Size (1024 × 1366, [Medium Quality])'))
                                            
        template_img_8 = CTkImage(light_image=Image.open("logos and icons/webview_icon.png"),
                                  dark_image=Image.open("logos and icons/webview_icon.png"),
                                  size=(115, 150))
        webview_size_btn = CTkButton(frame2, text='''Webview 
(1920 x 1080)''',
                                        image=template_img_8,
                                        compound='top',
                                        text_color='white',
                                        fg_color='#2B2B2B',
                                        hover_color='#3d3d3d',
                                        command=lambda: self.template_combo.set(
                                            'Template 8: Webview size (1920 x 1080, [High Quality])'))


        template_img_7 = CTkImage(light_image=Image.open("logos and icons/create_custom_icon.png"),
                                  dark_image=Image.open("logos and icons/create_custom_icon.png"),
                                  size=(115, 150))
        custom_size_btn = CTkButton(frame2, text='''Custom Template
(Width x Height)''',
                                    image=template_img_7,
                                    compound='top',
                                    text_color='white',
                                    fg_color='#2B2B2B',
                                    hover_color='#3d3d3d',
                                    command=lambda: open_create_template_dialog())

        # Add widgets
        custom_size_btn.pack(pady=5, side='left')
        letter_size_btn.pack(pady=5, side='left')
        post_card_size_btn.pack(pady=5, side='left')
        phone_size_btn.pack(pady=5, side='left')
        tablet_size_btn.pack(pady=5, side='left')
        webview_size_btn.pack(pady=5, side='left')
        
    def launch_project(self):
        win = QApplication([])
        self.app = MPRUN()
        self.app.show()
        self.set_attr()

        with open('main_style.css', 'r') as file:
            self.app.setStyleSheet(file.read())

        sys.exit(win.exec_())

    def set_attr(self):
        selected_template = self.template_combo.get()
        selected_value = self.values[selected_template]
        self.app.set_template(selected_value)

class CreateTemplateDialog(CTk):
    def __init__(self):
        super().__init__()

        self.title('Create Template')
        self.iconbitmap(resource_path('logos and icons/MPRUN_icon.ico'))
        self.geometry('220x500+200+200')
        self.resizable(False, False)

        self.checks = tk.IntVar(value=0)

        self.create_ui()

    def create_ui(self):
        # Labels
        welcome_label = CTkLabel(self, text='Template Attributes', font=('Arial', 20))
        width_label = CTkLabel(self, text='Width')
        height_label = CTkLabel(self, text='Height')
        default_text_label = CTkLabel(self, text='Default Text')
        gsnap_grid_size_label = CTkLabel(self, text='GSNAP Grid Size')

        # Checkboxes
        self.check1 = CTkCheckBox(self, checkbox_width=15, checkbox_height=15, text='', textvariable=self.checks)

        # Entries
        self.x_size_entry = CTkEntry(self, placeholder_text='X width (in px)', width=200)
        self.y_size_entry = CTkEntry(self, placeholder_text='Y width (in px)', width=200)
        self.default_text_entry = CTkTextbox(self, width=180, height=50)
        self.grid_size_entry = CTkEntry(self, placeholder_text='Grid size (in px)', width=200)

        create_project_btn = CTkButton(self, text='Create Project', text_color='white', fg_color='#525252', hover_color='gray', command=self.create_project)

        # Place widgets
        welcome_label.place(x=10, y=5)
        width_label.place(x=10, y=40)
        self.x_size_entry.place(x=10, y=65)
        height_label.place(x=10, y=100)
        self.y_size_entry.place(x=10, y=125)
        self.check1.place(x=10, y=170)
        self.default_text_entry.place(x=30, y=170)
        gsnap_grid_size_label.place(x=10, y=230)
        self.grid_size_entry.place(x=10, y=255)

        create_project_btn.place(x=10, y=400)

        # Insert default values
        self.x_size_entry.insert('end', '1920')
        self.y_size_entry.insert('end', '1080')
        self.default_text_entry.insert('0.0', 'Default text on canvas')
        self.grid_size_entry.insert('end', '10')

    def create_project(self):
        win = QApplication([])
        self.app = MPRUN()
        self.app.show()
        self.set_attr()
        self.destroy()

        with open('main_style.css', 'r') as file:
            self.app.setStyleSheet(file.read())

        sys.exit(win.exec_())

    def set_attr(self):
        if self.check1.get() == 1:
            self.app.custom_template(int(self.x_size_entry.get()), int(self.y_size_entry.get()), self.default_text_entry.get('0.0', 'end-1c'), int(self.grid_size_entry.get()))

        else:
            self.app.custom_template(int(self.x_size_entry.get()), int(self.y_size_entry.get()), '', int(self.grid_size_entry.get()))


if __name__ == '__main__':
    app = Dialog()
    app.mainloop()
